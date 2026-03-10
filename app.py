"""
EduGen - AI-Powered Curriculum Generator

Flask application with dual LLM inference (Groq primary, Ollama fallback),
MongoDB persistence, and PDF export capabilities.
"""

from flask import Flask, render_template, request, jsonify, send_file, session, g, redirect, url_for
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
import json
import os
import secrets
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo.errors import DuplicateKeyError

# Load .env file (API keys)
load_dotenv()

# Import custom modules
from groq_client import GroqClient
from ollama_client import OllamaClient
from prompt_templates import build_structure_prompt, build_subject_detail_prompt, build_chat_prompt
from curriculum_engine import CurriculumEngine
from pdf_generator import PDFGenerator
from database import init_db
from models import User, Profile, Curriculum, ChatHistory

# Absolute base path for reliable file resolution across environments.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

def get_flask_secret_key() -> str:
    """Return a valid Flask secret key and enforce secure production behavior."""
    secret_key = (os.environ.get('FLASK_SECRET_KEY') or '').strip()
    flask_env = os.environ.get('FLASK_ENV', 'development').lower()
    force_https = os.environ.get('FORCE_HTTPS', 'false').lower() == 'true'
    is_production = flask_env == 'production' or force_https

    if secret_key:
        if len(secret_key) < 32:
            message = "FLASK_SECRET_KEY must be at least 32 characters for secure sessions."
            if is_production:
                raise RuntimeError(message)
            print(f"⚠️  WARNING: {message}")
        return secret_key

    if is_production:
        raise RuntimeError(
            "FLASK_SECRET_KEY is required in production. "
            "Set it in environment variables or .env."
        )

    # Development fallback keeps local setup easy while avoiding a hardcoded insecure key.
    print("⚠️  WARNING: No FLASK_SECRET_KEY set. Using temporary development key.")
    print("   Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\"")
    print("   Then add to .env file: FLASK_SECRET_KEY=<generated_key>")
    return secrets.token_hex(32)


app.secret_key = get_flask_secret_key()

CORS(app)
init_db(app)

# Phase 2: Rate Limiting (prevent abuse)
RATE_LIMIT_STORAGE_URI = os.environ.get('RATE_LIMIT_STORAGE_URI', 'memory://')
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri=RATE_LIMIT_STORAGE_URI
)

# Phase 2: HTTPS Enforcement (production only)
@app.before_request
def enforce_https():
    """Redirect HTTP to HTTPS in production."""
    if os.environ.get('FORCE_HTTPS', 'false').lower() == 'true':
        if not request.is_secure and request.headers.get('X-Forwarded-Proto', 'http') != 'https':
            url = request.url.replace('http://', 'https://', 1)
            return redirect(url, code=301)

# Initialize components
# PRIORITY: Groq (fast cloud, FREE) -> Ollama (local fallback)
groq_client = GroqClient()  # 1-3 seconds, FREE
ollama_client = OllamaClient(model="qwen2.5:1.5b")  # Fallback if no internet/API key
curriculum_engine = CurriculumEngine()
pdf_generator = PDFGenerator()

# Thread-safe caching using Flask's g (request-scoped) and session (user-scoped)
# Removed global subject_cache and current_structure to prevent race conditions

def get_subject_cache():
    """Get thread-safe subject cache for current request."""
    if 'subject_cache' not in g:
        g.subject_cache = {}
    return g.subject_cache

def get_current_structure():
    """Get current curriculum structure from user session."""
    return session.get('current_structure', {})

def set_current_structure(structure):
    """Set current curriculum structure in user session."""
    session['current_structure'] = structure

def clear_current_structure():
    """Clear current curriculum structure from session."""
    session.pop('current_structure', None)


@app.context_processor
def inject_auth_context():
    """Inject lightweight auth context for templates."""
    user_id = session.get('user_id')
    username = session.get('username')
    current_user = None
    if user_id and username:
        current_user = {"id": user_id, "username": username}
    return {"current_user": current_user}


