import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
from apps.exams.models import Course, Exam, Question
from tests.factories.user_factory import UserFactory


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    name = factory.Faker("sentence", nb_words=3)
    code = factory.Faker("bothify", text="??###")
    description = factory.Faker("paragraph")
    instructor = factory.SubFactory(UserFactory, role="INSTRUCTOR")
    is_active = True


class ExamFactory(DjangoModelFactory):

    class Meta:
        model = Exam

    title = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("paragraph")
    course = factory.SubFactory(CourseFactory)
    duration_minutes = 120
    total_marks = 100
    passing_marks = 50
    is_active = True
    start_time = factory.LazyFunction(lambda: timezone.now() - timezone.timedelta(hours=1))
    end_time = factory.LazyFunction(lambda: timezone.now() + timezone.timedelta(hours=2))
    instructions = factory.Faker("paragraph")
    created_by = factory.SelfAttribute("course.instructor")


class QuestionFactory(DjangoModelFactory):

    class Meta:
        model = Question

    exam = factory.SubFactory(ExamFactory)
    question_text = factory.Faker("sentence", nb_words=10)
    question_type = "MCQ"
    marks = 10
    order = factory.Sequence(lambda n: n + 1)
    options = factory.LazyFunction(lambda: {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"})
    correct_answer = "B"
    case_sensitive = False
