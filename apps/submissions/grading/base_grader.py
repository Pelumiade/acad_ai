from abc import ABC, abstractmethod
from typing import Tuple, Dict


class BaseGrader(ABC):
    @abstractmethod
    def grade_answer(self, question: "Question", answer_text: str, rubric: Dict = None) -> Tuple[float, str]:
        pass

    @abstractmethod
    def grade_submission(self, submission: "Submission") -> Dict:
        pass

    def _validate_answer(self, answer_text: str) -> bool:
        return bool(answer_text and answer_text.strip())
