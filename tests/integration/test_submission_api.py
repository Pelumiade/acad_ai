import pytest
from rest_framework import status
from apps.submissions.models import Submission


@pytest.mark.integration
@pytest.mark.django_db
class TestSubmissionAPI:
    def test_create_submission_success(self, authenticated_client, sample_exam, student_user):
        # Create questions for the exam
        from tests.factories.exam_factory import QuestionFactory

        question1 = QuestionFactory(exam=sample_exam, order=1, question_type="MCQ")
        question2 = QuestionFactory(exam=sample_exam, order=2, question_type="SHORT_ANSWER")

        url = "/submissions/"
        data = {
            "exam_uuid": str(sample_exam.uuid),
            "answers": [
                {"question_uuid": str(question1.uuid), "answer_text": "B"},
                {"question_uuid": str(question2.uuid), "answer_text": "Sample answer text"},
            ],
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "submission" in response.data["data"]

        # Verify submission was created
        assert Submission.objects.filter(exam=sample_exam, student=student_user).exists()

    def test_create_submission_duplicate_fails(self, authenticated_client, sample_exam, student_user):
        from tests.factories.exam_factory import QuestionFactory
        from tests.factories.submission_factory import SubmissionFactory

        question = QuestionFactory(exam=sample_exam, order=1)

        # Create first submission
        SubmissionFactory(student=student_user, exam=sample_exam)

        url = "/submissions/"
        data = {
            "exam_uuid": str(sample_exam.uuid),
            "answers": [{"question_uuid": str(question.uuid), "answer_text": "Answer"}],
        }

        response = authenticated_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.data["success"] is False

    def test_list_submissions(self, authenticated_client, student_user):
        from tests.factories.submission_factory import SubmissionFactory

        SubmissionFactory(student=student_user)

        url = "/submissions/list/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert len(response.data["data"]["results"]) >= 1

    def test_get_submission_detail(self, authenticated_client, student_user):
        from tests.factories.submission_factory import SubmissionFactory

        submission = SubmissionFactory(student=student_user, status="COMPLETED")

        url = f"/submissions/{submission.uuid}/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

