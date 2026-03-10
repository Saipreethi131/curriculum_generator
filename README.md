# EduGen — AI-Powered Curriculum Generator

A full-stack web application that automates academic curriculum design using large language models. Given a subject, education level, and program duration, EduGen generates structured, semester-wise curricula complete with course syllabi, industry certifications, and capstone projects.

## Architecture

```
Client (HTML/CSS/JS)
    |
Flask Application (app.py)
    |
    +-- Groq Cloud API (primary -- llama-3.1-8b-instant)
    +-- Ollama (local fallback -- qwen2.5:1.5b)
    |
    +-- Curriculum Engine (structure calculation, JSON validation)
    +-- Prompt Templates (structured output generation)
    +-- PDF Generator (ReportLab)
    +-- MongoDB (users, profiles, curricula, chat history)
```

The system uses a dual-engine inference architecture: Groq's LPU hardware serves as the primary inference backend (~1-3s response times), with Ollama providing offline fallback capability. Both engines implement a uniform response contract, allowing seamless failover.

## Features

- **Curriculum Generation** — Configure subject, level (UG/PG/Diploma), semesters (1-12), courses per semester, and weekly hours. Advanced options include academic system type, difficulty progression, learning style, and certification/project focus.
- **Detailed Syllabi** — On-demand generation of 5-unit syllabi with course objectives, lab activities, a 16-week schedule, recommended reading, industry certifications, and capstone projects.
- **Context-Aware Chatbot** — Conversational assistant that dynamically incorporates the current program context into LLM prompts, with Markdown-rendered responses and persistent chat history.
- **Dual View Modes** — Table view for traditional academic presentation and a visual skill-path roadmap with animated progression indicators.
- **PDF Export** — Full curriculum and individual course syllabus exports via ReportLab, generated in-memory with sub-2s latency.
- **Profile Management** — Save, load, and reuse named generation profiles across sessions.
- **User Authentication** — Email/password registration with bcrypt hashing, session management, and anonymous guest support with data partitioning.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python, Flask |
| Database | MongoDB (pymongo) |
| Primary LLM | Groq Cloud API (llama-3.1-8b-instant) |
| Fallback LLM | Ollama (qwen2.5:1.5b) |
| PDF Generation | ReportLab |
| Frontend | HTML5, CSS3, vanilla JavaScript |
| Security | Werkzeug password hashing, Flask-Limiter, CORS, input sanitization |

## Setup

### Prerequisites

- Python 3.8+
- MongoDB instance (local or Atlas)
- Groq API key ([console.groq.com](https://console.groq.com), free tier available)
- (Optional) Ollama for local inference fallback

### Installation

```bash
git clone https://github.com/Saipreethi131/curriculum_generator.git
cd curriculum_generator
pip install -r requirements.txt
```

### Configuration

Copy the environment template and add your credentials:

```bash
cp .env.example .env
```

Required variables in `.env`:

```
GROQ_API_KEY=<your_groq_api_key>
FLASK_SECRET_KEY=<random_secret_min_32_chars>
MONGO_URI=mongodb://localhost:27017/curriculum_generator
```

Generate a secure secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Running

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`.

To enable the Ollama fallback:

```bash
ollama pull qwen2.5:1.5b
ollama serve
```

## Project Structure

```
curriculum_generator/
├── app.py                  # Flask application and route handlers
├── groq_client.py          # Groq Cloud API client
├── ollama_client.py        # Ollama local inference client
├── curriculum_engine.py    # Structure calculation and response validation
├── prompt_templates.py     # LLM prompt construction
├── pdf_generator.py        # ReportLab PDF generation
├── database.py             # MongoDB connection and initialization
├── models/
│   ├── user.py             # User authentication model
│   ├── profile.py          # Generation profile model
│   ├── curriculum.py       # Curriculum storage model
│   └── chat_history.py     # Chat persistence model
├── templates/
│   ├── index.html          # Main application page
│   ├── result.html         # Curriculum display page
│   ├── login.html          # Login page
│   └── register.html       # Registration page
├── static/
│   ├── css/style.css
│   └── js/script.js
├── requirements.txt
└── .env.example
```

## API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/generate_structure` | Generate full curriculum |
| POST | `/generate_subject_details` | Generate detailed course syllabus |
| POST | `/chat` | Chatbot interaction |
| POST | `/api/generate-curriculum` | REST API for programmatic access |
| GET | `/curriculum_history` | List saved curricula |
| GET | `/download_pdf` | Export curriculum as PDF |
| GET | `/health` | Service health check |

## License

MIT
