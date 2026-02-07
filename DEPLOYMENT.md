# GenAI Curriculum Generator - Deployment Guide

## 🎯 Performance Target
**< 20 seconds** on Intel i5 11th Gen, 16GB RAM

## 📋 Prerequisites
- Python 3.8 or higher
- 16GB RAM minimum
- Windows/Linux/macOS

## 🚀 Step-by-Step Deployment

### 1. Install Ollama

**Windows:**
```powershell
# Download from https://ollama.ai/download
# Run installer
```

**Linux/macOS:**
```bash
curl https://ollama.ai/install.sh | sh
```

### 2. Pull Recommended Model

**RECOMMENDED (Best Balance - 8-12s):**
```bash
ollama pull phi3:mini
```

**ALTERNATIVES:**
```bash
# Fastest (5-10s)
ollama pull llama3.2:3b

# Ultra-fast backup (3-7s)
ollama pull gemma2:2b
```

**⚠️ DO NOT USE:**
- `granite3.3:2b` - Too slow (30-60s)
- Any 7B+ models - Will exceed 20s target

### 3. Start Ollama Service

```bash
ollama serve
```

Leave this terminal open. Ollama will run on `http://localhost:11434`

### 4. Setup Python Environment

**Create virtual environment:**
```bash
cd curriculum_generator
python -m venv venv
```

**Activate environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Verify Installation

```bash
python benchmark.py
```

This will:
- Check Ollama connection
- Verify model availability
- Run performance test
- Report generation time

### 7. Start Application

```bash
python app.py
```

You should see:
```
================================================================================
🚀 GenAI Curriculum Generator
================================================================================
📊 Model: phi3:mini
🎯 Target Latency: <20 seconds
🌐 Server: http://127.0.0.1:5000
================================================================================
✅ Ollama connected
✅ Model 'phi3:mini' available
================================================================================
```

### 8. Access Application

Open browser: **http://127.0.0.1:5000**

## 🧪 Testing Performance

### Quick Test
1. Enter "Machine Learning" as skill
2. Select "Masters" level
3. Choose "4 semesters"
4. Click "Generate Curriculum"
5. **Should complete in < 20 seconds**

### Benchmark Test
```bash
python benchmark.py --full
```

This runs multiple test scenarios and reports average latency.

## ⚡ Performance Optimization

### If Generation is Too Slow (>20s):

1. **Switch to faster model:**
   ```bash
   ollama pull llama3.2:3b
   ```
   
   Then edit `app.py` line 25:
   ```python
   ollama_client = OllamaClient(model="llama3.2:3b")
   ```

2. **Reduce token limits** (edit `ollama_client.py`):
   ```python
   'num_predict': 600,  # Reduce from 800
   ```

3. **Close other applications** to free RAM

4. **Check Ollama is using CPU/GPU properly:**
   ```bash
   ollama ps
   ```

## 📊 Expected Performance

| Model | Hardware | Avg Time | Quality |
|-------|----------|----------|---------|
| phi3:mini | i5 11th Gen, 16GB | 8-12s | Excellent |
| llama3.2:3b | i5 11th Gen, 16GB | 5-10s | Very Good |
| gemma2:2b | i5 11th Gen, 16GB | 3-7s | Good |

## 🐛 Troubleshooting

### "Ollama not running"
```bash
# Start Ollama
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull phi3:mini
```

### "Generation timeout"
- Check if Ollama is running
- Try a faster model
- Reduce `num_predict` in `ollama_client.py`

### "Port 5000 already in use"
Edit `app.py` last line:
```python
app.run(debug=True, port=5001, threaded=True)
```

## 📁 Project Structure

```
curriculum_generator/
├── app.py                    # Main Flask application
├── ollama_client.py          # Optimized Ollama client
├── curriculum_engine.py      # Curriculum logic
├── prompt_templates.py       # Speed-optimized prompts
├── pdf_generator.py          # PDF export
├── benchmark.py              # Performance testing
├── requirements.txt          # Dependencies
├── templates/
│   ├── index.html           # Landing page
│   └── result.html          # Results page
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

## 🎓 Usage Examples

### Web Interface
1. Go to http://127.0.0.1:5000
2. Fill in the form
3. Click "Generate Curriculum"
4. View results
5. Download PDF

### API Usage
```bash
curl -X POST http://127.0.0.1:5000/api/generate-curriculum \
  -H "Content-Type: application/json" \
  -d '{
    "skill": "Machine Learning",
    "education_level": "Masters",
    "num_semesters": 4,
    "weekly_hours": "20-25",
    "industry_focus": "AI"
  }'
```

## ✅ Success Criteria

Your deployment is successful if:
- ✅ Generation completes in < 20 seconds
- ✅ Curriculum structure is accurate
- ✅ PDF exports successfully
- ✅ No errors in console
- ✅ Cache works (second click is instant)

## 🔧 Advanced Configuration

### Change Model
Edit `app.py` line 25:
```python
ollama_client = OllamaClient(model="your_model_here")
```

### Adjust Performance Settings
Edit `ollama_client.py` `default_options`:
```python
self.default_options = {
    'temperature': 0.3,      # Lower = faster
    'num_ctx': 2048,         # Smaller = faster
    'num_predict': 800,      # Lower = faster
    'top_p': 0.9,
    'top_k': 40
}
```

## 📞 Support

If you encounter issues:
1. Check Ollama is running: `ollama ps`
2. Verify model: `ollama list`
3. Run benchmark: `python benchmark.py`
4. Check logs in terminal

---

**Ready to generate curricula at lightning speed! ⚡**
