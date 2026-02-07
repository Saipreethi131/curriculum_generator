"""Speed test - Groq vs Ollama"""
from groq_client import GroqClient
from ollama_client import OllamaClient
from prompt_templates import build_structure_prompt
import json
import os

def test_model(client, name):
    print(f"\n{'=' * 50}")
    print(f"TESTING: {name}")
    print(f"{'=' * 50}")
    
    prompt = build_structure_prompt("Machine Learning", "Undergraduate", 2, "20-25")
    
    print("Generating curriculum...")
    result = client.generate(prompt)
    
    print(f"\nSUCCESS: {result['success']}")
    print(f"TIME:    {result['generation_time']}s")
    
    if result['success']:
        try:
            resp = result['response'].strip().replace('```json', '').replace('```', '').strip()
            data = json.loads(resp)
            semesters = data.get('semesters', [])
            print(f"Semesters: {len(semesters)}")
            for sem in semesters:
                print(f"  Sem {sem['semester']}: {len(sem.get('subjects', []))} courses")
            print("JSON PARSE: OK")
        except Exception as e:
            print(f"JSON PARSE FAILED: {e}")
            print(result['response'][:300])
    else:
        print(f"Error: {result.get('error')}")

# Test Groq
groq = GroqClient()
if groq.is_available():
    test_model(groq, f"Groq ({groq.model})")
else:
    print("\n⚠️  GROQ_API_KEY not set!")
    print("   Get free key: https://console.groq.com")
    print("   Then run: $env:GROQ_API_KEY='gsk_your_key_here'")
    print("   Then re-run: python test_speed.py")