def get_user_identifier():
    """Get a stable anonymous identifier for per-user data partitioning."""
    if 'user_id' in session:
        return f"user:{session['user_id']}"

    if 'user_identifier' not in session:
        session['user_identifier'] = os.urandom(16).hex()
    return session['user_identifier']


def _get_safe_next_url(default='/'):
    """Return safe local redirect target from request args/form."""
    next_url = request.args.get('next') or request.form.get('next') or default
    if not next_url.startswith('/'):
        return default
    return next_url


def smart_generate(prompt: str, options: dict = None, json_mode: bool = True) -> Dict[str, Any]:
    """
    Smart generation: tries Groq first, falls back to Ollama.
    Returns dict with 'response', 'generation_time', 'model', 'success'.
    """
    # Try Groq first (fast cloud)
    if groq_client.is_available():
        print(f"⚡ Using Groq ({groq_client.model})...")
        result = groq_client.generate(prompt, options, json_mode=json_mode)
        if result['success']:
            print(f"✅ Groq responded in {result['generation_time']}s")
            return result
        else:
            print(f"⚠️ Groq failed: {result.get('error')}. Falling back to Ollama...")
    else:
        print("⚠️ No GROQ_API_KEY set. Using Ollama (local)...")
    
    # Fallback to Ollama
    print(f"🔄 Using Ollama ({ollama_client.model})...")
    result = ollama_client.generate(prompt, options)
    return result

