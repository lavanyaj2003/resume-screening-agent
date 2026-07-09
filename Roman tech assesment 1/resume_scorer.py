"""
Resume Scorer Module
Scores resumes against a job description using TF-IDF and optional OpenAI API
"""
import os
import math
from collections import Counter
from typing import Dict, List, Tuple


class ResumeScorer:
    """Score resumes against a job description"""

    def __init__(self, use_openai=False):
        """
        Initialize the scorer.
        
        Args:
            use_openai: Whether to use OpenAI API if OPENAI_API_KEY is available
        """
        self.use_openai = use_openai and self._has_openai_key()
        if self.use_openai:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = os.getenv('OPENAI_API_KEY')
            except ImportError:
                self.use_openai = False

    def _has_openai_key(self):
        """Check if OpenAI API key is available"""
        return bool(os.getenv('OPENAI_API_KEY'))

    def score_resume(self, job_description: str, resume: Dict) -> Tuple[float, str]:
        """
        Score a single resume against the job description.
        
        Args:
            job_description: The job description text
            resume: Resume dict with keys: name, skills, experience, education, raw_text
            
        Returns:
            Tuple of (score, reasoning)
        """
        # Calculate TF-IDF similarity score
        tfidf_score = self._tfidf_similarity(job_description, resume['raw_text'])
        
        # Calculate skill matching bonus
        skill_bonus = self._skill_match_score(job_description, resume)
        
        # Combine scores with a slightly different weighting for a distinct variant
        local_score = min(100, (tfidf_score * 0.65 + skill_bonus * 0.35) * 100)
        
        reasoning = self._generate_reasoning(
            resume, job_description, local_score, tfidf_score, skill_bonus
        )
        
        # If OpenAI is available, use it for additional reasoning
        if self.use_openai:
            try:
                ai_score, ai_reasoning = self._openai_score_resume(
                    job_description, resume, local_score
                )
                # Blend the scores (70% local, 30% AI)
                final_score = local_score * 0.7 + ai_score * 0.3
                reasoning = f"{reasoning}\n\nOpenAI Analysis: {ai_reasoning}"
                return final_score, reasoning
            except Exception as e:
                print(f"Warning: OpenAI API call failed: {e}. Using local scoring only.")
        
        return local_score, reasoning

    def _tfidf_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate TF-IDF cosine similarity between two texts.
        
        Args:
            text1: Job description
            text2: Resume text
            
        Returns:
            Similarity score between 0 and 1
        """
        # Preprocess texts (use simpler word filtering)
        words1 = self._preprocess_text(text1)
        words2 = self._preprocess_text(text2)
        
        if not words1 or not words2:
            return 0.0
        
        # Build term frequency vectors
        tf1 = self._calculate_tf(words1)
        tf2 = self._calculate_tf(words2)
        
        # Calculate IDF using a larger corpus assumption
        # This gives more weight to rare/specific terms
        all_words = set(words1 + words2)
        
        # Enhanced IDF calculation that works better with 2 documents
        idf = {}
        for word in all_words:
            word_in_jd = word in words1
            word_in_resume = word in words2
            
            # Words appearing in both docs get lower IDF (common)
            # Words in only one get higher IDF (specific)
            if word_in_jd and word_in_resume:
                idf[word] = 1.0  # Common terms
            elif word_in_jd or word_in_resume:
                idf[word] = 1.5  # Specific terms
            else:
                idf[word] = 0.0
        
        # Calculate TF-IDF vectors
        tfidf1 = {word: tf1.get(word, 0) * idf.get(word, 0) for word in all_words}
        tfidf2 = {word: tf2.get(word, 0) * idf.get(word, 0) for word in all_words}
        
        # Calculate cosine similarity
        return self._cosine_similarity(tfidf1, tfidf2)

    def _preprocess_text(self, text: str) -> List[str]:
        """Preprocess text: lowercase, tokenize, keep meaningful words"""
        text = text.lower()
        # Simple tokenization - split on non-alphanumeric characters
        import re
        words = re.findall(r'\b\w+\b', text)
        # Keep words 2+ chars, filter out common stop words
        stop_words = {'the', 'is', 'at', 'which', 'on', 'and', 'or', 'if', 'be', 
                      'to', 'of', 'in', 'for', 'with', 'by', 'a', 'as', 'an', 'are',
                      'from', 'has', 'this', 'that', 'was', 'were', 'have', 'he', 'she',
                      'it', 'we', 'you', 'they', 'can', 'will', 'may', 'should'}
        return [w for w in words if len(w) >= 2 and w not in stop_words]

    def _calculate_tf(self, words: List[str]) -> Dict[str, float]:
        """Calculate Term Frequency"""
        counter = Counter(words)
        total = len(words)
        if total == 0:
            return {}
        return {word: count / total for word, count in counter.items()}

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two vectors"""
        # Calculate dot product
        dot_product = sum(vec1.get(word, 0) * vec2.get(word, 0) for word in vec1)
        
        # Calculate magnitudes
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)

    def _skill_match_score(self, job_description: str, resume: Dict) -> float:
        """
        Calculate skill matching score.
        Compares resume skills with job description keywords.
        """
        # Extract key technical terms from job description
        job_keywords = self._extract_key_keywords(job_description)
        resume_skills = set(s.lower() for s in resume['skills'])
        
        # Count matches
        matches = sum(1 for skill in resume_skills 
                     if any(keyword.lower() in skill for keyword in job_keywords))
        
        # Bonus for having many relevant skills
        if len(resume_skills) == 0:
            return 0
        
        match_percentage = min(1.0, matches / len(job_keywords))
        
        # Boost score based on number of relevant skills
        skill_count_bonus = min(0.3, len(resume_skills) / 20)
        
        return min(1.0, match_percentage + skill_count_bonus)

    def _extract_key_keywords(self, text: str) -> List[str]:
        """Extract key technical keywords from job description"""
        keywords = [
            'Python', 'JavaScript', 'Java', 'Go', 'TypeScript', 'React', 'Vue',
            'Node.js', 'Django', 'FastAPI', 'PostgreSQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'Docker', 'Kubernetes', 'CI/CD', 'GraphQL',
            'REST', 'microservices', 'cloud', 'database', 'API', 'TensorFlow',
            'PyTorch', 'machine learning', 'Linux', 'Git', 'Terraform'
        ]
        
        found = []
        for keyword in keywords:
            if keyword.lower() in text.lower():
                found.append(keyword)
        
        return found if found else keywords

    def _generate_reasoning(self, resume: Dict, job_description: str, 
                           score: float, tfidf: float, skill_bonus: float) -> str:
        """Generate reasoning for the score"""
        reasoning = f"Candidate: {resume['name']}\n"
        reasoning += f"Overall Score: {score:.1f}/100\n"
        reasoning += f"Score Breakdown:\n"
        reasoning += f"  - TF-IDF Similarity: {tfidf*100:.1f}%\n"
        reasoning += f"  - Skill Match: {skill_bonus*100:.1f}%\n"
        
        if resume['skills']:
            reasoning += f"Detected Skills: {', '.join(resume['skills'][:5])}"
            if len(resume['skills']) > 5:
                reasoning += f" +{len(resume['skills'])-5} more"
            reasoning += "\n"
        
        return reasoning

    def _openai_score_resume(self, job_description: str, resume: Dict, 
                            local_score: float) -> Tuple[float, str]:
        """
        Use OpenAI API to score and provide reasoning.
        
        Args:
            job_description: The job description
            resume: Resume data
            local_score: The local TF-IDF score
            
        Returns:
            Tuple of (openai_score, reasoning)
        """
        try:
            prompt = f"""
            Job Description:
            {job_description[:1000]}
            
            Resume Summary:
            Name: {resume['name']}
            Skills: {', '.join(resume['skills'])}
            Education: {resume['education'][:200]}
            
            Based on this job description and resume, provide:
            1. A relevance score from 0-100
            2. A brief one-sentence explanation of why this candidate is well/poorly matched
            
            Format your response as:
            SCORE: [number]
            REASON: [reason]
            """
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a recruiter scoring resume relevance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            response_text = response.choices[0].message.content
            
            # Parse score and reason
            score = local_score  # Default to local score
            reason = "AI evaluation complete"
            
            for line in response_text.split('\n'):
                if 'SCORE:' in line:
                    try:
                        score = float(line.split('SCORE:')[1].strip())
                    except ValueError:
                        pass
                elif 'REASON:' in line:
                    reason = line.split('REASON:')[1].strip()
            
            return min(100, score), reason
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _classify_fit_level(self, score: float) -> str:
        """Convert a numeric score into a simple fit label."""
        if score >= 80:
            return 'Strong'
        if score >= 60:
            return 'Moderate'
        return 'Weak'

    def rank_resumes(self, job_description: str, resumes: List[Dict]) -> List[Dict]:
        """
        Rank all resumes against the job description.
        
        Args:
            job_description: The job description text
            resumes: List of resume dicts
            
        Returns:
            List of resumes with scores, ranked by score (highest first)
        """
        scored_resumes = []
        
        for resume in resumes:
            score, reasoning = self.score_resume(job_description, resume)
            scored_resumes.append({
                'name': resume['name'],
                'score': score,
                'reasoning': reasoning,
                'skills': resume['skills'],
                'education': resume['education'],
                'experience': resume['experience'],
                'confidence': round(min(100.0, max(0.0, score * 0.97)), 2),
                'fit_level': self._classify_fit_level(score)
            })
        
        # Sort by score descending
        scored_resumes.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_resumes
