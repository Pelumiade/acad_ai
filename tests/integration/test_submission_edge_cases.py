import pytest
from django.utils import timezone
from rest_framework import status
from tests.factories.exam_factory import ExamFactory, QuestionFactory


@pytest.mark.integration
@pytest.mark.django_db
class TestSubmissionEdgeCases:
    def test_create_submission_exam_not_started(self, authenticated_client, student_user):
        from tests.factories.exam_factory import CourseFactory

        instructor = student_user.__class__.objects.create_user(
            email="instructor@example.com",
            password="testpass123",
            first_name="Instructor",
            last_name="User",
            role="INSTRUCTOR",
        )
        course = CourseFactory(instructor=instructor)
        exam = ExamFactory(
            course=course,
            start_time=timezone.now() + timezone.timedelta(hours=1),
            end_time=timezone.now() + timezone.timedelta(hours=2),
        )
        question = QuestionFactory(exam=exam, order=1)

        url = "/submissions/"
        data = {
            "exam_uuid": str(exam.uuid),
            "answers": [{"question_uuid": str(question.uuid), "answer_text": "Answer"}],
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_submission_exam_ended(self, authenticated_client, student_user):
        from tests.factories.exam_factory import CourseFactory

        instructor = student_user.__class__.objects.create_user(
            email="instructor2@example.com",
            password="testpass123",
            first_name="Instructor2",
            last_name="User",
            role="INSTRUCTOR",
        )
        course = CourseFactory(instructor=instructor)
        exam = ExamFactory(
            course=course,
            start_time=timezone.now() - timezone.timedelta(hours=2),
            end_time=timezone.now() - timezone.timedelta(hours=1),
        )
        question = QuestionFactory(exam=exam, order=1)

        url = "/submissions/"
        data = {
            "exam_uuid": str(exam.uuid),
            "answers": [{"question_uuid": str(question.uuid), "answer_text": "Answer"}],
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_create_submission_missing_answers(self, authenticated_client, sample_exam):
        from tests.factories.exam_factory import QuestionFactory

        question1 = QuestionFactory(exam=sample_exam, order=1)
        QuestionFactory(exam=sample_exam, order=2)

        url = "/submissions/"
        data = {
            "exam_uuid": str(sample_exam.uuid),
            "answers": [
                {"question_uuid": str(question1.uuid), "answer_text": "Answer"}
                # Missing answer for question2
            ],
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
