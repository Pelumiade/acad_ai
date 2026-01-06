from django.contrib import admin
from .models import Course, Exam, Question


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ["uuid", "code", "name", "instructor", "is_active"]
    list_filter = ["is_active", "created_at"]
    search_fields = ["name", "code", "instructor__email"]
    readonly_fields = ["uuid"]


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ["uuid", "title", "course", "total_marks", "is_active", "start_time", "end_time"]
    list_filter = ["is_active", "start_time", "end_time", "created_at"]
    search_fields = ["title", "course__code", "course__name"]
    readonly_fields = ["uuid"]
    filter_horizontal = []


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ["uuid", "exam", "question_type", "order", "marks"]
    list_filter = ["question_type", "exam"]
    search_fields = ["question_text", "exam__title"]
    readonly_fields = ["uuid"]
    ordering = ["exam", "order"]
