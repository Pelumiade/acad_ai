import pytest
from apps.submissions.grading.grader_factory import GraderFactory
from apps.submissions.grading.mock_grader import MockGrader


@pytest.mark.unit
class TestGraderFactory:
    """Test grader factory implementation."""

    def test_create_mock_grader(self):
        grader = GraderFactory.create_grader("mock")
        assert isinstance(grader, MockGrader)

    def test_create_grader_default(self):
        from django.conf import settings
        from unittest.mock import patch
        # Ensure default falls back to mock if not configured
        with patch.object(settings, "GRADING_SERVICE", "mock"):
            grader = GraderFactory.create_grader()
            assert isinstance(grader, MockGrader)

    def test_create_llm_grader_without_config(self):
        from unittest.mock import patch
        # Without API key, should fallback to mock
        with patch.dict("os.environ", {"LLM_API_KEY": ""}):
            grader = GraderFactory.create_grader("llm")
            # Should fallback to MockGrader because LLMGrader.__init__ raises ValueError
            assert isinstance(grader, MockGrader)

    def test_create_grader_invalid_type(self):
        with pytest.raises(ValueError, match="Unknown grader type"):
            GraderFactory.create_grader("invalid_type")

    def test_register_custom_grader(self):
        from apps.submissions.grading.base_grader import BaseGrader

        class CustomGrader(BaseGrader):
            def grade_answer(self, question, answer_text, rubric=None):
                return 10.0, "Custom feedback"

            def grade_submission(self, submission):
                return {"total_score": 10.0, "percentage": 100}

        # Register custom grader
        GraderFactory.register_grader("custom", CustomGrader)

        # Verify it's registered in the dict
        assert "custom" in GraderFactory._graders

        # Test that we can get the class
        grader_class = GraderFactory._graders["custom"]
        grader = grader_class()
        assert isinstance(grader, CustomGrader)

        # Note: create_grader has hardcoded checks for 'mock' and 'llm'
        # Custom graders would need factory modification to work with create_grader
        # But registration mechanism works

        # Clean up
        GraderFactory._graders.pop("custom", None)
