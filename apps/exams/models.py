import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from apps.common.mixins.timestamp_mixin import TimestampMixin


class Course(TimestampMixin):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True, db_index=True)
    description = models.TextField(blank=True)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="courses", db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "courses"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["code"]),
            models.Index(fields=["instructor"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Exam(TimestampMixin):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="exams", db_index=True)
    duration_minutes = models.PositiveIntegerField()
    total_marks = models.DecimalField(max_digits=6, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=6, decimal_places=2)
    start_time = models.DateTimeField(null=True, blank=True, db_index=True)
    end_time = models.DateTimeField(null=True, blank=True, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_exams"
    )

    class Meta:
        db_table = "exams"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["course"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["start_time"]),
            models.Index(fields=["is_active", "start_time", "end_time"], name="exam_availability_idx"),
        ]

    def clean(self):
        """Validate exam data."""
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError("start_time must be before end_time")

        if self.passing_marks > self.total_marks:
            raise ValidationError("passing_marks cannot exceed total_marks")

    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.course.code}"


class Question(TimestampMixin):
    QUESTION_TYPE_CHOICES = [
        ("MCQ", "Multiple Choice Question"),
        ("SHORT_ANSWER", "Short Answer"),
        ("ESSAY", "Essay"),
    ]
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions", db_index=True)
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    marks = models.DecimalField(max_digits=5, decimal_places=2)
    order = models.PositiveIntegerField()
    options = models.JSONField(null=True, blank=True)
    correct_answer = models.TextField(null=True, blank=True)
    grading_rubric = models.JSONField(null=True, blank=True)
    case_sensitive = models.BooleanField(default=False)

    class Meta:
        db_table = "questions"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["exam", "order"], name="question_exam_order_idx"),
        ]
        unique_together = [["exam", "order"]]
        ordering = ["order"]

    def clean(self):
        """Validate question data."""
        if self.question_type == "MCQ":
            if not self.options:
                raise ValidationError("MCQ questions must have options")
            if not self.correct_answer:
                raise ValidationError("MCQ questions must have a correct_answer")

    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"
