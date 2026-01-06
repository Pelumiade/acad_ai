import os
import json
import re
import logging
from typing import Tuple, Dict
from decimal import Decimal
from .base_grader import BaseGrader

logger = logging.getLogger("apps")


class LLMGrader(BaseGrader):

    def __init__(self):
        self.api_key = os.environ.get("LLM_API_KEY", "")
        if not self.api_key:
            raise ValueError("LLM_API_KEY is not configured")
        self.model = os.environ.get("LLM_MODEL", "gemini-1.5-flash")
        self.model_name = self.model
        self.client = None

        # Initialize client based on model type
        if "claude" in self.model.lower():
            try:
                import anthropic

                self.client = anthropic.Anthropic(api_key=self.api_key)
                self.grade_method = self._grade_with_claude
            except ImportError:
                logger.warning("anthropic package not installed. Install with: pip install anthropic")
                raise ImportError("anthropic package required for Claude grading")
        elif "gpt" in self.model.lower():
            try:
                import openai

                self.client = openai.OpenAI(api_key=self.api_key)
                self.grade_method = self._grade_with_openai
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")
                raise ImportError("openai package required for GPT grading")
        elif "gemini" in self.model.lower():
            try:
                import google.genai as genai

                self.client = genai.Client(api_key=self.api_key)
                self.grade_method = self._grade_with_gemini
            except ImportError:
                logger.warning("google-genai package not installed. Install with: pip install google-genai")
                raise ImportError("google-genai package required for Gemini grading")
        else:
            raise ValueError(f"Unsupported LLM model: {self.model}")

    def _validate_answer(self, answer_text: str) -> bool:
        """Common validation logic."""
        return bool(answer_text and answer_text.strip())

    def grade_answer(self, question, answer_text: str, rubric: Dict = None) -> Tuple[float, str]:
        """
        Grade a single answer using LLM.

        Args:
            question: Question object with expected answer and rubric
            answer_text: Student's submitted answer
            rubric: Optional grading rubric override

        Returns:
            Tuple of (marks_obtained, feedback_text)
        """
        if not self._validate_answer(answer_text):
            return 0.0, "No answer provided"

        try:
            prompt = self._build_grading_prompt(question, answer_text, rubric or question.grading_rubric)
            marks, feedback = self.grade_method(prompt, question)

            # Ensure marks don't exceed question marks
            marks = min(float(marks), float(question.marks))

            return round(marks, 2), feedback
        except Exception as e:
            logger.error(f"LLM grading error: {str(e)}")
            return 0.0, f"Grading service error: {str(e)}"

    def _build_grading_prompt(self, question, answer_text: str, rubric: Dict = None) -> str:
        """Construct prompt for LLM."""
        prompt = f"""You are an expert academic grader. Grade the following student answer.

Question Type: {question.question_type}
Question: {question.question_text}
Maximum Marks: {float(question.marks)}

"""

        if question.correct_answer:
            prompt += f"Expected Answer (for reference): {question.correct_answer}\n\n"

        if rubric:
            prompt += f"Grading Rubric: {json.dumps(rubric, indent=2)}\n\n"

        prompt += f"""Student Answer: {answer_text}

Provide your response in JSON format:
{{
    "marks": <float between 0 and {float(question.marks)}>,
    "feedback": "<detailed feedback string explaining the grade>"
}}

Be fair but rigorous. Consider:
- Accuracy and correctness
- Completeness of the answer
- Understanding demonstrated
- For essay questions, consider structure, clarity, and depth
"""

        return prompt

    def _grade_with_claude(self, prompt: str, question) -> Tuple[float, str]:
        """Grade using Anthropic Claude."""
        try:
            response = self.client.messages.create(
                model=self.model, max_tokens=1000, messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            return self._parse_llm_response(response_text, question)
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise

    def _grade_with_openai(self, prompt: str, question) -> Tuple[float, str]:
        """Grade using OpenAI GPT."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert academic grader. Always respond with valid JSON."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            response_text = response.choices[0].message.content
            return self._parse_llm_response(response_text, question)
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

    def _grade_with_gemini(self, prompt: str, question) -> Tuple[float, str]:
        """Grade using Google Gemini (new google.genai SDK)."""
        try:
            # Use the new unified SDK API
            response = self.client.models.generate_content(model=self.model_name, contents=prompt)
            # New API returns response with .text attribute
            response_text = response.text
            return self._parse_llm_response(response_text, question)
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise

    def _parse_llm_response(self, response_text: str, question) -> Tuple[float, str]:
        """Extract marks and feedback from LLM response."""
        try:
            # Try to find JSON in response
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                marks = float(result.get("marks", 0))
                feedback = result.get("feedback", "No feedback provided")

                # Validate marks range
                marks = max(0, min(marks, float(question.marks)))

                return marks, feedback
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            logger.warning(f"Failed to parse LLM response as JSON: {str(e)}")

        # Fallback parsing - try to extract marks from text
        marks_match = re.search(r'marks?["\']?\s*[:=]\s*([\d.]+)', response_text, re.IGNORECASE)
        if marks_match:
            try:
                marks = float(marks_match.group(1))
                marks = max(0, min(marks, float(question.marks)))
                feedback = response_text[:500] if len(response_text) > 500 else response_text
                return marks, feedback
            except ValueError:
                pass

        # Final fallback
        return 0.0, response_text[:500] if len(response_text) > 500 else response_text

    def grade_submission(self, submission) -> Dict:
        """
        Grade all answers in a submission using LLM.

        Args:
            submission: Submission object with answers

        Returns:
            Dictionary with total score and grading details
        """
        from apps.submissions.models import Answer
        from django.utils import timezone

        total_marks_obtained = Decimal("0.0")
        total_possible_marks = Decimal("0.0")
        grading_details = []

        answers = submission.answers.select_related("question").all()

        for answer in answers:
            question = answer.question

            try:
                marks, feedback = self.grade_answer(question, answer.answer_text, question.grading_rubric)

                # Update answer object
                answer.marks_obtained = Decimal(str(marks))
                answer.feedback = feedback
                answer.is_correct = marks >= float(question.marks) * 0.8  # 80% threshold for correctness
                answer.graded_by_service = "llm"
                answer.graded_at = timezone.now()
                answer.save()

                total_marks_obtained += Decimal(str(marks))
                total_possible_marks += question.marks

                grading_details.append(
                    {
                        "question_uuid": str(question.uuid),
                        "marks_obtained": float(marks),
                        "marks_possible": float(question.marks),
                        "feedback": feedback,
                    }
                )
            except Exception as e:
                logger.error(f"Error grading answer {answer.uuid}: {str(e)}")
                # Mark as failed but continue
                answer.graded_by_service = "llm"
                answer.marks_obtained = Decimal("0.0")
                answer.feedback = f"Grading failed: {str(e)}"
                answer.save()

                total_possible_marks += question.marks
                grading_details.append(
                    {
                        "question_uuid": str(question.uuid),
                        "marks_obtained": 0.0,
                        "marks_possible": float(question.marks),
                        "feedback": f"Grading failed: {str(e)}",
                    }
                )

        percentage = (total_marks_obtained / total_possible_marks * 100) if total_possible_marks > 0 else 0

        return {
            "total_score": float(total_marks_obtained),
            "total_possible": float(total_possible_marks),
            "percentage": float(percentage),
            "details": grading_details,
        }
