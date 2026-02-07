"""
Speed-Optimized Prompt Templates for Curriculum Generation
Key: Shorter prompts = faster responses (target: <200 words)
"""

def build_structure_prompt(skill: str, level: str, semesters: int, hours: str, industry: str = "") -> str:
    """
    Build optimized prompt for curriculum structure generation.
    
    OPTIMIZATION STRATEGY:
    - Concise instructions (<200 words)
    - JSON format requirement (faster to parse)
    - One-shot example (reduces back-and-forth)
    - Pre-calculated structure (don't ask AI to decide)
    """
    
    courses_per_sem = 3  # Groq is fast enough for 3 courses/semester
    total_courses = semesters * courses_per_sem
    
    industry_note = f", {industry} focus" if industry else ""
    
    # Build semester structure examples to make the requirement crystal clear
    semester_examples = []
    for sem_num in range(1, min(semesters + 1, 3)):  # Show first 2 semesters as examples
        semester_examples.append(f"""    {{
      "semester": {sem_num},
      "subjects": [
        {{"name": "Course Name", "code": "SKL{sem_num}01", "credits": 3, "hours_per_week": 4, "description": "Brief description", "topics": ["Topic1", "Topic2"]}},
        {{"name": "Advanced Course", "code": "SKL{sem_num}02", "credits": 4, "hours_per_week": 5, "description": "Brief description", "topics": ["Topic1", "Topic2"]}}
      ]
    }}""")
    
    # Add ellipsis if more than 2 semesters
    if semesters > 2:
        semester_examples.append(f"""    ... (continue through semester {semesters})""")
    
    semester_structure = ",\n".join(semester_examples)
    
    prompt = f"""Generate a {level} curriculum for "{skill}"{industry_note}.

CRITICAL REQUIREMENT: Generate EXACTLY {semesters} semesters, {courses_per_sem} courses per semester, {hours} hours/week.

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "program": "{skill}",
  "semesters": [
{semester_structure}
  ]
}}

MANDATORY RULES:
- Generate EXACTLY {semesters} semesters (NOT 8, NOT 4, EXACTLY {semesters}!)
- Each semester must have EXACTLY {courses_per_sem} courses
- Total courses: {total_courses}
- Include all semesters from 1 to {semesters}
- Each subject needs: name, code, credits (3-4 based on complexity), hours_per_week (4-6), description (8 words max), topics (2 items)
- Vary credits: foundational courses = 3 credits, advanced/major courses = 4 credits
- Vary hours: lighter courses = 4-5 hours/week, intensive courses = 5-6 hours/week
- Progressive difficulty across semesters
- Unique realistic course codes"""
    
    return prompt


def build_subject_detail_prompt(subject: str, program: str) -> str:
    """
    Build optimized prompt for subject syllabus generation.
    
    OPTIMIZATION: Structured prompt for complete syllabus generation
    """
    
    prompt = f"""Design a detailed syllabus for the course **"{subject}"** in the {program} program.

Format your response in clean Markdown exactly like this:

## 🎯 Course Objective
One clear sentence about what students will learn.

## 📋 Course Modules

### Unit 1: [Module Title] (2-3 weeks)
- **Topic:** [First core topic with brief explanation]
- **Topic:** [Second core topic with brief explanation]
- **Topic:** [Third core topic with brief explanation]
- **Lab/Activity:** [Practical exercise]

### Unit 2: [Module Title] (2-3 weeks)
- **Topic:** [First core topic with brief explanation]
- **Topic:** [Second core topic with brief explanation]
- **Topic:** [Third core topic with brief explanation]
- **Lab/Activity:** [Practical exercise]

### Unit 3: [Module Title] (2-3 weeks)
- **Topic:** [First core topic with brief explanation]
- **Topic:** [Second core topic with brief explanation]
- **Topic:** [Third core topic with brief explanation]
- **Lab/Activity:** [Practical exercise]

### Unit 4: [Module Title] (2-3 weeks)
- **Topic:** [First core topic with brief explanation]
- **Topic:** [Second core topic with brief explanation]
- **Topic:** [Third core topic with brief explanation]
- **Lab/Activity:** [Practical exercise]

### Unit 5: [Module Title] (2-3 weeks)
- **Topic:** [First core topic with brief explanation]
- **Topic:** [Second core topic with brief explanation]
- **Topic:** [Third core topic with brief explanation]
- **Lab/Activity:** [Practical exercise]

## 📖 Recommended Reading
- **Book:** [Title] by [Author]
- **Book:** [Title] by [Author]
- **Online Resource:** [Resource name]

## 📅 Course Schedule
- **Weeks 1-3:** Unit 1 - [Topic area]
- **Weeks 4-6:** Unit 2 - [Topic area]
- **Weeks 7-9:** Unit 3 - [Topic area]
- **Weeks 10-12:** Unit 4 - [Topic area]
- **Weeks 13-15:** Unit 5 - [Topic area]
- **Week 16:** Final project presentations

## ✅ Assessment
- **Assignments:** 30%
- **Mid-term Exam:** 25%
- **Final Project:** 35%
- **Class Participation:** 10%

## 💡 Capstone Project Ideas
Suggest 3-4 practical project ideas that students can work on:
- **Project 1:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 2:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 3:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 4:** [Project title] - [Brief description of what students will build and technologies/concepts used]

Make projects relevant to real-world applications and include specific technologies or methodologies students will apply.

## 🏆 Industry Certifications
Suggest 2-3 relevant industry certifications that align with this course:
- **Certification Name:** [Provider] - [Brief description of alignment]
- **Certification Name:** [Provider] - [Brief description of alignment]
- **Certification Name:** [Provider] - [Brief description of alignment]

Examples: AWS Certified Solutions Architect, Google Cloud Professional, Microsoft Azure Administrator, CompTIA Security+, Oracle Certified Professional, Cisco CCNA, etc.

IMPORTANT: Complete ALL sections fully. Include 5 units with specific week allocations."""
    
    return prompt


# Prompt length validation
def validate_prompt_length(prompt: str, max_words: int = 200) -> bool:
    """Ensure prompts stay under word limit for speed."""
    word_count = len(prompt.split())
    return word_count <= max_words
