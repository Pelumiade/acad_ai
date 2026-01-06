from rest_framework import status
from rest_framework.exceptions import APIException


class ValidationError(APIException):
    """Custom validation error."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Validation failed"
    default_code = "validation_error"


class BusinessRuleError(APIException):
    """Business rule violation error."""

    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Business rule violation"
    default_code = "business_rule_error"
