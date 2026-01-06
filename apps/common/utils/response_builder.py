from .response_utils import (
    StandardResponseMessages,
    StandardResponseCodes,
    success_response,
    error_response,
    created_response,
    validation_error_response,
    authentication_error_response,
    not_found_response,
    permission_denied_response,
)


class ServiceResponse:
    """Universal service response class for all services"""

    def __init__(self, success: bool, message: str, code: str, data=None, errors=None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data
        self.errors = errors

    def to_response(self, status_code=None):
        """Convert to HTTP response - handles all conditional logic automatically"""
        if self.success:
            # Check for created responses (201 status) - case insensitive
            code_upper = self.code.upper()
            created_patterns = ["REGISTRATION", "CREATED", "SUBMISSION_CREATED"]
            if any(pattern in code_upper for pattern in created_patterns):
                return created_response(data=self.data, message=self.message, response_code=self.code)
            return success_response(data=self.data, message=self.message, response_code=self.code)

        if self.code == StandardResponseCodes.VALIDATION_ERROR:
            return validation_error_response(errors=self.errors or {}, message=self.message, response_code=self.code)

        if self.code in [StandardResponseCodes.AUTHENTICATION_ERROR, StandardResponseCodes.INVALID_CREDENTIALS]:
            return authentication_error_response(message=self.message, response_code=self.code)

        if self.code == StandardResponseCodes.PERMISSION_ERROR or self.code == StandardResponseCodes.FORBIDDEN:
            return permission_denied_response(message=self.message, response_code=self.code)

        if self.code == StandardResponseCodes.NOT_FOUND_ERROR or "NOT_FOUND" in self.code.upper():
            return not_found_response(message=self.message, response_code=self.code)

        # Handle duplicate submission with 409 status
        if self.code == StandardResponseCodes.DUPLICATE_SUBMISSION:
            return error_response(message=self.message, response_code=self.code, status_code=409)

        # Use custom status code if provided, otherwise use default
        if status_code:
            return error_response(message=self.message, response_code=self.code, status_code=status_code)

        return error_response(message=self.message, response_code=self.code)


class ResponseBuilder:
    """Builder for creating standardized service responses."""

    @staticmethod
    def success(response_type: str, data=None):
        """Build success response using constants from response_utils.py"""
        type_mapping = {
            "registration": (
                StandardResponseMessages.REGISTRATION_SUCCESSFUL,
                StandardResponseCodes.REGISTRATION_SUCCESSFUL,
            ),
            "login": (StandardResponseMessages.LOGIN_SUCCESSFUL, StandardResponseCodes.LOGIN_SUCCESSFUL),
            "logout": (StandardResponseMessages.LOGOUT_SUCCESSFUL, StandardResponseCodes.LOGOUT_SUCCESSFUL),
            "profile_retrieved": (
                StandardResponseMessages.PROFILE_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.PROFILE_RETRIEVED_SUCCESSFUL,
            ),
            "exam_retrieved": (
                StandardResponseMessages.EXAM_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.EXAM_RETRIEVED_SUCCESSFUL,
            ),
            "exams_retrieved": (
                StandardResponseMessages.EXAMS_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.EXAMS_RETRIEVED_SUCCESSFUL,
            ),
            "exam_created": (
                StandardResponseMessages.EXAM_CREATED_SUCCESSFUL,
                StandardResponseCodes.EXAM_CREATED_SUCCESSFUL,
            ),
            "course_created": (
                StandardResponseMessages.COURSE_CREATED_SUCCESSFUL,
                StandardResponseCodes.COURSE_CREATED_SUCCESSFUL,
            ),
            "submission_created": (
                StandardResponseMessages.SUBMISSION_CREATED_SUCCESSFUL,
                StandardResponseCodes.SUBMISSION_CREATED_SUCCESSFUL,
            ),
            "submission_retrieved": (
                StandardResponseMessages.SUBMISSION_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.SUBMISSION_RETRIEVED_SUCCESSFUL,
            ),
            "submissions_retrieved": (
                StandardResponseMessages.SUBMISSIONS_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.SUBMISSIONS_RETRIEVED_SUCCESSFUL,
            ),
            "results_retrieved": (
                StandardResponseMessages.RESULTS_RETRIEVED_SUCCESSFUL,
                StandardResponseCodes.RESULTS_RETRIEVED_SUCCESSFUL,
            ),
            "token_refreshed": (StandardResponseMessages.TOKEN_REFRESHED, StandardResponseCodes.TOKEN_REFRESHED),
        }
        message, code = type_mapping.get(
            response_type, (StandardResponseMessages.SUCCESS_GENERIC, StandardResponseCodes.SUCCESS_GENERIC)
        )
        return ServiceResponse(success=True, message=message, code=code, data=data)

    @staticmethod
    def error(response_type: str, errors=None):
        """Build error response using constants from response_utils.py"""
        type_mapping = {
            "validation": (StandardResponseMessages.VALIDATION_ERROR, StandardResponseCodes.VALIDATION_ERROR),
            "authentication": (
                StandardResponseMessages.AUTHENTICATION_ERROR,
                StandardResponseCodes.AUTHENTICATION_ERROR,
            ),
            "invalid_credentials": (
                StandardResponseMessages.INVALID_CREDENTIALS,
                StandardResponseCodes.INVALID_CREDENTIALS,
            ),
            "permission_denied": (StandardResponseMessages.PERMISSION_ERROR, StandardResponseCodes.PERMISSION_ERROR),
            "not_found": (StandardResponseMessages.NOT_FOUND_ERROR, StandardResponseCodes.NOT_FOUND_ERROR),
            "server_error": (StandardResponseMessages.SERVER_ERROR, StandardResponseCodes.SERVER_ERROR),
            "user_not_found": (StandardResponseMessages.USER_NOT_FOUND, StandardResponseCodes.USER_NOT_FOUND),
            "account_deactivated": (
                StandardResponseMessages.ACCOUNT_DEACTIVATED,
                StandardResponseCodes.ACCOUNT_DEACTIVATED,
            ),
            "forbidden": (StandardResponseMessages.FORBIDDEN, StandardResponseCodes.FORBIDDEN),
            "exam_not_found": (StandardResponseMessages.EXAM_NOT_FOUND, StandardResponseCodes.EXAM_NOT_FOUND),
            "submission_not_found": (
                StandardResponseMessages.SUBMISSION_NOT_FOUND,
                StandardResponseCodes.SUBMISSION_NOT_FOUND,
            ),
            "duplicate_submission": (
                StandardResponseMessages.DUPLICATE_SUBMISSION,
                StandardResponseCodes.DUPLICATE_SUBMISSION,
            ),
            "exam_not_available": (
                StandardResponseMessages.EXAM_NOT_AVAILABLE,
                StandardResponseCodes.EXAM_NOT_AVAILABLE,
            ),
            "exam_ended": (StandardResponseMessages.EXAM_ENDED, StandardResponseCodes.EXAM_ENDED),
            "exam_not_started": (StandardResponseMessages.EXAM_NOT_STARTED, StandardResponseCodes.EXAM_NOT_STARTED),
            "token_refresh_failed": (
                StandardResponseMessages.TOKEN_REFRESH_FAILED,
                StandardResponseCodes.TOKEN_REFRESH_FAILED,
            ),
        }
        message, code = type_mapping.get(
            response_type, (StandardResponseMessages.ERROR_GENERIC, StandardResponseCodes.ERROR_GENERIC)
        )
        return ServiceResponse(success=False, message=message, code=code, errors=errors)

    @staticmethod
    def custom_response(success: bool, message: str, code: str, data=None, errors=None):
        """Custom response when standard types don't fit exactly"""
        return ServiceResponse(success=success, message=message, code=code, data=data, errors=errors)
