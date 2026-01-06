from django.conf import settings
from .base_grader import BaseGrader
from .mock_grader import MockGrader


class GraderFactory:
    _graders = {
        "mock": MockGrader,
    }

    @classmethod
    def create_grader(cls, grader_type: str = None) -> BaseGrader:

        if grader_type is None:
            grader_type = getattr(settings, "GRADING_SERVICE", "mock")

        grader_type = grader_type.lower()

        if grader_type == "mock":
            return MockGrader()
        elif grader_type == "llm":
            try:
                from .llm_grader import LLMGrader

                return LLMGrader()
            except (ImportError, ValueError) as e:
                # Fallback to mock if LLM is not properly configured
                import logging

                logger = logging.getLogger("apps")
                logger.warning(f"LLM grader not available: {str(e)}. Falling back to mock grader.")
                return MockGrader()
        else:
            raise ValueError(f"Unknown grader type: {grader_type}. Supported types: 'mock', 'llm'")

    @classmethod
    def register_grader(cls, name: str, grader_class: type):

        if not issubclass(grader_class, BaseGrader):
            raise TypeError("Grader must inherit from BaseGrader")

        cls._graders[name.lower()] = grader_class
