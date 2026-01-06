from django.urls import path
from .views import SubmissionCreateView, SubmissionListView, SubmissionDetailView

app_name = "submissions"

urlpatterns = [
    path("", SubmissionCreateView.as_view(), name="submission-create"),
    path("list/", SubmissionListView.as_view(), name="submission-list"),
    path("<uuid:uuid>/", SubmissionDetailView.as_view(), name="submission-detail"),
]
