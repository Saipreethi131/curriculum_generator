# 🎓 EduGen - AI-Powered Curriculum Generator

> **Transform learning goals into complete, industry-aligned academic curricula in under 30 seconds**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/Groq-API-orange.svg)](https://groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 **Overview**

**EduGen** is an AI-powered web application that automates complete curriculum design for academic institutions, coding bootcamps, and corporate training programs. What traditionally takes educators 2-3 weeks now takes **less than 30 seconds**.

### **Key Features**
✅ **Lightning-Fast Generation** - Complete curricula in <30 seconds using Groq's LPU infrastructure  
✅ **Industry Certifications** - Auto-suggests relevant AWS, Google, Microsoft certifications  
✅ **Project-Based Learning** - 3-4 capstone project ideas per course  
✅ **Flexible Programs** - Generate 1-8 semester curricula with varied credit allocations  
✅ **Professional PDFs** - Export full curriculum or individual course syllabi  
✅ **Modern UI** - Navy blue theme with metrics dashboard and smooth animations

---

## 📸 **Screenshots**

### Homepage with Metrics Dashboard
Professional landing page showcasing key metrics: <30s generation time, 1-8 semester range, 100% project-based learning.

### Generated Curriculum
Semester-wise course cards with credit hours, weekly hours, and interactive course details.

### Course Syllabus
Detailed syllabi with 5 units, industry certifications, capstone projects, and reading recommendations.

---

## 🛠️ **Tech Stack**

### **Backend**
- **Python 3.8+** - Core application language
- **Flask 3.0+** - Web framework
- **Groq Cloud API** - Primary LLM inference (llama-3.1-8b-instant)
- **Ollama** - Local fallback inference engine (qwen2.5:1.5b)
- **ReportLab** - Professional PDF generation

### **AI/LLM**
- **Groq LPU Hardware** - 500+ tokens/sec throughput
- **llama-3.1-8b-instant** - Primary model via Groq API
- **Temperature: 0.1** - Deterministic, consistent output
- **JSON Mode** - Structured curriculum generation

### **Frontend**
- **HTML5/CSS3** - Semantic markup, responsive design
- **Vanilla JavaScript** - No framework overhead
- **Phosphor Icons** - Modern icon library
- **Marked.js** - Markdown rendering for syllabi

---

## 🎯 **Features in Detail**

### **1. Intelligent Curriculum Generation**
- **Varied Credits**: 3 credits for foundational courses, 4 for advanced
- **Progressive Difficulty**: Courses build on previous semesters
- **Realistic Course Codes**: Auto-generated unique identifiers
- **Smart Credit Distribution**: Balanced workload across semesters

### **2. Industry Certification Mapping**
Each course includes 2-3 relevant certifications:
- AWS Certified Solutions Architect
- Google Cloud Professional
- Microsoft Azure Administrator
- CompTIA Security+, Network+
- Oracle Certified Professional
- Cisco CCNA, CCNP

### **3. Capstone Project Ideas**
3-4 practical projects per course with:
- Real-world applications
- Technology stack specifications
- Hands-on learning outcomes

### **4. Comprehensive Syllabi**
- **5 Units** with 2-3 week allocations
- **Course Objectives** aligned with outcomes
- **Course Modules** with topics and lab activities
- **Recommended Reading** (books + online resources)
- **16-Week Schedule** with unit-to-week mapping
- **Assessment Structure** (assignments, exams, projects)

### **5. Professional PDF Export**
- **Full Curriculum PDF**: All semesters and courses
- **Course-Wise PDF**: Individual syllabi with one click
- **Clean Formatting**: Proper headers, spacing, tables
- **Print-Ready**: A4 format with margins

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.8 or higher
- pip (Python package manager)
- Groq API key ([Get free at console.groq.com](https://console.groq.com))
- (Optional) Ollama for offline fallback

### **1. Clone Repository**
```bash
git clone https://github.com/Saipreethi131/curriculum_generator.git
cd curriculum_generator
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Set Up Groq API Key**

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your_api_key_here"
```

**Mac/Linux:**
```bash
export GROQ_API_KEY="your_api_key_here"
```

**Or create `.env` file:**
```
GROQ_API_KEY=your_api_key_here
```

### **4. (Optional) Install Ollama Fallback**
```bash
# Download from https://ollama.ai
ollama pull qwen2.5:1.5b
ollama serve
```

---

## 🚀 **Usage**

### **Start Server**
```bash
python app.py
```

Server starts at: **http://127.0.0.1:5000**

### **Generate Curriculum**
1. Enter skill/program name (e.g., "Computer Science Engineering")
2. Provide brief description
3. Select education level (UG/PG/Diploma)
4. Choose number of semesters (1-8)
5. Set weekly hours (20-50)
6. Click **"Generate Curriculum"**

### **View Course Details**
- Click any course card to view detailed syllabus
- See industry certifications, project ideas, reading materials
- Download individual course PDF

### **Export Full Curriculum**
- Click **"Download Full Curriculum PDF"** button
- Get complete program with all courses and syllabi

---

## 📊 **Performance**

| Metric | Value | Implementation |
|--------|-------|----------------|
| **Generation Time** | <30s | Groq LPU hardware (500+ tokens/sec) |
| **Token Throughput** | 500+ tok/s | llama-3.1-8b-instant via Groq |
| **Accuracy** | 95%+ | Temperature 0.1, structured prompts |
| **Concurrent Users** | 10+ | Flask with efficient caching |
| **PDF Generation** | <2s | ReportLab optimization |
| **API Cost** | FREE | Groq free tier |

---

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)                  │
│  ┌─────────────┐  ┌─────────────┐             │
│  │   Metrics   │  │   Course    │             │
│  │  Dashboard  │  │   Cards     │             │
│  └─────────────┘  └─────────────┘             │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│          Flask Backend (app.py)                 │
│  ┌─────────────────┐  ┌──────────────────────┐ │
│  │ Route Handlers  │  │  Session Management  │ │
│  └─────────────────┘  └──────────────────────┘ │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌───────────────────┐  ┌───────────────────┐
│   Groq Client     │  │  Ollama Client    │
│  (Primary - Fast) │  │   (Fallback)      │
│llama-3.1-8b-instant│ │ qwen2.5:1.5b      │
│   1-3s response   │  │  30-60s response  │
└─────────┬─────────┘  └─────────┬─────────┘
          │                      │
          └──────────┬───────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│         Prompt Templates                        │
│  ┌────────────────┐  ┌────────────────────────┐│
│  │ Curriculum JSON│  │  Syllabus Markdown     ││
│  │  Generation    │  │  with Units & Projects ││
│  └────────────────┘  └────────────────────────┘│
└─────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         PDF Generator (ReportLab)               │
│  • Custom styles  • Markdown parsing           │
│  • Print-ready formatting                       │
└─────────────────────────────────────────────────┘
```

---

## 🎨 **UI/UX Features**

### **Modern Design**
- **Navy Blue Theme** (#0a2654) - Professional, academic aesthetic
- **Gradient Effects** - Smooth color transitions
- **Hover Animations** - Lifted cards with shadows
- **Responsive Layout** - Works on all screen sizes

### **Metrics Dashboard**
Three key metrics displayed prominently:
- ⚡ **<30s** Generation Time
- 🎓 **1-8** Semester Range
- 📚 **100%** Project-Based Learning

### **Interactive Elements**
- **Smooth Scrolling** - Navigate to form from hero
- **Modal Drawers** - Slide-in course details
- **Loading States** - Spinners during generation
- **Toast Notifications** - Success/error feedback

---

## 📁 **Project Structure**

```
curriculum_generator/
├── app.py                      # Main Flask application
├── groq_client.py              # Groq API integration (primary)
├── ollama_client.py            # Ollama fallback integration
├── curriculum_engine.py        # Core curriculum logic
├── prompt_templates.py         # AI prompt engineering
├── pdf_generator.py            # ReportLab PDF creation
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── DEPLOYMENT.md               # Deployment guide
├── benchmark.py                # Performance testing
├── test_speed.py              # Speed benchmarks
├── static/
│   ├── css/
│   │   └── style.css          # Navy blue theme, animations
│   └── js/
│       └── script.js          # Frontend interactivity
└── templates/
    ├── index.html             # Homepage with metrics
    └── result.html            # Curriculum display
```

---

## 🔧 **Configuration**

### **Change Primary Model**
Edit `groq_client.py`:
```python
self.model = "llama-3.1-8b-instant"  # Or llama-3.3-70b-versatile
```

### **Adjust Token Limits**
Edit `app.py`:
```python
max_tokens=2048  # Increase for longer syllabi
```

### **Customize Colors**
Edit `static/css/style.css`:
```css
:root {
    --primary-color: #0a2654;  /* Change navy blue */
    --primary-light: #1e40af;
}
```

---

## 🧪 **Testing**

### **Run Performance Benchmark**
```bash
python benchmark.py
```

### **Test Speed**
```bash
python test_speed.py
```

### **Manual Testing Checklist**
- [ ] Generate 1-semester curriculum
- [ ] Generate 8-semester curriculum
- [ ] Click course to view syllabus
- [ ] Verify certifications appear
- [ ] Verify project ideas appear
- [ ] Download course PDF
- [ ] Download full curriculum PDF
- [ ] Test with different skills/programs

---

## 🐛 **Troubleshooting**

### **Issue: "Groq API Key not found"**
**Solution:**
```bash
export GROQ_API_KEY="your_key_here"
```
Or set in `.env` file

### **Issue: "Ollama connection failed"**
**Solution:**
```bash
ollama serve
ollama pull qwen2.5:1.5b
```

### **Issue: "Generation too slow"**
**Solution:**
- Ensure Groq API key is set (switches to slow Ollama if missing)
- Check internet connection
- Verify Groq API limits not exceeded

### **Issue: "PDF download fails"**
**Solution:**
- Check `pdf_generator.py` for errors
- Ensure ReportLab is installed: `pip install reportlab`

---

## 📈 **Future Enhancements**

- [ ] **LMS Integration** - Direct export to Moodle, Canvas, Blackboard
- [ ] **Multi-language Support** - Generate curricula in different languages
- [ ] **Collaborative Editing** - Multiple educators refine AI output
- [ ] **Version Control** - Track curriculum changes over time
- [ ] **Analytics Dashboard** - Track industry trends
- [ ] **Custom Templates** - User-defined syllabus formats
- [ ] **AI Course Recommendations** - Suggest prerequisites and co-requisites

---

## 🤝 **Contributing**

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👏 **Acknowledgments**

- **Groq** - For lightning-fast LLM inference
- **Meta AI** - For llama-3.1-8b-instant model
- **Ollama** - For local AI model serving
- **ReportLab** - For PDF generation
- **Phosphor Icons** - For beautiful icons

---

## 📞 **Contact**

**Repository:** [github.com/Saipreethi131/curriculum_generator](https://github.com/Saipreethi131/curriculum_generator)

---

**Built with ❤️ for educators and learners worldwide** 🚀

*Automate curriculum design. Focus on teaching.*