# ═══════════════════════════════════════════════════════════════════════════
# ROUTES - Frontend Integration
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Serve login as landing page; show app only for authenticated users."""
    if not session.get('user_id'):
        return redirect(url_for('login'))

    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Simple registration page for email/password accounts."""
    if request.method == 'GET':
        return render_template('register.html', error=None)

    try:
        username = (request.form.get('username') or '').strip()
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''
        confirm_password = request.form.get('confirm_password') or ''

        if not username or not email or not password:
            return render_template('register.html', error='All fields are required.'), 400

        if '@' not in email:
            return render_template('register.html', error='Please enter a valid email address.'), 400

        if len(password) < 8:
            return render_template('register.html', error='Password must be at least 8 characters.'), 400

        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.'), 400

        if User.get_by_email(email):
            return render_template('register.html', error='An account with this email already exists.'), 409

        user = User.create(username=username, email=email, password_hash=generate_password_hash(password))

        session['user_id'] = str(user['_id'])
        session['username'] = user['username']
        session.pop('user_identifier', None)

        return redirect(_get_safe_next_url('/'))
    except DuplicateKeyError:
        return render_template('register.html', error='An account with this email already exists.'), 409
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return render_template('register.html', error='Registration failed. Please try again.'), 500


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple login page for email/password accounts."""
    if request.method == 'GET':
        return render_template('login.html', error=None)

    try:
        email = (request.form.get('email') or '').strip().lower()
        password = request.form.get('password') or ''

        if not email or not password:
            return render_template('login.html', error='Email and password are required.'), 400

        user = User.get_by_email(email)
        if not user:
            return render_template('login.html', error='Invalid email or password.'), 401

        stored_hash = user.get('password_hash')
        if not stored_hash or not check_password_hash(stored_hash, password):
            return render_template('login.html', error='Invalid email or password.'), 401

        session['user_id'] = str(user['_id'])
        session['username'] = user.get('username', 'User')
        session.pop('user_identifier', None)

        return redirect(_get_safe_next_url('/'))
    except Exception as e:
        print(f"❌ Login error: {e}")
        return render_template('login.html', error='Login failed. Please try again.'), 500


@app.route('/logout', methods=['POST'])
def logout():
    """Log out current user and return to home page."""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('current_structure', None)
    session.pop('user_identifier', None)
    return redirect('/')


@app.route('/generate_structure', methods=['POST'])
@limiter.limit("10 per minute")
def generate_structure():
    """
    Generate curriculum structure (optimized for speed).
    
    Expected form data:
    - program: Subject/skill name
    - semesters: Number of semesters
    - level: Education level
    - (optional) industry_focus
    """
    try:
        # Extract form data
        program = request.form.get('program')
        
        # Validate integer inputs
        try:
            semesters = int(request.form.get('semesters', 4))
            if semesters < 1 or semesters > 12:
                return render_template('result.html', 
                                     error="Semesters must be between 1 and 12", 
                                     nav_data=None)
        except ValueError:
            return render_template('result.html', 
                                 error="Invalid semester value. Please enter a number.", 
                                 nav_data=None)
        
        try:
            courses_per_sem = int(request.form.get('courses_per_sem', 3))
            if courses_per_sem < 1 or courses_per_sem > 10:
                return render_template('result.html', 
                                     error="Courses per semester must be between 1 and 10", 
                                     nav_data=None)
        except ValueError:
            return render_template('result.html', 
                                 error="Invalid courses per semester value. Please enter a number.", 
                                 nav_data=None)
        
        level = request.form.get('level', 'Undergraduate')
        hours = request.form.get('hours', '20-25')  # Optional field
        industry = request.form.get('industry_focus', '')  # Optional
        
        # Advanced settings from customization panel
        custom_settings_raw = request.form.get('custom_settings', '{}')
        try:
            custom_settings = json.loads(custom_settings_raw)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse custom_settings: {e}")
            custom_settings = {}
            
        if not program:
            return render_template('result.html', 
                                 error="Program name is required", 
                                 nav_data=None)
        
        # Clear cache for new generation (thread-safe)
        clear_current_structure()
        # subject_cache is automatically request-scoped via g
        
        # Pre-calculate structure
        structure_info = curriculum_engine.calculate_structure(semesters, hours, courses_per_sem)
        
        print(f"⚡ Generating curriculum for: {program}")
        print(f"📊 Structure: {structure_info}")
        
        # Build optimized prompt
        prompt = build_structure_prompt(
            skill=program,
            level=level,
            semesters=semesters,
            hours=hours,
            industry=industry,
            courses_per_sem=courses_per_sem,
            custom_settings=custom_settings
        )
        
        # Generate with smart fallback (Groq -> Ollama)
        start_time = time.time()
        result = smart_generate(prompt)
        print(f"📊 Result: success={result.get('success')}, time={result.get('generation_time')}s")
        
        if not result['success']:
            print(f"❌ Generation failed: {result.get('error')}")
            return render_template('result.html',
                                 error=f"Generation failed: {result.get('error', 'Unknown error')}",
                                 nav_data=None)
        
        # Parse AI response
        curriculum_data = curriculum_engine.parse_ai_response(result['response'])
        
        if not curriculum_data:
            return render_template('result.html',
                                 error="Failed to parse AI response. Please try again.",
                                 nav_data=None)
        
        # Validate structure
        if not curriculum_engine.validate_curriculum(curriculum_data):
            # Try to fix common issues
            curriculum_data = curriculum_engine.ensure_minimum_quality(curriculum_data)
        
        # Store in session for PDF export.
        set_current_structure(curriculum_data)

        # Persist curriculum for history tracking.
        Curriculum.create(
            user_identifier=get_user_identifier(),
            program=program,
            level=level,
            semesters=semesters,
            hours=hours,
            industry=industry,
            courses_per_sem=courses_per_sem,
            custom_settings=custom_settings,
            curriculum_data=curriculum_data,
            model=result.get('model'),
            generation_time=result.get('generation_time')
        )
        
        elapsed = time.time() - start_time
        print(f"✅ Generation completed in {elapsed:.2f}s")
        
        return render_template('result.html', nav_data=curriculum_data)
        
    except Exception as e:
        print(f"❌ Error in generate_structure: {str(e)}")
        return render_template('result.html',
                             error=f"An error occurred: {str(e)}",
                             nav_data=None)


@app.route('/generate_subject_details', methods=['POST'])
@limiter.limit("20 per minute")
def generate_subject_details():
    """
    Generate detailed syllabus for a subject (with caching).
    
    Expected JSON:
    - subject: Subject name
    - program: Program name
    """
    try:
        data = request.get_json()
        subject = data.get('subject')
        program = data.get('program')
        
        if not subject or not program:
            return jsonify({"error": "Missing subject or program"}), 400
        
        # Check cache (thread-safe request-scoped cache)
        cache = get_subject_cache()
        cache_key = f"{program}_{subject}"
        print(f"🔍 Checking cache for: {cache_key}")
        print(f"📦 Cache keys: {list(cache.keys())}")
        
        if cache_key in cache:
            print(f"✅ Cache HIT for: {subject}")
            return jsonify({
                "content": cache[cache_key],
                "cached": True
            })
        
        print(f"⚡ Cache MISS for: {subject}. Generating...")
        
        # Build optimized prompt
        prompt = build_subject_detail_prompt(subject, program)
        
        # Generate with smart fallback (Groq -> Ollama) — Markdown mode for syllabus
        # Increased token limits to prevent abrupt cutoffs
        result = smart_generate(
            prompt,
            options={'max_tokens': 2048, 'num_predict': 2048},
            json_mode=False
        )
        
        if not result['success']:
            return jsonify({"error": result.get('error', 'Generation failed')}), 500
        
        content = result['response']
        
        # Cache the result (thread-safe request-scoped cache)
        cache = get_subject_cache()
        cache[cache_key] = content
        
        print(f"✅ Generated in {result['generation_time']}s")
        
        return jsonify({
            "content": content,
            "cached": False,
            "generation_time": result['generation_time']
        })
        
    except Exception as e:
        print(f"❌ Error in generate_subject_details: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/download_pdf')
def download_pdf():
    """
    Generate and download PDF of current curriculum.
    Target: <2 seconds generation time
    """
    try:
        # Get structure from session (thread-safe)
        structure = get_current_structure()
        
        if not structure:
            return "No curriculum found. Please generate one first.", 400
        
        print("📄 Generating PDF...")
        start_time = time.time()
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_pdf(structure)
        
        elapsed = time.time() - start_time
        print(f"✅ PDF generated in {elapsed:.2f}s")
        
        program_name = structure.get('program', 'curriculum')
        filename = f"{program_name.replace(' ', '_')}_curriculum.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ Error in download_pdf: {str(e)}")
        return f"PDF generation failed: {str(e)}", 500


@app.route('/download_course_pdf', methods=['POST'])
def download_course_pdf():
    """
    Generate and download PDF for individual course syllabus.
    """
    try:
        data = request.get_json()
        subject = data.get('subject')
        content = data.get('content')
        
        if not subject or not content:
            return jsonify({"error": "Missing subject or content"}), 400
        
        print(f"📄 Generating course PDF for: {subject}")
        start_time = time.time()
        
        # Generate PDF for single course
        pdf_buffer = pdf_generator.generate_course_pdf(subject, content)
        
        elapsed = time.time() - start_time
        print(f"✅ Course PDF generated in {elapsed:.2f}s")
        
        filename = f"{subject.replace(' ', '_')}_syllabus.pdf"
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        print(f"❌ Error in download_course_pdf: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ═══════════════════════════════════════════════════════════════════════════
# PROFILE MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/get_profiles')
def get_profiles():
    """Get list of saved profile names."""
    try:
        names = Profile.list_names(get_user_identifier())
        return jsonify({"success": True, "profiles": names})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/save_profile', methods=['POST'])
def save_profile():
    """Save a curriculum generation profile."""
    try:
        data = request.get_json()
        profile_name = data.get('profile_name')
        settings = data.get('settings')
        
        if not profile_name or not settings:
            return jsonify({"success": False, "error": "Missing profile name or settings"}), 400
            
        Profile.upsert(get_user_identifier(), profile_name, settings)
        
        return jsonify({"success": True, "message": f'Profile "{profile_name}" saved successfully'})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/load_profile/<name>')
def load_profile(name):
    """Load a specific profile."""
    profile = Profile.get(get_user_identifier(), name)
    if profile:
        return jsonify({"success": True, "settings": profile.get('settings', {})})
    return jsonify({"success": False, "error": f'Profile "{name}" not found'}), 404

@app.route('/delete_profile/<name>', methods=['DELETE'])
def delete_profile(name):
    """Delete a saved profile."""
    if Profile.delete(get_user_identifier(), name):
        return jsonify({"success": True, "message": f'Profile "{name}" deleted'})
    return jsonify({"success": False, "error": "Profile not found"}), 404


# ═══════════════════════════════════════════════════════════════════════════
# API ENDPOINTS - For programmatic access
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/generate-curriculum', methods=['POST'])
@limiter.limit("10 per minute")
def api_generate_curriculum():
    """
    API endpoint for curriculum generation.
    
    Expected JSON:
    {
        "skill": "Machine Learning",
        "education_level": "Masters",
        "num_semesters": 4,
        "weekly_hours": "20-25",
        "industry_focus": "AI"
    }
    
    Returns:
    {
        "status": "success",
        "curriculum": {...},
        "generation_time": 12.3
    }
    """
    try:
        data = request.get_json()
        
        skill = data.get('skill')
        level = data.get('education_level', 'Undergraduate')
        semesters = int(data.get('num_semesters', 4))
        hours = data.get('weekly_hours', '20-25')
        industry = data.get('industry_focus', '')
        
        if not skill:
            return jsonify({
                "status": "error",
                "message": "Skill/subject is required"
            }), 400
        
        # Generate curriculum
        start_time = time.time()
        
        prompt = build_structure_prompt(skill, level, semesters, hours, industry)
        result = smart_generate(prompt)
        
        if not result['success']:
            return jsonify({
                "status": "error",
                "message": result.get('error', 'Generation failed')
            }), 500
        
        curriculum_data = curriculum_engine.parse_ai_response(result['response'])
        
        if not curriculum_data:
            return jsonify({
                "status": "error",
                "message": "Failed to parse curriculum"
            }), 500
        
        curriculum_data = curriculum_engine.ensure_minimum_quality(curriculum_data)

        Curriculum.create(
            user_identifier=get_user_identifier(),
            program=skill,
            level=level,
            semesters=semesters,
            hours=hours,
            industry=industry,
            courses_per_sem=3,
            custom_settings={},
            curriculum_data=curriculum_data,
            model=result.get('model'),
            generation_time=result.get('generation_time')
        )
        
        elapsed = time.time() - start_time
        
        return jsonify({
            "status": "success",
            "curriculum": curriculum_data,
            "generation_time": round(elapsed, 2)
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/curriculum_history')
def curriculum_history():
    """Return curriculum generation history for current user."""
    try:
        limit = request.args.get('limit', 20, type=int)
        limit = min(max(limit, 1), 100)
        history = Curriculum.list_history(get_user_identifier(), limit=limit)

        for item in history:
            if isinstance(item.get('created_at'), datetime):
                item['created_at'] = item['created_at'].isoformat() + 'Z'

        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/curriculum_history/<curriculum_id>')
def curriculum_history_item(curriculum_id):
    """Return a single stored curriculum by id for current user."""
    try:
        item = Curriculum.get_by_id(curriculum_id, get_user_identifier())
        if not item:
            return jsonify({"success": False, "error": "Curriculum not found"}), 404

        if isinstance(item.get('created_at'), datetime):
            item['created_at'] = item['created_at'].isoformat() + 'Z'

        return jsonify({"success": True, "curriculum": item})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/curriculum_history/<curriculum_id>/view')
def view_saved_curriculum(curriculum_id):
    """Render a previously saved curriculum in result.html."""
    try:
        item = Curriculum.get_by_id(curriculum_id, get_user_identifier())
        if not item:
            return render_template('result.html', error="Curriculum not found.", nav_data=None)
        curriculum_data = item.get('curriculum_data')
        if curriculum_data:
            set_current_structure(curriculum_data)
        return render_template('result.html', nav_data=curriculum_data)
    except Exception as e:
        return render_template('result.html', error=f"Error loading curriculum: {str(e)}", nav_data=None)


@app.route('/curriculum_history/<curriculum_id>', methods=['DELETE'])
def delete_curriculum_history_item(curriculum_id):
    """Delete a single curriculum from history."""
    try:
        result = Curriculum.delete_by_id(curriculum_id, get_user_identifier())
        if result:
            return jsonify({"success": True})
        return jsonify({"success": False, "error": "Curriculum not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route('/health')
def health_check():
    """Health check endpoint."""
    groq_health = groq_client.health_check() if groq_client.is_available() else {'connected': False, 'status': 'no_api_key'}
    ollama_health = ollama_client.health_check()
    
    healthy = groq_health.get('connected', False) or ollama_health.get('ollama_connected', False)
    
    return jsonify({
        'status': 'healthy' if healthy else 'unhealthy',
        'groq': groq_health,
        'ollama': ollama_health,
        'active_engine': 'groq' if groq_client.is_available() else 'ollama'
    }), 200 if healthy else 503


@app.route('/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    """AI-powered chatbot for curriculum assistance."""
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        context = data.get('context', {})
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
            
        # Build chat prompt with context
        prompt = build_chat_prompt(message, context)
        
        # Get response from AI using smart_generate with increased timeout for chat
        result = smart_generate(prompt, options={'max_tokens': 1024}, json_mode=False)
        
        if result['success']:
            ChatHistory.create(
                user_identifier=get_user_identifier(),
                message=message,
                response=result['response'].strip(),
                context=context,
                model=result.get('model'),
                generation_time=result.get('generation_time'),
                success=True
            )
            return jsonify({
                'response': result['response'].strip(),
                'timestamp': datetime.now().isoformat(),
                'model': result['model'],
                'generation_time': result['generation_time']
            })
        else:
            # Provide detailed error message
            error_msg = result.get('error', 'Unknown error occurred')
            print(f"❌ Chat generation failed: {error_msg}")
            ChatHistory.create(
                user_identifier=get_user_identifier(),
                message=message,
                response="I'm having trouble connecting to the AI service right now. Please try again in a moment.",
                context=context,
                model=result.get('model'),
                generation_time=result.get('generation_time'),
                success=False,
                error_details=error_msg
            )
            
            # Return a user-friendly error with the actual error for debugging
            return jsonify({
                'error': 'AI service is temporarily unavailable',
                'details': error_msg,
                'response': "I'm having trouble connecting to the AI service right now. Please try again in a moment."
            }), 503
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        try:
            data = request.get_json(silent=True) or {}
            ChatHistory.create(
                user_identifier=get_user_identifier(),
                message=(data.get('message', '') or '').strip(),
                response='Failed to process chat message',
                context=data.get('context', {}),
                success=False,
                error_details=str(e)
            )
        except Exception:
            pass
        return jsonify({
            'error': 'Failed to process chat message',
            'details': str(e)
        }), 500


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    print("=" * 80)
    print("🚀 GenAI Curriculum Generator")
    print("=" * 80)
    print(f"🎯 Target Latency: <5 seconds (Groq) | <60s (Ollama fallback)")
    print(f"🌐 Server: http://127.0.0.1:5000")
    print("=" * 80)
    
    # Check Groq (primary)
    if groq_client.is_available():
        print(f"✅ Groq API key configured")
        print(f"⚡ Primary engine: Groq ({groq_client.model}) — ~1-3s responses")
    else:
        print("⚠️  No GROQ_API_KEY set!")
        print("   Get free key: https://console.groq.com")
        print("   Then: set GROQ_API_KEY=gsk_your_key_here")
    
    # Check Ollama (fallback)
    health = ollama_client.health_check()
    if health['ollama_connected']:
        print(f"✅ Ollama connected (fallback: {ollama_client.model})")
        if not groq_client.is_available():
            # Only warm up Ollama if it's the primary engine
            if health['model_available']:
                ollama_client.warm_up()
            else:
                print(f"   ⚠️ Model '{ollama_client.model}' not found. Run: ollama pull {ollama_client.model}")
    else:
        if not groq_client.is_available():
            print("❌ No AI engine available!")
            print("   Option 1: Set GROQ_API_KEY (recommended, free)")
            print("   Option 2: Start Ollama with: ollama serve")
    
    print("=" * 80)
    
    app.run(debug=True, port=5000, threaded=True)
