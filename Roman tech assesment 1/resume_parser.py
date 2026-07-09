"""
Resume Parser Module
Handles parsing of resume files in different formats (.txt, .pdf, .docx)
"""
import os
from pathlib import Path


class ResumeParser:
    """Parse resume files and extract relevant information"""

    def __init__(self):
        self.supported_formats = ['.txt', '.pdf', '.docx']

    def parse_resume(self, file_path):
        """
        Parse a resume file and extract information.
        
        Args:
            file_path: Path to the resume file
            
        Returns:
            dict: Contains name, skills, experience, education, raw_text
        """
        file_path = Path(file_path)
        file_ext = file_path.suffix.lower()

        if file_ext == '.txt':
            return self._parse_txt(file_path)
        elif file_ext == '.pdf':
            return self._parse_pdf(file_path)
        elif file_ext == '.docx':
            return self._parse_docx(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_ext}")

    def _parse_txt(self, file_path):
        """Parse .txt resume file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                text = f.read()

        return self._extract_information(text)

    def _parse_pdf(self, file_path):
        """Parse .pdf resume file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            return self._extract_information(text)
        except ImportError:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")

    def _parse_docx(self, file_path):
        """Parse .docx resume file"""
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([para.text for para in doc.paragraphs])
            return self._extract_information(text)
        except ImportError:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")

    def _extract_information(self, text):
        """
        Extract structured information from resume text.
        Uses pattern matching to identify key sections.
        """
        lower_text = text.lower()
        
        # Extract name (usually first line or after "Name:" tag)
        name = self._extract_name(text)
        
        # Extract skills section
        skills = self._extract_skills(text)
        
        # Extract experience summary
        experience = self._extract_experience(text)
        
        # Extract education summary
        education = self._extract_education(text)

        return {
            'name': name,
            'skills': skills,
            'experience': experience,
            'education': education,
            'raw_text': text
        }

    def _extract_name(self, text):
        """Extract name from resume"""
        lines = text.split('\n')
        # Try to find name in first few lines
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) <= 3 and len(line) < 50:
                # Check if it looks like a name (not an email or URL)
                if '@' not in line and '://' not in line and any(c.isupper() for c in line):
                    return line
        return "Unknown"

    def _extract_skills(self, text):
        """Extract technical skills from resume"""
        keywords = [
            'Python', 'JavaScript', 'TypeScript', 'Java', 'Go', 'C++', 'C#', 'Ruby', 'PHP',
            'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Django', 'FastAPI', 'Flask',
            'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch', 'MySQL', 'NoSQL', 'SQL',
            'AWS', 'Azure', 'GCP', 'Google Cloud', 'Docker', 'Kubernetes', 'CI/CD',
            'Jenkins', 'GitLab', 'GitHub', 'Terraform', 'Ansible', 'Linux',
            'GraphQL', 'REST', 'API', 'Microservices', 'Kafka', 'Spark',
            'TensorFlow', 'PyTorch', 'Machine Learning', 'Scikit-learn',
            'Swift', 'Kotlin', 'React Native', 'Flutter',
            'Git', 'Nginx', 'Apache', 'HTML5', 'CSS3', 'Bootstrap'
        ]
        
        found_skills = []
        for skill in keywords:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return found_skills

    def _extract_experience(self, text):
        """Extract experience summary from resume"""
        lines = text.split('\n')
        experience_section = []
        in_experience = False
        
        for line in lines:
            lower_line = line.lower()
            if 'professional experience' in lower_line or 'work experience' in lower_line:
                in_experience = True
                continue
            elif 'education' in lower_line and in_experience:
                break
            elif in_experience:
                stripped = line.strip()
                if stripped:
                    experience_section.append(stripped)
                if len(experience_section) > 10:  # Limit to first 10 lines
                    break
        
        return ' '.join(experience_section[:5]) if experience_section else "No experience details found"

    def _extract_education(self, text):
        """Extract education summary from resume"""
        lines = text.split('\n')
        education_section = []
        in_education = False
        
        for line in lines:
            lower_line = line.lower()
            if 'education' in lower_line:
                in_education = True
                continue
            elif in_education and any(x in lower_line for x in ['certification', 'skills', 'professional']):
                break
            elif in_education:
                stripped = line.strip()
                if stripped:
                    education_section.append(stripped)
                if len(education_section) > 5:  # Limit to first 5 lines
                    break
        
        return ' '.join(education_section[:3]) if education_section else "No education details found"
