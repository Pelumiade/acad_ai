import pytest
from apps.submissions.grading.mock_grader import MockGrader
from tests.factories.exam_factory import QuestionFactory


@pytest.mark.unit
@pytest.mark.django_db
class TestMockGrader:

    def test_mcq_correct_answer(self):
        grader = MockGrader()
        question = QuestionFactory(question_type="MCQ", correct_answer="B", marks=5)

        marks, feedback = grader.grade_answer(question, "B")

        assert marks == 5.0
        assert "Correct" in feedback

    def test_mcq_incorrect_answer(self):
        grader = MockGrader()
        question = QuestionFactory(question_type="MCQ", correct_answer="B", marks=5)

        marks, feedback = grader.grade_answer(question, "A")

        assert marks == 0.0
        assert "Incorrect" in feedback

    def test_short_answer_keyword_matching(self):
        grader = MockGrader()
        question = QuestionFactory(
            question_type="SHORT_ANSWER",
            correct_answer="Photosynthesis is the process by which plants convert light energy",
            marks=10,
            grading_rubric={
                "keywords": ["photosynthesis", "light", "energy", "plants"],
                "keyword_weight": 0.5,
                "similarity_weight": 0.5,
            },
        )

        answer = "Photosynthesis allows plants to use light energy to create glucose"
        marks, feedback = grader.grade_answer(question, answer)

        assert marks > 0
        assert marks <= 10
        assert "photosynthesis" in feedback.lower() or "keyword" in feedback.lower()

    def test_essay_grading_with_keywords(self):
        grader = MockGrader()
        question = QuestionFactory(
            question_type="ESSAY",
            marks=20,
            grading_rubric={"keywords": ["python", "function", "variable"], "min_length": 50},
        )

        answer = "Python is a programming language. Functions are reusable code blocks. Variables store data. " * 20
        marks, feedback = grader.grade_answer(question, answer)

        assert marks > 0
        assert marks <= 20

    def test_empty_answer(self):
        grader = MockGrader()
        question = QuestionFactory(question_type="MCQ", marks=5)

        marks, feedback = grader.grade_answer(question, "")

        assert marks == 0.0
        assert "No answer provided" in feedback
