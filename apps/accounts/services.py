from rest_framework_simplejwt.tokens import RefreshToken
from apps.common.utils.response_builder import ResponseBuilder
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from .models import User


class AuthService:
    @staticmethod
    def register_user(data, request=None):

        serializer = RegisterSerializer(data=data)
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        validated_data = serializer.validated_data

        try:
            user = User.objects.create_user(
                email=validated_data["email"],
                password=validated_data["password"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
                role=validated_data.get("role", "STUDENT"),
            )

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            user_data = UserSerializer(user).data
            return ResponseBuilder.success(
                "registration", data={"user": user_data, "access": str(refresh.access_token), "refresh": str(refresh)}
            )
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def login_user(data, request=None):

        from django.contrib.auth import authenticate

        serializer = LoginSerializer(data=data, context={"request": request})
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        validated_data = serializer.validated_data

        user = authenticate(email=validated_data["email"], password=validated_data["password"])

        if not user:
            return ResponseBuilder.error("invalid_credentials")

        if not user.is_active:
            return ResponseBuilder.error("account_deactivated")

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        user_data = UserSerializer(user).data

        return ResponseBuilder.success(
            "login", data={"user": user_data, "access": str(refresh.access_token), "refresh": str(refresh)}
        )

    @staticmethod
    def logout_user(user, refresh_token=None):
        # If refresh token provided, blacklist it
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return ResponseBuilder.success("logout")

    @staticmethod
    def get_user_profile(user):
        user_data = UserSerializer(user).data
        return ResponseBuilder.success("profile_retrieved", data={"user": user_data})

    @staticmethod
    def refresh_token(refresh_token_string):
        try:
            from django.conf import settings

            refresh = RefreshToken(refresh_token_string)
            data = {"access": str(refresh.access_token)}

            # Handle rotation if enabled in settings
            rotate_tokens = getattr(settings, "SIMPLE_JWT", {}).get("ROTATE_REFRESH_TOKENS", False)
            if rotate_tokens:
                blacklist_tokens = getattr(settings, "SIMPLE_JWT", {}).get("BLACKLIST_AFTER_ROTATION", False)
                if blacklist_tokens:
                    try:
                        refresh.blacklist()
                    except (AttributeError, Exception):
                        pass

                # Rotation means creating a NEW token for the same user
                refresh.set_jti()
                refresh.set_exp()
                refresh.set_iat()
                data["refresh"] = str(refresh)
            else:
                data["refresh"] = refresh_token_string

            return ResponseBuilder.success("token_refreshed", data=data)
        except Exception as e:
            return ResponseBuilder.error("token_refresh_failed", errors={"detail": [str(e)]})
