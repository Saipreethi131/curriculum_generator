"""
Speed-Optimized Prompt Templates for Curriculum Generation
Key: Shorter prompts = faster responses (target: <200 words)
"""

import json

def build_structure_prompt(skill: str, level: str, semesters: int, hours: str, industry: str = "", courses_per_sem: int = 3, custom_settings: dict = None) -> str:
    """
    Build optimized prompt for curriculum structure generation.
    """
    if custom_settings is None:
        custom_settings = {}
        
    total_courses = semesters * courses_per_sem
    industry_note = f", {industry} focus" if industry else ""
    
    # Extract advanced settings
    academic_system = custom_settings.get('academicSystem', 'semester')
    difficulty = custom_settings.get('difficultyLevel', 'intermediate')
    learning_style = custom_settings.get('learningStyle', 'practical')
    prerequisites = custom_settings.get('prerequisites', 'assume')
    cert_focus = custom_settings.get('certFocus', True)
    project_focus = custom_settings.get('projectFocus', True)
    
    # Build semester structure examples
    semester_examples = []
    for sem_num in range(1, min(semesters + 1, 3)):
        semester_examples.append(f"""    {{
      "semester": {sem_num},
      "subjects": [
        {{"name": "Course Name", "code": "SKL{sem_num}01", "credits": 3, "hours_per_week": 4, "description": "Brief description", "topics": ["Topic1", "Topic2"], "skills": ["Skill A", "Skill B", "Skill C"]}},
        ... ({courses_per_sem} courses total)
      ]
    }}""")
    
    if semesters > 2:
        semester_examples.append(f"""    ... (continue through {academic_system} {semesters})""")
    
    semester_structure = ",\n".join(semester_examples)
    
    prompt = f"""Generate a {level} curriculum for "{skill}"{industry_note} using the {academic_system} system.

CRITICAL PARAMETERS:
- Difficulty: {difficulty}
- Learning Style: {learning_style}
- Prerequisites: {prerequisites}
- Certification Focus: {"Yes" if cert_focus else "No"}
- Project Focus: {"Yes" if project_focus else "No"}
- Structure: {semesters} {academic_system}s, {courses_per_sem} courses/{academic_system}, {hours} total hours/week.

Respond with ONLY valid JSON (no markdown, no explanation):
{{
  "program": "{skill}",
  "semesters": [
{semester_structure}
  ]
}}

MANDATORY RULES:
- Generate EXACTLY {semesters} {academic_system}s
- Each {academic_system} must have EXACTLY {courses_per_sem} courses
- Total courses: {total_courses}
- Each subject needs: name, code, credits (3-4), hours_per_week (4-6), description (8 words max), topics (2 items), skills (3 key skills students will gain)
- Progressive difficulty: starts at {difficulty} level and advances
- Skills should show clear progression across semesters (fundamentals first, advanced later)
- Realistic unique course codes"""
    
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

## 💡 Capstone Project Ideas
Suggest 3-4 practical project ideas that students can work on:
- **Project 1:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 2:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 3:** [Project title] - [Brief description of what students will build and technologies/concepts used]
- **Project 4:** [Project title] - [Brief description of what students will build and technologies/concepts used]

Make projects relevant to real-world applications and include specific technologies or methodologies students will apply.

## 🏆 Industry Certifications
Suggest 2-3 relevant industry certifications that align with this course:
- **Certification Name** — Provider — Brief description of alignment
- **Certification Name** — Provider — Brief description of alignment
- **Certification Name** — Provider — Brief description of alignment

Use ONLY real, well-known certifications. Examples: AWS Certified Solutions Architect, Google Cloud Professional, Microsoft Azure Administrator, CompTIA Security+, Cisco CCNA, Oracle Certified Professional, etc. Do NOT include URLs.

IMPORTANT: Complete ALL sections fully. Include 5 units with specific week allocations."""
    
    return prompt


# Prompt length validation
def validate_prompt_length(prompt: str, max_words: int = 200) -> bool:
    """Ensure prompts stay under word limit for speed."""
    word_count = len(prompt.split())
    return word_count <= max_words


def build_chat_prompt(user_message: str, context: dict = None) -> str:
    """
    Build optimized prompt for chatbot responses about curriculum generation.
    """
    if context is None:
        context = {}
    
    current_program = context.get('program', 'unknown program')
    current_level = context.get('level', 'unknown level')
    custom_settings = context.get('custom_settings', {})
    
    context_info = f"\n\nCURRENT CONTEXT:\nProgram: {current_program}\nLevel: {current_level}"
    if custom_settings:
        context_info += f"\nSettings: {json.dumps(custom_settings)}"
    
    if context.get('curriculum_data'):
        context_info += "\nUser is working on a generated curriculum."
    
    prompt = f"""You are an expert educational consultant and curriculum advisor. You help users with:
- Curriculum design and course selection
- Learning path recommendations  
- Educational concepts and explanations
- Study strategies and career advice
- Technical skills development

Be helpful, concise, and practical. Support the user's specific goals.

USER QUESTION: {user_message}{context_info}

RESPONSE:"""
    
    return prompt
