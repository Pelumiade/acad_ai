import logging
import time

logger = logging.getLogger("apps")


class LoggingMiddleware:
    """Middleware to log all requests and responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Log request
        logger.info(
            f"Request: {request.method} {request.path} | " f"User: {getattr(request.user, 'email', 'Anonymous')}"
        )

        response = self.get_response(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            f"Response: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s"
        )

        return response
