import traceback
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.common.utils.response_utils import server_error_response
from .services import AuthService
from .serializers import RegisterSerializer, LoginSerializer

logger = logging.getLogger("apps")


class RegisterView(APIView):

    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request):
        try:
            result = AuthService.register_user(request.data)
            return result.to_response()
        except Exception:
            logger.error(f"Registration error: {traceback.format_exc()}")
            return server_error_response()


class LoginView(APIView):

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        try:
            result = AuthService.login_user(request.data)
            return result.to_response()
        except Exception:
            logger.error(f"Login error: {traceback.format_exc()}")
            return server_error_response()


class LogoutView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = None

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            result = AuthService.logout_user(request.user, refresh_token)
            return result.to_response()
        except Exception:
            logger.error(f"Logout error: {traceback.format_exc()}")
            return server_error_response()


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]
    serializer_class = None

    def get(self, request):
        try:
            result = AuthService.get_user_profile(request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Profile retrieval error: {traceback.format_exc()}")
            return server_error_response()


class RefreshTokenView(APIView):

    permission_classes = [AllowAny]
    serializer_class = None

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                return server_error_response()
            result = AuthService.refresh_token(refresh_token)
            return result.to_response()
        except Exception:
            logger.error(f"Token refresh error: {traceback.format_exc()}")
            return server_error_response()
