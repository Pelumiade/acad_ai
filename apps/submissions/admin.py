from django.contrib import admin
from .models import Submission, Answer


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ["uuid", "student", "exam", "status", "score", "percentage", "submitted_at"]
    list_filter = ["status", "submitted_at", "graded_at"]
    search_fields = ["student__email", "exam__title"]
    readonly_fields = ["uuid", "submitted_at", "graded_at", "percentage"]
    ordering = ["-submitted_at"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["uuid", "submission", "question", "marks_obtained", "is_correct", "graded_at"]
    list_filter = ["is_correct", "graded_by_service", "graded_at"]
    search_fields = ["submission__student__email", "question__question_text"]
    readonly_fields = ["uuid", "graded_at"]
    ordering = ["-created_at"]
