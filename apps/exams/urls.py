from django.urls import path
from .views import (
    CourseCreateView,
    CourseListView,
    ExamListView,
    ExamDetailView,
    ExamCreateView,
    ExamUpdateView,
    ExamDeleteView,
)

app_name = "exams"

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/create/", CourseCreateView.as_view(), name="course-create"),
    path("", ExamListView.as_view(), name="exam-list"),
    path("<uuid:uuid>/", ExamDetailView.as_view(), name="exam-detail"),
    path("create/", ExamCreateView.as_view(), name="exam-create"),
    path("<uuid:uuid>/update/", ExamUpdateView.as_view(), name="exam-update"),
    path("<uuid:uuid>/delete/", ExamDeleteView.as_view(), name="exam-delete"),
]
