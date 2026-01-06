import re
from typing import Tuple, Dict, List
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.utils import timezone
from .base_grader import BaseGrader


class MockGrader(BaseGrader):

    def __init__(self):
        self.vectorizer = TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))

    def grade_answer(self, question: "Question", answer_text: str, rubric: Dict = None) -> Tuple[float, str]:

        if not self._validate_answer(answer_text):
            return 0.0, "No answer provided"

        question_type = question.question_type

        if question_type == "MCQ":
            return self._grade_mcq(question, answer_text)
        elif question_type == "SHORT_ANSWER":
            return self._grade_short_answer(question, answer_text, rubric)
        elif question_type == "ESSAY":
            return self._grade_essay(question, answer_text, rubric)
        else:
            return 0.0, "Unknown question type"

    def _grade_mcq(self, question, answer_text: str) -> Tuple[float, str]:
        expected = question.correct_answer.strip()
        provided = answer_text.strip()

        if question.case_sensitive:
            is_correct = expected == provided
        else:
            is_correct = expected.lower() == provided.lower()

        if is_correct:
            return float(question.marks), "Correct answer"
        else:
            return 0.0, f"Incorrect. Expected: {expected}"

    def _grade_short_answer(self, question, answer_text: str, rubric: Dict = None) -> Tuple[float, str]:

        rubric = rubric or question.grading_rubric or {}
        expected = question.correct_answer

        if not expected:
            return float(question.marks), "Manual grading required"

        # Extract keywords from rubric or expected answer
        keywords = rubric.get("keywords", [])
        if not keywords:
            keywords = self._extract_keywords(expected)

        # Calculate keyword score
        keyword_score = self._calculate_keyword_score(answer_text, keywords, weight=rubric.get("keyword_weight", 0.4))

        # Calculate similarity score
        similarity_score = self._calculate_similarity_score(
            answer_text, expected, weight=rubric.get("similarity_weight", 0.6)
        )

        # Combined score
        total_score = keyword_score + similarity_score
        marks_obtained = total_score * float(question.marks)

        # Generate feedback
        feedback = self._generate_feedback(total_score, keyword_score, similarity_score, keywords, answer_text)

        return round(marks_obtained, 2), feedback

    def _grade_essay(self, question, answer_text: str, rubric: Dict = None) -> Tuple[float, str]:

        rubric = rubric or question.grading_rubric or {}

        # Check minimum length requirement
        min_length = rubric.get("min_length", 100)
        word_count = len(answer_text.split())

        if word_count < min_length:
            penalty = 0.3  # 30% penalty
            feedback = f"Answer too short ({word_count} words, minimum {min_length})"
        else:
            penalty = 0
            feedback = "Length requirement met. "

        # Keyword-based scoring
        keywords = rubric.get("keywords", [])
        if keywords:
            keyword_score = self._calculate_keyword_score(answer_text, keywords, weight=1.0)

            marks_obtained = keyword_score * float(question.marks) * (1 - penalty)

            matched_keywords = self._find_matched_keywords(answer_text, keywords)
            feedback += f"Covered {len(matched_keywords)}/{len(keywords)} key concepts: {', '.join(matched_keywords)}"
        else:
            # No rubric - give full marks with note
            marks_obtained = float(question.marks)
            feedback = "Manual grading recommended - no rubric provided"

        return round(marks_obtained, 2), feedback

    def _calculate_keyword_score(self, text: str, keywords: List[str], weight: float) -> float:
        """Calculate score based on keyword presence and density."""
        if not keywords:
            return 0.0

        text_lower = text.lower()
        matched_keywords = [kw for kw in keywords if kw.lower() in text_lower]

        # Basic presence score
        presence_score = len(matched_keywords) / len(keywords)

        # Keyword density bonus
        total_words = len(text.split())
        keyword_density = sum(text_lower.count(kw.lower()) for kw in matched_keywords) / max(total_words, 1)

        # Combined score with diminishing returns on density
        combined = (presence_score * 0.8) + min(keyword_density * 5, 0.2)

        return combined * weight

    def _calculate_similarity_score(self, text1: str, text2: str, weight: float) -> float:
        """Calculate cosine similarity using TF-IDF."""
        try:
            # Vectorize texts
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])

            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return similarity * weight
        except Exception:
            # Fallback to simple word overlap
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            overlap = len(words1 & words2) / max(len(words1 | words2), 1)
            return overlap * weight

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text."""
        # Simple extraction - remove common words
        words = re.findall(r"\b[a-z]{4,}\b", text.lower())
        # Return unique words
        return list(set(words))[:10]

    def _find_matched_keywords(self, text: str, keywords: List[str]) -> List[str]:
        """Find which keywords are present in text."""
        text_lower = text.lower()
        return [kw for kw in keywords if kw.lower() in text_lower]

    def _generate_feedback(
        self, total_score: float, keyword_score: float, similarity_score: float, keywords: List[str], answer_text: str
    ) -> str:
        """Generate detailed feedback."""
        matched = self._find_matched_keywords(answer_text, keywords)
        missing = [kw for kw in keywords if kw not in matched]

        feedback_parts = [
            f"Overall Score: {total_score:.1%}",
            f"Keyword Coverage: {keyword_score:.1%}",
            f"Content Similarity: {similarity_score:.1%}",
        ]

        if matched:
            feedback_parts.append(f"Mentioned: {', '.join(matched)}")
        if missing:
            feedback_parts.append(f"Consider including: {', '.join(missing)}")

        return " | ".join(feedback_parts)

    def grade_submission(self, submission: "Submission") -> Dict:
        """Grade all answers in a submission."""
        from apps.submissions.models import Answer

        total_marks_obtained = 0.0
        total_possible_marks = 0.0
        grading_details = []

        answers = submission.answers.select_related("question").all()

        for answer in answers:
            question = answer.question
            marks, feedback = self.grade_answer(question, answer.answer_text, question.grading_rubric)

            # Update answer object
            answer.marks_obtained = marks
            answer.feedback = feedback
            answer.is_correct = marks >= float(question.marks)
            answer.graded_by_service = "mock"
            answer.graded_at = timezone.now()
            answer.save()

            total_marks_obtained += marks
            total_possible_marks += float(question.marks)

            grading_details.append(
                {
                    "question_uuid": str(question.uuid),
                    "marks_obtained": marks,
                    "marks_possible": float(question.marks),
                    "feedback": feedback,
                }
            )

        return {
            "total_score": total_marks_obtained,
            "total_possible": total_possible_marks,
            "percentage": (total_marks_obtained / total_possible_marks * 100) if total_possible_marks > 0 else 0,
            "details": grading_details,
        }
