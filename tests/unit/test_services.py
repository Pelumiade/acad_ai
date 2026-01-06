import pytest
from apps.accounts.services import AuthService
from apps.submissions.services import SubmissionService
from apps.exams.services import ExamService


@pytest.mark.unit
@pytest.mark.django_db
class TestAuthService:

    def test_register_user_success(self):
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        result = AuthService.register_user(data)

        assert result.success is True
        assert "access" in result.data
        assert "refresh" in result.data
        assert "user" in result.data

    def test_register_user_duplicate_email(self, student_user):
        data = {
            "email": student_user.email,
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Test",
            "last_name": "User",
        }

        result = AuthService.register_user(data)

        assert result.success is False

    def test_login_user_success(self, student_user):
        data = {"email": student_user.email, "password": "testpass123"}

        result = AuthService.login_user(data)

        assert result.success is True
        assert "access" in result.data
        assert "refresh" in result.data

    def test_login_user_invalid_credentials(self):
        data = {"email": "nonexistent@example.com", "password": "wrongpass"}

        result = AuthService.login_user(data)

        assert result.success is False

    def test_refresh_token_success(self, student_user):
        """Test successful token refresh."""
        from rest_framework_simplejwt.tokens import RefreshToken

        # Create initial refresh token
        refresh = RefreshToken.for_user(student_user)
        old_refresh_token = str(refresh)

        result = AuthService.refresh_token(old_refresh_token)

        assert result.success is True
        assert "access" in result.data
        assert "refresh" in result.data
        # New refresh token should be different (rotation enabled)
        assert result.data["refresh"] != old_refresh_token


@pytest.mark.unit
@pytest.mark.django_db
class TestSubmissionService:
    """Test submission services."""

    def test_create_submission_validation_error(self, student_user, sample_exam):
        data = {"exam_uuid": "invalid-uuid", "answers": []}

        result = SubmissionService.create_submission(data, student_user)

        assert result.success is False

    def test_grade_submission_not_found(self):
        result = SubmissionService.grade_submission("00000000-0000-0000-0000-000000000000")

        assert result.success is False

    def test_get_student_submissions(self, student_user):
        """Test getting student submissions."""
        result = SubmissionService.get_student_submissions(student_user)

        assert result.success is True
        assert "results" in result.data


@pytest.mark.unit
@pytest.mark.django_db
class TestExamService:
    """Test exam services."""

    def test_get_exam_by_uuid_not_found(self):
        with pytest.raises(ValueError):
            ExamService.get_exam_by_uuid("00000000-0000-0000-0000-000000000000")

    def test_list_exams(self, student_user):
        result = ExamService.list_exams(student_user)

        assert result.success is True
        assert "results" in result.data

    def test_get_exam_detail_not_found(self):
        result = ExamService.get_exam_detail("00000000-0000-0000-0000-000000000000")

        assert result.success is False
