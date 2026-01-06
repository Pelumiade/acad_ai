import pytest
from rest_framework import status


@pytest.mark.integration
@pytest.mark.django_db
class TestExamAPI:

    def test_list_exams_authenticated(self, authenticated_client, sample_exam):
        url = "/exams/"

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "results" in response.data["data"]

    def test_get_exam_detail(self, authenticated_client, sample_exam):
        from tests.factories.exam_factory import QuestionFactory

        QuestionFactory(exam=sample_exam, order=1)
        QuestionFactory(exam=sample_exam, order=2)

        url = f"/exams/{sample_exam.uuid}/"

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "questions" in response.data["data"]

    def test_get_exam_detail_not_found(self, authenticated_client):
        url = "/exams/00000000-0000-0000-0000-000000000000/"

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False

    def test_list_exams_unauthenticated(self, api_client):
        url = "/exams/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
