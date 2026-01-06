from typing import Dict, Optional
from rest_framework import serializers
from apps.exams.models import Exam, Question
from apps.submissions.models import Submission, Answer


class AnswerSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    question_uuid = serializers.UUIDField(source="question.uuid", read_only=True)
    question_text = serializers.CharField(source="question.question_text", read_only=True)
    question_type = serializers.CharField(source="question.question_type", read_only=True)
    marks_possible = serializers.DecimalField(source="question.marks", max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Answer
        fields = [
            "id",
            "question_uuid",
            "question_text",
            "question_type",
            "answer_text",
            "marks_obtained",
            "marks_possible",
            "feedback",
            "is_correct",
            "graded_by_service",
            "graded_at",
        ]
        read_only_fields = ["id", "marks_obtained", "feedback", "is_correct", "graded_by_service", "graded_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    exam_title = serializers.CharField(source="exam.title", read_only=True)
    exam_uuid = serializers.UUIDField(source="exam.uuid", read_only=True)
    course_code = serializers.CharField(source="exam.course.code", read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "exam_uuid",
            "exam_title",
            "course_code",
            "status",
            "started_at",
            "submitted_at",
            "graded_at",
            "score",
            "percentage",
            "time_taken_minutes",
        ]
        read_only_fields = ["id", "status", "started_at", "submitted_at", "graded_at", "score", "percentage"]


class SubmissionListQuerySerializer(serializers.Serializer):
    exam_uuid = serializers.UUIDField(required=False, allow_null=False)
    status = serializers.ChoiceField(choices=Submission.STATUS_CHOICES, required=False, allow_null=False)


class SubmissionCreateSerializer(serializers.Serializer):
    exam_uuid = serializers.UUIDField(required=True)
    started_at = serializers.DateTimeField(required=False, allow_null=True)
    answers = serializers.ListField(child=serializers.DictField(), min_length=1, required=True)

    def validate_exam_uuid(self, value):
        """Validate exam exists and is active."""
        try:
            exam = Exam.objects.get(uuid=value, is_active=True)
            from django.utils import timezone

            now = timezone.now()
            if exam.start_time and now < exam.start_time:
                raise serializers.ValidationError("Exam has not started yet")
            if exam.end_time and now > exam.end_time:
                raise serializers.ValidationError("Exam has ended")
            return value
        except Exam.DoesNotExist:
            raise serializers.ValidationError("Exam not found or not active")

    def validate_answers(self, value):
        """Validate answer structure."""
        for answer in value:
            if "question_uuid" not in answer:
                raise serializers.ValidationError("Each answer must have question_uuid")
            if "answer_text" not in answer:
                raise serializers.ValidationError("Each answer must have answer_text")
            if not isinstance(answer["answer_text"], str):
                raise serializers.ValidationError("answer_text must be a string")
        return value


class SubmissionDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    exam = serializers.SerializerMethodField()
    answers = AnswerSerializer(many=True, read_only=True)
    passed = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = [
            "id",
            "exam",
            "status",
            "submitted_at",
            "graded_at",
            "score",
            "percentage",
            "time_taken_minutes",
            "passed",
            "answers",
        ]

    def get_exam(self, obj) -> Dict:
        """Get exam details."""
        return {
            "id": str(obj.exam.uuid),
            "title": obj.exam.title,
            "total_marks": float(obj.exam.total_marks),
            "passing_marks": float(obj.exam.passing_marks),
        }

    def get_passed(self, obj) -> Optional[bool]:
        """Check if student passed."""
        if obj.score is None:
            return None
        return float(obj.score) >= float(obj.exam.passing_marks)
