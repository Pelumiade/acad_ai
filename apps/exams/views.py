import traceback
import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.common.utils.response_utils import server_error_response
from apps.accounts.permissions import IsStudent, IsInstructor
from .services import ExamService, CourseService
from .serializers import ExamListSerializer, ExamDetailSerializer, CourseSerializer

logger = logging.getLogger("apps")


class CourseCreateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = CourseSerializer

    def post(self, request):
        try:
            result = CourseService.create_course(request.data, request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Course creation error: {traceback.format_exc()}")
            return server_error_response()


class CourseListView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CourseSerializer

    def get(self, request):
        try:
            result = CourseService.list_courses()
            return result.to_response()
        except Exception:
            logger.error(f"Course list error: {traceback.format_exc()}")
            return server_error_response()


class ExamListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ExamListSerializer

    def get(self, request):
        try:
            result = ExamService.list_exams(request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Exam list error: {traceback.format_exc()}")
            return server_error_response()


class ExamDetailView(APIView):

    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ExamDetailSerializer

    def get(self, request, uuid):
        try:
            result = ExamService.get_exam_detail(str(uuid))
            return result.to_response()
        except Exception:
            logger.error(f"Exam detail error: {traceback.format_exc()}")
            return server_error_response()


class ExamCreateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = ExamDetailSerializer

    def post(self, request):
        try:
            result = ExamService.create_exam(request.data, request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Exam creation error: {traceback.format_exc()}")
            return server_error_response()


class ExamUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = ExamDetailSerializer

    def put(self, request, uuid):
        try:
            result = ExamService.update_exam(str(uuid), request.data, request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Exam update error: {traceback.format_exc()}")
            return server_error_response()

    def patch(self, request, uuid):
        try:
            result = ExamService.update_exam(str(uuid), request.data, request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Exam patch error: {traceback.format_exc()}")
            return server_error_response()


class ExamDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsInstructor]
    serializer_class = None

    def delete(self, request, uuid):
        try:
            result = ExamService.delete_exam(str(uuid), request.user)
            return result.to_response()
        except Exception:
            logger.error(f"Exam deletion error: {traceback.format_exc()}")
            return server_error_response()
