import pytest
from rest_framework import status
from tests.factories.submission_factory import SubmissionFactory


@pytest.mark.integration
@pytest.mark.django_db
class TestPermissions:
    def test_student_cannot_view_others_submission(self, authenticated_client, student_user):
        from tests.factories.user_factory import UserFactory

        other_student = UserFactory(role="STUDENT")
        other_submission = SubmissionFactory(student=other_student)

        url = f"/submissions/{other_submission.uuid}/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_unauthenticated_cannot_access_submissions(self, api_client):
        url = "/submissions/"

        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_student_can_view_own_submission(self, authenticated_client, student_user):
        submission = SubmissionFactory(student=student_user)

        url = f"/submissions/{submission.uuid}/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_student_can_view_own_results(self, authenticated_client, student_user):
        from decimal import Decimal

        submission = SubmissionFactory(student=student_user, status="COMPLETED")
        submission.score = Decimal("85.0")
        submission.save()

        url = f"/submissions/{submission.uuid}/"
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
