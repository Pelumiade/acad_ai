import traceback
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.common.utils.response_utils import server_error_response
from apps.accounts.permissions import IsStudent
from .services import SubmissionService
from .serializers import SubmissionCreateSerializer, SubmissionSerializer, SubmissionDetailSerializer

logger = logging.getLogger("apps")


class SubmissionCreateView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = SubmissionCreateSerializer

    def post(self, request):
        try:
            result = SubmissionService.create_submission(request.data, request.user, request)
            return result.to_response()
        except Exception:
            logger.error(f"Submission creation error: {traceback.format_exc()}")
            return server_error_response()


class SubmissionListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = SubmissionSerializer

    def get(self, request):
        try:
            result = SubmissionService.get_student_submissions(request.user, request.query_params)
            return result.to_response()
        except Exception:
            logger.error(f"Submission list error: {traceback.format_exc()}")
            return server_error_response()


class SubmissionDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = SubmissionDetailSerializer

    def get(self, request, uuid):
        try:
            result = SubmissionService.get_submission_detail(str(uuid), request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Submission detail error: {traceback.format_exc()}")
            return server_error_response()
