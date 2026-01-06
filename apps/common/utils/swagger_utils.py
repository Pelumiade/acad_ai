from drf_spectacular.utils import OpenApiParameter, OpenApiExample
from typing import Dict, Any

def wrap_responses_hook(result, generator, request, public):
    """
    Hook to wrap all success responses in the standardized envelope:
    {
        "success": true,
        "message": "string",
        "code": "string",
        "data": { ... original schema ... }
    }
    """
    if 'paths' not in result:
        return result

    # Define standard error responses to inject if missing
    standard_errors = {
        '400': {
            'description': 'Bad Request',
            'example': {
                'success': False,
                'message': 'Validation failed',
                'code': 'validation_error',
                'data': None,
                'errors': {'field_name': ['This field is required.']}
            }
        },
        '401': {
            'description': 'Unauthorized',
            'example': {
                'success': False,
                'message': 'Authentication credentials were not provided.',
                'code': 'authentication_error',
                'data': None
            }
        },
        '403': {
            'description': 'Forbidden',
            'example': {
                'success': False,
                'message': 'You do not have permission to perform this action.',
                'code': 'permission_error',
                'data': None
            }
        },
        '404': {
            'description': 'Not Found',
            'example': {
                'success': False,
                'message': 'The requested resource was not found.',
                'code': 'not_found_error',
                'data': None
            }
        },
        '500': {
            'description': 'Internal Server Error',
            'example': {
                'success': False,
                'message': 'An unexpected error occurred on the server.',
                'code': 'server_error',
                'data': None
            }
        }
    }

    for path, methods in result['paths'].items():
        for method, operation in methods.items():
            if 'responses' not in operation:
                operation['responses'] = {}

            # Inject missing standard error responses
            for code, details in standard_errors.items():
                if code not in operation['responses']:
                    operation['responses'][code] = {
                        'description': details['description'],
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'success': {'type': 'boolean', 'example': details['example']['success']},
                                        'message': {'type': 'string', 'example': details['example']['message']},
                                        'code': {'type': 'string', 'example': details['example']['code']},
                                        'data': {'type': 'object', 'nullable': True, 'example': details['example']['data']}
                                    }
                                }
                            }
                        }
                    }
                    if 'errors' in details['example']:
                        operation['responses'][code]['content']['application/json']['schema']['properties']['errors'] = {
                            'type': 'object', 'example': details['example']['errors']
                        }

            # Wrap success responses
            for status_code, response in operation['responses'].items():
                if status_code in ['200', '201']:
                    if 'content' not in response:
                        response['content'] = {'application/json': {}}
                    elif 'application/json' not in response['content']:
                        response['content']['application/json'] = {}
                    
                    schema = response['content']['application/json'].get('schema')
                    
                    default_msg = "Operation completed successfully"
                    if status_code == '201':
                        default_msg = "Resource created successfully"
                    elif 'logout' in path.lower():
                        default_msg = "Logout successful"
                    elif 'profile' in path.lower():
                        default_msg = "Profile retrieved successfully"

                    wrapped_schema = {
                        'type': 'object',
                        'properties': {
                            'success': {'type': 'boolean', 'example': True},
                            'message': {'type': 'string', 'example': default_msg},
                            'code': {'type': 'string', 'example': 'success'},
                            'data': schema if schema else {'type': 'object', 'description': 'Response data', 'example': {}}
                        },
                        'required': ['success', 'message', 'code', 'data']
                    }
                    response['content']['application/json']['schema'] = wrapped_schema
    
    return result
