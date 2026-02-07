"""
Professional PDF Generator using ReportLab
Target: <2 seconds generation time
"""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether
)
from reportlab.lib import colors
from html import escape
import io
import re
from datetime import datetime
from typing import Dict, Any


class PDFGenerator:
    """Generate professional curriculum PDFs with ReportLab."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles for professional formatting."""
        
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            textColor=colors.HexColor('#5b54e0'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        # Semester header style
        self.styles.add(ParagraphStyle(
            name='SemesterHeader',
            parent=self.styles['Heading1'],
            fontSize=16,
            textColor=colors.white,
            backColor=colors.HexColor('#5b54e0'),
            spaceAfter=12,
            spaceBefore=12,
            leftIndent=10,
            rightIndent=10
        ))
        
        # Course title style
        self.styles.add(ParagraphStyle(
            name='CourseTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#111827'),
            spaceAfter=6,
            spaceBefore=12
        ))
        
        # Custom Normal style with better line spacing
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#374151')
        ))
        
        # Heading3 with better styling
        self.styles.add(ParagraphStyle(
            name='CustomHeading3',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#4338ca'),
            spaceAfter=8,
            spaceBefore=10
        ))
    
    def generate_pdf(self, curriculum: Dict[str, Any], filename: str = None) -> io.BytesIO:
        """
        Generate PDF from curriculum data.
        
        Args:
            curriculum: Curriculum dictionary
            filename: Optional filename (defaults to timestamp)
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build content
        story = []
        
        # Title Page
        story.extend(self._build_title_page(curriculum))
        
        # Program Structure
        story.extend(self._build_structure_section(curriculum))
        
        story.append(PageBreak())
        
        # Detailed Syllabi (if available)
        # This will be populated when subject details are cached
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _build_title_page(self, curriculum: Dict) -> list:
        """Build title page elements."""
        elements = []
        
        program_name = escape(curriculum.get('program', 'Academic Program'))
        
        elements.append(Paragraph(
            f"Curriculum for {program_name}",
            self.styles['CustomTitle']
        ))
        
        elements.append(Spacer(1, 0.5 * inch))
        
        # Program details table
        details = [
            ['Total Semesters:', str(len(curriculum.get('semesters', [])))],
            ['Total Courses:', str(sum(len(s.get('subjects', [])) for s in curriculum.get('semesters', [])))],
            ['Generated:', datetime.now().strftime('%Y-%m-%d %H:%M')]
        ]
        
        table = Table(details, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5 * inch))
        
        return elements
    
    def _build_structure_section(self, curriculum: Dict) -> list:
        """Build program structure section."""
        elements = []
        
        elements.append(Paragraph("Program Structure", self.styles['Heading1']))
        elements.append(Spacer(1, 0.2 * inch))
        
        for sem in curriculum.get('semesters', []):
            sem_num = sem.get('semester', 0)
            subjects = sem.get('subjects', [])
            
            # Semester header
            elements.append(Paragraph(
                f"Semester {sem_num}: {len(subjects)} Courses",
                self.styles['SemesterHeader']
            ))
            
            # Subjects table
            table_data = [['Code', 'Course Name', 'Credits', 'Hours/Week']]
            
            for subj in subjects:
                table_data.append([
                    escape(subj.get('code', '')),
                    escape(subj.get('name', '')),
                    str(subj.get('credits', 4)),
                    str(subj.get('hours_per_week', 3))
                ])
            
            table = Table(table_data, colWidths=[1*inch, 3.5*inch, 1*inch, 1.2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e0e7ff')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#4338ca')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.3 * inch))
        
        return elements    
    def generate_course_pdf(self, subject_name: str, markdown_content: str) -> io.BytesIO:
        """
        Generate PDF for individual course syllabus.
        
        Args:
            subject_name: Name of the course
            markdown_content: Markdown-formatted syllabus content
            
        Returns:
            BytesIO buffer containing PDF
        """
        buffer = io.BytesIO()
        
        # Create document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        story = []
        
        # Course title
        story.append(Paragraph(
            escape(subject_name),
            self.styles['CustomTitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Parse markdown content and convert to PDF elements
        story.extend(self._parse_markdown_to_pdf(markdown_content))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    def _parse_markdown_to_pdf(self, markdown_text: str) -> list:
        """
        Convert markdown content to ReportLab flowables.
        
        Args:
            markdown_text: Markdown formatted text
            
        Returns:
            List of ReportLab flowable elements
        """
        elements = []
        lines = markdown_text.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip empty lines but add small spacing
            if not line:
                elements.append(Spacer(1, 0.05 * inch))
                i += 1
                continue
            
            # H2 headers (##)
            if line.startswith('## '):
                header_text = line[3:].strip()
                # Remove emoji if present
                header_text = re.sub(r'[^\w\s:()-]', '', header_text).strip()
                elements.append(Spacer(1, 0.25 * inch))
                elements.append(Paragraph(
                    header_text,
                    self.styles['Heading2']
                ))
                elements.append(Spacer(1, 0.15 * inch))
            
            # H3 headers (###)
            elif line.startswith('### '):
                header_text = line[4:].strip()
                # Remove emoji if present
                header_text = re.sub(r'[^\w\s:()-]', '', header_text).strip()
                elements.append(Spacer(1, 0.2 * inch))
                elements.append(Paragraph(
                    f"<b>{escape(header_text)}</b>",
                    self.styles['CustomHeading3']
                ))
                elements.append(Spacer(1, 0.1 * inch))
            
            # List items (-)
            elif line.startswith('- '):
                list_items = []
                while i < len(lines) and lines[i].strip().startswith('- '):
                    item_text = lines[i].strip()[2:]
                    # Handle bold text (**text**)
                    item_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', item_text)
                    # Handle italic text (*text*)
                    item_text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', item_text)
                    list_items.append(item_text)
                    i += 1
                
                # Create list with proper indentation
                for item in list_items:
                    elements.append(Paragraph(
                        f"&nbsp;&nbsp;&nbsp;• {item}",
                        self.styles['CustomNormal']
                    ))
                    elements.append(Spacer(1, 0.08 * inch))
                
                continue  # Skip the i += 1 at the end
            
            # Regular paragraph
            else:
                # Handle bold text
                text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
                # Handle italic text
                text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
                # Remove emoji
                text = re.sub(r'[^\w\s:().,%\-–—/\'"<>b/i]', '', text)
                elements.append(Paragraph(text, self.styles['CustomNormal']))
                elements.append(Spacer(1, 0.1 * inch))
            
            i += 1
        
        return elements