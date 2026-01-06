from rest_framework.response import Response
from rest_framework import status
from typing import Any, Optional, Dict


class StandardResponseCodes:
    """Standard response codes for the assessment engine."""

    SUCCESS_GENERIC = "success"
    REGISTRATION_SUCCESSFUL = "registration_successful"
    LOGIN_SUCCESSFUL = "login_successful"
    LOGOUT_SUCCESSFUL = "logout_successful"
    PROFILE_RETRIEVED_SUCCESSFUL = "profile_retrieved_successful"

    EXAM_RETRIEVED_SUCCESSFUL = "exam_retrieved_successful"
    EXAMS_RETRIEVED_SUCCESSFUL = "exams_retrieved_successful"
    EXAM_CREATED_SUCCESSFUL = "exam_created_successful"
    COURSE_CREATED_SUCCESSFUL = "course_created_successful"
    SUBMISSION_CREATED_SUCCESSFUL = "submission_created_successful"
    SUBMISSION_RETRIEVED_SUCCESSFUL = "submission_retrieved_successful"
    SUBMISSIONS_RETRIEVED_SUCCESSFUL = "submissions_retrieved_successful"
    RESULTS_RETRIEVED_SUCCESSFUL = "results_retrieved_successful"

    ERROR_GENERIC = "error_generic"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    PERMISSION_ERROR = "permission_error"
    NOT_FOUND_ERROR = "not_found_error"
    SERVER_ERROR = "server_error"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    ACCOUNT_DEACTIVATED = "account_deactivated"
    FORBIDDEN = "forbidden"
    EXAM_NOT_FOUND = "exam_not_found"
    SUBMISSION_NOT_FOUND = "submission_not_found"
    DUPLICATE_SUBMISSION = "duplicate_submission"
    EXAM_NOT_AVAILABLE = "exam_not_available"
    EXAM_ENDED = "exam_ended"
    EXAM_NOT_STARTED = "exam_not_started"

    # Token refresh
    TOKEN_REFRESHED = "token_refreshed"
    TOKEN_REFRESH_FAILED = "token_refresh_failed"


class StandardResponseMessages:
    """Standard response messages for the assessment engine."""

    SUCCESS_GENERIC = "Operation completed successfully"
    REGISTRATION_SUCCESSFUL = "Registration successful"
    LOGIN_SUCCESSFUL = "Login successful"
    LOGOUT_SUCCESSFUL = "Logout successful"
    PROFILE_RETRIEVED_SUCCESSFUL = "Profile retrieved successfully"

    EXAM_RETRIEVED_SUCCESSFUL = "Exam details retrieved successfully"
    EXAMS_RETRIEVED_SUCCESSFUL = "Exams retrieved successfully"
    EXAM_CREATED_SUCCESSFUL = "Exam created successfully"
    COURSE_CREATED_SUCCESSFUL = "Course created successfully"
    SUBMISSION_CREATED_SUCCESSFUL = "Submission successful. Grading completed."
    SUBMISSION_RETRIEVED_SUCCESSFUL = "Submission retrieved successfully"
    SUBMISSIONS_RETRIEVED_SUCCESSFUL = "Submissions retrieved successfully"
    RESULTS_RETRIEVED_SUCCESSFUL = "Results retrieved successfully"

    ERROR_GENERIC = "An error occurred"
    VALIDATION_ERROR = "Validation failed"
    AUTHENTICATION_ERROR = "Authentication required"
    PERMISSION_ERROR = "Permission denied"
    NOT_FOUND_ERROR = "Resource not found"
    SERVER_ERROR = "Internal server error"
    INVALID_CREDENTIALS = "Invalid email or password"
    USER_NOT_FOUND = "User not found"
    ACCOUNT_DEACTIVATED = "Account has been deactivated"
    FORBIDDEN = "You do not have permission to access this resource"
    EXAM_NOT_FOUND = "Exam not found or not active"
    SUBMISSION_NOT_FOUND = "Submission not found"
    DUPLICATE_SUBMISSION = "You have already submitted this exam"
    EXAM_NOT_AVAILABLE = "Exam is not currently available"
    EXAM_ENDED = "Exam has ended"
    EXAM_NOT_STARTED = "Exam has not started yet"

    # Token refresh
    TOKEN_REFRESHED = "Token refreshed successfully"
    TOKEN_REFRESH_FAILED = "Token refresh failed"


def create_response_data(
    success: bool, message: str, response_code: str, data: Any = None, errors: Optional[Dict] = None
) -> Dict:
    """Create standardized response data structure."""
    response_data = {
        "success": success,
        "message": message,
        "code": response_code,
        "data": data if data is not None else [] if success else None,
    }
    if errors and not success:
        response_data["errors"] = errors
    return response_data


def success_response(
    data: Any = None,
    message: str = StandardResponseMessages.SUCCESS_GENERIC,
    response_code: str = StandardResponseCodes.SUCCESS_GENERIC,
    status_code: int = status.HTTP_200_OK,
) -> Response:
    """Create a success response."""
    response_data = create_response_data(success=True, message=message, response_code=response_code, data=data)
    return Response(response_data, status=status_code)


def error_response(
    message: str = StandardResponseMessages.ERROR_GENERIC,
    response_code: str = StandardResponseCodes.ERROR_GENERIC,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    errors: Optional[Dict] = None,
) -> Response:
    """Create an error response."""
    response_data = create_response_data(
        success=False, message=message, response_code=response_code, data=None, errors=errors
    )
    return Response(response_data, status=status_code)


def created_response(
    data: Any = None,
    message: str = StandardResponseMessages.SUCCESS_GENERIC,
    response_code: str = StandardResponseCodes.SUCCESS_GENERIC,
) -> Response:
    """Create a created response (201)."""
    return success_response(
        data=data, message=message, response_code=response_code, status_code=status.HTTP_201_CREATED
    )


def not_found_response(
    message: str = StandardResponseMessages.NOT_FOUND_ERROR, response_code: str = StandardResponseCodes.NOT_FOUND_ERROR
) -> Response:
    """Create a not found response (404)."""
    return error_response(message=message, response_code=response_code, status_code=status.HTTP_404_NOT_FOUND)


def validation_error_response(
    errors: Dict,
    message: str = StandardResponseMessages.VALIDATION_ERROR,
    response_code: str = StandardResponseCodes.VALIDATION_ERROR,
) -> Response:
    """Create a validation error response (400)."""
    return error_response(
        message=message, response_code=response_code, status_code=status.HTTP_400_BAD_REQUEST, errors=errors
    )


def server_error_response(
    message: str = StandardResponseMessages.SERVER_ERROR, response_code: str = StandardResponseCodes.SERVER_ERROR
) -> Response:
    """Create a server error response (500)."""
    return error_response(
        message=message, response_code=response_code, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def permission_denied_response(
    message: str = StandardResponseMessages.PERMISSION_ERROR,
    response_code: str = StandardResponseCodes.PERMISSION_ERROR,
) -> Response:
    """Create a permission denied response (403)."""
    return error_response(message=message, response_code=response_code, status_code=status.HTTP_403_FORBIDDEN)


def authentication_error_response(
    message: str = StandardResponseMessages.AUTHENTICATION_ERROR,
    response_code: str = StandardResponseCodes.AUTHENTICATION_ERROR,
) -> Response:
    """Create an authentication error response (401)."""
    return error_response(message=message, response_code=response_code, status_code=status.HTTP_401_UNAUTHORIZED)
