"""
Performance Benchmarking Tool
Tests curriculum generation latency and validates <20s target
"""
import time
import sys
from ollama_client import OllamaClient
from prompt_templates import build_structure_prompt
from curriculum_engine import CurriculumEngine

# Test scenarios
TEST_SCENARIOS = [
    {
        "name": "Machine Learning Masters (4 sem)",
        "skill": "Machine Learning",
        "level": "Masters",
        "semesters": 4,
        "hours": "20-25",
        "industry": "AI"
    },
    {
        "name": "Full Stack Web Dev (2 sem)",
        "skill": "Full Stack Web Development",
        "level": "Undergraduate",
        "semesters": 2,
        "hours": "30",
        "industry": "Web"
    },
    {
        "name": "Python Data Science (2 sem)",
        "skill": "Python Data Science",
        "level": "Diploma",
        "semesters": 2,
        "hours": "15-20",
        "industry": "Data Science"
    }
]

def run_benchmark(client: OllamaClient, scenario: dict) -> dict:
    """Run single benchmark test."""
    print(f"\n{'='*80}")
    print(f"Testing: {scenario['name']}")
    print(f"{'='*80}")
    
    # Build prompt
    prompt = build_structure_prompt(
        skill=scenario['skill'],
        level=scenario['level'],
        semesters=scenario['semesters'],
        hours=scenario['hours'],
        industry=scenario['industry']
    )
    
    # Generate
    start_time = time.time()
    result = client.generate(prompt)
    elapsed = time.time() - start_time
    
    # Parse and validate
    engine = CurriculumEngine()
    curriculum = engine.parse_ai_response(result['response'])
    valid = engine.validate_curriculum(curriculum) if curriculum else False
    
    # Results
    status = "✅ PASS" if elapsed < 20 and valid else "❌ FAIL"
    
    print(f"\nResults:")
    print(f"  Time: {elapsed:.2f}s")
    print(f"  Target: <20s")
    print(f"  Valid: {valid}")
    print(f"  Status: {status}")
    
    if elapsed < 20:
        print(f"  🎉 Under target by {20 - elapsed:.2f}s!")
    else:
        print(f"  ⚠️  Over target by {elapsed - 20:.2f}s")
    
    return {
        'scenario': scenario['name'],
        'time': elapsed,
        'valid': valid,
        'pass': elapsed < 20 and valid
    }

def main():
    """Run benchmark suite."""
    print("\n" + "="*80)
    print("🚀 GenAI Curriculum Generator - Performance Benchmark")
    print("="*80)
    print(f"Target: <20 seconds per generation")
    print(f"Hardware: Intel i5 11th Gen, 16GB RAM (or equivalent)")
    print("="*80)
    
    # Initialize client
    client = OllamaClient(model="phi3:mini")
    
    # Health check
    print("\n📊 System Check:")
    health = client.health_check()
    
    print(f"  Ollama: {'✅ Connected' if health['ollama_connected'] else '❌ Not running'}")
    print(f"  Model: {client.model}")
    print(f"  Available: {'✅ Yes' if health['model_available'] else '❌ No'}")
    
    if not health['ollama_connected']:
        print("\n❌ ERROR: Ollama is not running!")
        print("   Start with: ollama serve")
        sys.exit(1)
    
    if not health['model_available']:
        print(f"\n❌ ERROR: Model '{client.model}' not found!")
        print(f"   Pull with: ollama pull {client.model}")
        sys.exit(1)
    
    # Run tests
    results = []
    
    for scenario in TEST_SCENARIOS:
        result = run_benchmark(client, scenario)
        results.append(result)
        time.sleep(1)  # Brief pause between tests
    
    # Summary
    print("\n" + "="*80)
    print("📊 BENCHMARK SUMMARY")
    print("="*80)
    
    total_time = sum(r['time'] for r in results)
    avg_time = total_time / len(results)
    passed = sum(1 for r in results if r['pass'])
    
    print(f"\nTests Run: {len(results)}")
    print(f"Passed: {passed}/{len(results)}")
    print(f"Average Time: {avg_time:.2f}s")
    print(f"Total Time: {total_time:.2f}s")
    
    print(f"\nDetailed Results:")
    for r in results:
        status = "✅" if r['pass'] else "❌"
        print(f"  {status} {r['scenario']}: {r['time']:.2f}s")
    
    # Final verdict
    print("\n" + "="*80)
    if all(r['pass'] for r in results):
        print("🎉 ALL TESTS PASSED!")
        print("   System meets <20s performance target")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("   Consider:")
        print("   1. Switching to faster model (llama3.2:3b)")
        print("   2. Reducing num_predict in ollama_client.py")
        print("   3. Closing other applications")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
