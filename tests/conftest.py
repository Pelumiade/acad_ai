import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def student_user():
    from tests.factories.user_factory import UserFactory

    return UserFactory(role="STUDENT")


@pytest.fixture
def instructor_user():
    from tests.factories.user_factory import UserFactory

    return UserFactory(role="INSTRUCTOR")


@pytest.fixture
def authenticated_client(api_client, student_user):
    api_client.force_authenticate(user=student_user)
    return api_client


@pytest.fixture
def instructor_client(api_client, instructor_user):
    api_client.force_authenticate(user=instructor_user)
    return api_client


@pytest.fixture
def sample_exam(instructor_user):
    from tests.factories.exam_factory import ExamFactory, CourseFactory

    course = CourseFactory(instructor=instructor_user)
    exam = ExamFactory(course=course, created_by=instructor_user)
    return exam
