import factory
from decimal import Decimal
from factory.django import DjangoModelFactory
from apps.submissions.models import Submission, Answer
from tests.factories.user_factory import UserFactory
from tests.factories.exam_factory import ExamFactory, QuestionFactory


class SubmissionFactory(DjangoModelFactory):

    class Meta:
        model = Submission
        skip_postgeneration_save = True

    student = factory.SubFactory(UserFactory, role="STUDENT")
    exam = factory.SubFactory(ExamFactory)
    status = "PENDING"
    time_taken_minutes = 60
    score = None
    percentage = None

    @factory.post_generation
    def set_score(obj, create, extracted, **kwargs):
        """Set score and percentage if score is provided."""
        if extracted is not None and create:
            obj.score = Decimal(str(extracted))
            if obj.exam and obj.exam.total_marks > 0:
                obj.percentage = (obj.score / obj.exam.total_marks) * 100
            obj.save()


class AnswerFactory(DjangoModelFactory):

    class Meta:
        model = Answer

    submission = factory.SubFactory(SubmissionFactory)
    question = factory.SubFactory(QuestionFactory)
    answer_text = factory.Faker("sentence", nb_words=5)
    marks_obtained = None
    feedback = ""
    is_correct = None
