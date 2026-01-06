import pytest
from rest_framework import status


@pytest.mark.integration
@pytest.mark.django_db
class TestAuthAPI:

    def test_register_user_success(self, api_client):
        url = "/auth/register/"
        data = {
            "email": "newuser@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        assert "user" in response.data["data"]

    def test_register_user_duplicate_email(self, api_client, student_user):
        url = "/auth/register/"
        data = {
            "email": student_user.email,
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_login_success(self, api_client, student_user):
        url = "/auth/login/"
        data = {"email": student_user.email, "password": "testpass123"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        assert "user" in response.data["data"]

    def test_login_invalid_credentials(self, api_client):
        url = "/auth/login/"
        data = {"email": "nonexistent@example.com", "password": "wrongpass"}

        response = api_client.post(url, data, format="json")

        # The service returns 400 for validation or 401 for invalid credentials
        assert response.status_code in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED]
        assert response.data["success"] is False

    def test_logout_success(self, authenticated_client):
        url = "/auth/logout/"

        response = authenticated_client.post(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True

    def test_get_profile_authenticated(self, authenticated_client, student_user):
        url = "/auth/profile/"

        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["user"]["email"] == student_user.email

    def test_refresh_token_success(self, api_client, student_user):

        # First login to get refresh token
        login_url = "/auth/login/"
        login_data = {"email": student_user.email, "password": "testpass123"}
        login_response = api_client.post(login_url, login_data, format="json")
        refresh_token = login_response.data["data"]["refresh"]

        # Now refresh the token
        url = "/auth/refresh-token/"
        refresh_data = {"refresh_token": refresh_token}

        response = api_client.post(url, refresh_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]
        # Refresh token should be rotated
        assert response.data["data"]["refresh"] != refresh_token

    def test_refresh_token_invalid(self, api_client):
        url = "/auth/refresh-token/"
        refresh_data = {"refresh_token": "invalid-token"}

        response = api_client.post(url, refresh_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_refresh_token_missing(self, api_client):
        url = "/auth/refresh-token/"

        response = api_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_register_email_validation_case_insensitive(self, api_client, student_user):
        url = "/auth/register/"
        # Try to register with same email but different case
        data = {
            "email": student_user.email.upper(),
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_register_email_validation_whitespace(self, api_client):
        url = "/auth/register/"
        data = {
            "email": "  test@example.com  ",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "John",
            "last_name": "Doe",
        }

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["data"]["user"]["email"] == "test@example.com"
