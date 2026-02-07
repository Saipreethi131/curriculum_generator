"""
GenAI Curriculum Generator - Optimized Flask Application
Target Performance: <5 seconds with Groq Cloud API

Architecture:
- Groq (primary) -> Ollama (fallback)
- Performance-optimized for hackathon demos
- Professional PDF generation
- Existing frontend integration
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
import time
import json
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load .env file (API keys)
load_dotenv()

# Import custom modules
from groq_client import GroqClient
from ollama_client import OllamaClient
from prompt_templates import build_structure_prompt, build_subject_detail_prompt
from curriculum_engine import CurriculumEngine
from pdf_generator import PDFGenerator

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize components
# PRIORITY: Groq (fast cloud, FREE) -> Ollama (local fallback)
groq_client = GroqClient()  # 1-3 seconds, FREE
ollama_client = OllamaClient(model="qwen2.5:1.5b")  # Fallback if no internet/API key
curriculum_engine = CurriculumEngine()
pdf_generator = PDFGenerator()

# In-memory cache for generated content
subject_cache = {}
current_structure = {}


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
    """Serve main page (existing frontend)."""
    return render_template('index.html')


@app.route('/generate_structure', methods=['POST'])
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
        semesters = int(request.form.get('semesters', 4))
        level = request.form.get('level', 'Undergraduate')
        hours = request.form.get('hours', '20-25')  # Optional field
        industry = request.form.get('industry_focus', '')  # Optional
        
        if not program:
            return render_template('result.html', 
                                 error="Program name is required", 
                                 nav_data=None)
        
        # Clear cache for new generation
        global subject_cache, current_structure
        subject_cache = {}
        current_structure = {}
        
        # Pre-calculate structure (saves 5-10 seconds vs asking AI)
        structure_info = curriculum_engine.calculate_structure(semesters, hours)
        
        print(f"⚡ Generating curriculum for: {program}")
        print(f"📊 Structure: {structure_info}")
        
        # Build optimized prompt
        prompt = build_structure_prompt(
            skill=program,
            level=level,
            semesters=semesters,
            hours=hours,
            industry=industry
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
        
        # Store globally
        current_structure = curriculum_data
        
        elapsed = time.time() - start_time
        print(f"✅ Generation completed in {elapsed:.2f}s")
        
        return render_template('result.html', nav_data=curriculum_data)
        
    except Exception as e:
        print(f"❌ Error in generate_structure: {str(e)}")
        return render_template('result.html',
                             error=f"An error occurred: {str(e)}",
                             nav_data=None)


@app.route('/generate_subject_details', methods=['POST'])
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
        
        # Check cache
        cache_key = f"{program}_{subject}"
        print(f"🔍 Checking cache for: {cache_key}")
        print(f"📦 Cache keys: {list(subject_cache.keys())}")
        
        if cache_key in subject_cache:
            print(f"✅ Cache HIT for: {subject}")
            return jsonify({
                "content": subject_cache[cache_key],
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
        
        # Cache the result
        subject_cache[cache_key] = content
        
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
        global current_structure
        
        if not current_structure:
            return "No curriculum found. Please generate one first.", 400
        
        print("📄 Generating PDF...")
        start_time = time.time()
        
        # Generate PDF
        pdf_buffer = pdf_generator.generate_pdf(current_structure)
        
        elapsed = time.time() - start_time
        print(f"✅ PDF generated in {elapsed:.2f}s")
        
        program_name = current_structure.get('program', 'curriculum')
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
# API ENDPOINTS - For programmatic access
# ═══════════════════════════════════════════════════════════════════════════

@app.route('/api/generate-curriculum', methods=['POST'])
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
