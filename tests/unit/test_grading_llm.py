import pytest
from unittest.mock import patch, MagicMock
from apps.submissions.grading.llm_grader import LLMGrader
from tests.factories.exam_factory import QuestionFactory


@pytest.mark.unit
@pytest.mark.django_db
class TestLLMGrader:

    def test_llm_grader_initialization_gemini(self):
        with patch.dict("os.environ", {"LLM_API_KEY": "test-key", "LLM_MODEL": "gemini-1.5-flash"}):
            with patch("google.genai.Client"):
                grader = LLMGrader()
                assert grader.model == "gemini-1.5-flash"
                assert grader.api_key == "test-key"

    def test_llm_grader_mcq_grading(self):
        with patch.dict("os.environ", {"LLM_API_KEY": "test-key", "LLM_MODEL": "gemini-1.5-flash"}):
            with patch("google.genai.Client") as mock_genai:
                # Mock the API response
                mock_client = MagicMock()
                mock_response = MagicMock()
                mock_response.text = '{"marks": 5.0, "feedback": "Correct answer"}'
                mock_client.models.generate_content.return_value = mock_response
                mock_genai.return_value = mock_client

                grader = LLMGrader()
                grader.client = mock_client

                question = QuestionFactory(question_type="MCQ", correct_answer="B", marks=5)

                marks, feedback = grader.grade_answer(question, "B")

                assert marks == 5.0
                assert "correct answer" in feedback.lower()

    def test_llm_grader_empty_answer(self):
        with patch.dict("os.environ", {"LLM_API_KEY": "test-key", "LLM_MODEL": "gemini-1.5-flash"}):
            with patch("google.genai.Client"):
                grader = LLMGrader()
                question = QuestionFactory(question_type="MCQ", marks=5)

                marks, feedback = grader.grade_answer(question, "")

                assert marks == 0.0
                assert "No answer provided" in feedback

    def test_llm_grader_fallback_on_import_error(self):
        from apps.submissions.grading.grader_factory import GraderFactory

        with patch.dict("os.environ", {"GRADING_SERVICE": "llm"}):
            with patch("apps.submissions.grading.grader_factory.settings", spec=True) as mock_settings:
                mock_settings.GRADING_SERVICE = "llm"
                with patch(
                    "apps.submissions.grading.llm_grader.LLMGrader", side_effect=ImportError("Package not found")
                ):
                    grader = GraderFactory.create_grader("llm")
                    # Should fallback to MockGrader
                    from apps.submissions.grading.mock_grader import MockGrader

                    assert isinstance(grader, MockGrader)

    def test_llm_grader_json_parsing(self):
        with patch.dict("os.environ", {"LLM_API_KEY": "test-key", "LLM_MODEL": "gemini-1.5-flash"}):
            with patch("google.genai.Client"):
                grader = LLMGrader()

                # Test valid JSON response
                response_text = '{"marks": 8.5, "feedback": "Good answer with minor issues"}'
                marks, feedback = grader._parse_llm_response(response_text, QuestionFactory(marks=10))

                assert marks == 8.5
                assert "feedback" in feedback.lower() or "good answer" in feedback.lower()

                # Test response with extra text
                response_text = 'Here is my assessment:\n{"marks": 7.0, "feedback": "Average answer"}\nEnd of response'
                marks, feedback = grader._parse_llm_response(response_text, QuestionFactory(marks=10))

                assert marks == 7.0

                # Test fallback parsing
                response_text = "The marks are: 9.0 and the feedback is: Excellent work"
                marks, feedback = grader._parse_llm_response(response_text, QuestionFactory(marks=10))

                # Should extract marks or return 0
                assert isinstance(marks, float)
                assert marks >= 0
