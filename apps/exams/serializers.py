from rest_framework import serializers
from .models import Course, Exam, Question


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    instructor_id = serializers.UUIDField(source="instructor.uuid", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "name", "code", "description", "instructor_id", "is_active"]
        read_only_fields = ["id", "instructor_id"]


class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "question_type", "marks", "order", "options", "grading_rubric"]
        read_only_fields = ["id"]


class ExamListSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    course = CourseSerializer(read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "course",
            "duration_minutes",
            "total_marks",
            "start_time",
            "end_time",
            "is_active",
            "question_count",
        ]
        read_only_fields = ["id"]

    def get_question_count(self, obj) -> int:
        return obj.questions.count()


class ExamDetailSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source="uuid", read_only=True)
    course = CourseSerializer(read_only=True)
    course_uuid = serializers.UUIDField(write_only=True, required=False)
    questions = QuestionSerializer(many=True, required=False)

    class Meta:
        model = Exam
        fields = [
            "id",
            "title",
            "description",
            "course",
            "course_uuid",
            "duration_minutes",
            "total_marks",
            "passing_marks",
            "start_time",
            "end_time",
            "instructions",
            "is_active",
            "questions",
        ]
        read_only_fields = ["id", "course"]

    def validate(self, attrs):
        """Validate exam data."""
        if attrs.get("passing_marks") and attrs.get("total_marks"):
            if attrs["passing_marks"] > attrs["total_marks"]:
                raise serializers.ValidationError({"passing_marks": "Passing marks cannot exceed total marks."})
        return attrs
