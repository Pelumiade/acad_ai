import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from apps.common.mixins.timestamp_mixin import TimestampMixin
from apps.exams.models import Exam, Question


class Submission(TimestampMixin):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("GRADING", "Grading"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="submissions", db_index=True
    )
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="submissions", db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING", db_index=True)
    started_at = models.DateTimeField(null=True, blank=True, db_index=True)
    submitted_at = models.DateTimeField(auto_now_add=True, db_index=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    time_taken_minutes = models.PositiveIntegerField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "submissions"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["student"]),
            models.Index(fields=["exam"]),
            models.Index(fields=["status"]),
            models.Index(fields=["submitted_at"]),
            models.Index(fields=["student", "exam", "status"], name="student_submission_idx"),
        ]
        unique_together = [["student", "exam"]]

    def clean(self):
        """Validate submission data."""
        if self.score is not None and self.exam:
            if self.score > self.exam.total_marks:
                raise ValidationError("score cannot exceed exam total_marks")

        if self.time_taken_minutes and self.exam:
            if self.time_taken_minutes > self.exam.duration_minutes:
                raise ValidationError("time_taken_minutes cannot exceed exam duration_minutes")

        if self.score is not None and self.exam:
            # Auto-calculate percentage
            if self.exam.total_marks > 0:
                self.percentage = (self.score / self.exam.total_marks) * 100

    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        if self.score is not None and self.exam and self.exam.total_marks > 0:
            self.percentage = (self.score / self.exam.total_marks) * 100
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.email} - {self.exam.title} - {self.status}"


class Answer(TimestampMixin):

    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name="answers", db_index=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, db_index=True)
    answer_text = models.TextField()
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by_service = models.CharField(max_length=20, blank=True)

    class Meta:
        db_table = "answers"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["submission"]),
            models.Index(fields=["question"]),
            models.Index(fields=["submission", "question"], name="answer_submission_question_idx"),
        ]
        unique_together = [["submission", "question"]]

    def clean(self):
        """Validate answer data."""
        if self.marks_obtained is not None and self.question:
            if self.marks_obtained > self.question.marks:
                raise ValidationError("marks_obtained cannot exceed question marks")

        # Auto-set is_correct based on marks
        if self.marks_obtained is not None and self.question:
            self.is_correct = self.marks_obtained >= self.question.marks

    def save(self, *args, **kwargs):
        """Override save to call clean validation."""
        if self.marks_obtained is not None and self.question:
            self.is_correct = self.marks_obtained >= self.question.marks
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to Q{self.question.order} - {self.answer_text[:50]}"
