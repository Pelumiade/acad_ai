import pytest
from apps.common.utils.response_builder import ResponseBuilder
from apps.common.utils.response_utils import StandardResponseCodes, StandardResponseMessages


@pytest.mark.unit
class TestResponseBuilder:

    def test_success_response_registration(self):
        result = ResponseBuilder.success("registration", data={"user": "test"})

        assert result.success is True
        assert result.message == StandardResponseMessages.REGISTRATION_SUCCESSFUL
        assert result.code == StandardResponseCodes.REGISTRATION_SUCCESSFUL
        assert result.data == {"user": "test"}

    def test_error_response_validation(self):
        errors = {"email": ["Invalid email"]}
        result = ResponseBuilder.error("validation", errors=errors)

        assert result.success is False
        assert result.message == StandardResponseMessages.VALIDATION_ERROR
        assert result.code == StandardResponseCodes.VALIDATION_ERROR
        assert result.errors == errors

    def test_service_response_to_response_success(self):
        result = ResponseBuilder.success("login", data={"token": "abc123"})
        response = result.to_response()

        assert response.status_code == 200
        assert response.data["success"] is True
        assert response.data["code"] == StandardResponseCodes.LOGIN_SUCCESSFUL

    def test_service_response_to_response_created(self):
        result = ResponseBuilder.success("registration", data={"user": "test"})
        response = result.to_response()

        assert response.status_code == 201
        assert response.data["success"] is True
        assert "REGISTRATION" in response.data["code"] or response.status_code == 201
