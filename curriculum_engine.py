"""
Curriculum Engine - Core Logic for Structure and Validation
Pre-calculates structure to avoid asking AI (saves 5-10 seconds)
"""
import json
import re
from typing import Dict, List, Any, Optional


class CurriculumEngine:
    """Handles curriculum structure calculation and validation."""
    
    # Standard credit allocation
    CREDITS_PER_COURSE = 4
    COURSES_PER_SEMESTER = 3  # Fixed for speed and consistency
    
    @staticmethod
    def calculate_structure(semesters: int, hours: str) -> Dict[str, int]:
        """
        Pre-calculate curriculum structure (don't ask AI).
        
        This saves 5-10 seconds by not requiring AI to decide structure.
        
        Args:
            semesters: Number of semesters
            hours: Weekly hours (string like "20-25")
            
        Returns:
            Dict with total_courses, total_credits, courses_per_semester
        """
        courses_per_sem = CurriculumEngine.COURSES_PER_SEMESTER
        total_courses = semesters * courses_per_sem
        total_credits = total_courses * CurriculumEngine.CREDITS_PER_COURSE
        
        return {
            'total_courses': total_courses,
            'total_credits': total_credits,
            'courses_per_semester': courses_per_sem,
            'semesters': semesters
        }
    
    @staticmethod
    def parse_ai_response(raw_response: str) -> Optional[Dict]:
        """
        Parse JSON from AI response with aggressive cleaning.
        
        Args:
            raw_response: Raw text from Ollama
            
        Returns:
            Parsed JSON dict or None if parsing fails
        """
        try:
            # Strip markdown code blocks
            cleaned = re.sub(r'```(?:json)?', '', raw_response, flags=re.IGNORECASE)
            cleaned = cleaned.replace('```', '').strip()
            
            # Find JSON object
            start = cleaned.find('{')
            end = cleaned.rfind('}') + 1
            
            if start != -1 and end > start:
                json_str = cleaned[start:end]
                return json.loads(json_str)
            
            # Try parsing entire response
            return json.loads(cleaned)
            
        except json.JSONDecodeError:
            return None
    
    @staticmethod
    def validate_curriculum(curriculum: Dict) -> bool:
        """
        Validate curriculum structure.
        
        Args:
            curriculum: Parsed curriculum dict
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check required top-level keys
            if 'program' not in curriculum or 'semesters' not in curriculum:
                return False
            
            # Check semesters is a list
            if not isinstance(curriculum['semesters'], list):
                return False
            
            # Validate each semester
            for sem in curriculum['semesters']:
                if 'semester' not in sem or 'subjects' not in sem:
                    return False
                
                # Validate subjects
                for subj in sem.get('subjects', []):
                    required_keys = ['name', 'code', 'credits', 'hours_per_week', 'description', 'topics']
                    if not all(key in subj for key in required_keys):
                        return False
            
            return True
            
        except:
            return False
    
    @staticmethod
    def fill_missing_topics(course: Dict) -> Dict:
        """
        Fill missing topics with placeholders if AI didn't generate them.
        
        Args:
            course: Course dict
            
        Returns:
            Course dict with topics filled
        """
        if 'topics' not in course or not course['topics']:
            course['topics'] = [
                f"{course.get('name', 'Course')} Fundamentals",
                f"Advanced {course.get('name', 'Course')} Concepts"
            ]
        
        return course
    
    @staticmethod
    def ensure_minimum_quality(curriculum: Dict) -> Dict:
        """
        Ensure curriculum meets minimum quality standards.
        
        Args:
            curriculum: Curriculum dict
            
        Returns:
            Enhanced curriculum dict
        """
        # Fill missing topics for all courses
        for sem in curriculum.get('semesters', []):
            for subj in sem.get('subjects', []):
                CurriculumEngine.fill_missing_topics(subj)
        
        return curriculum
