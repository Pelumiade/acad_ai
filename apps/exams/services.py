from django.db.models import Prefetch, Q
from django.db import transaction
from apps.common.utils.response_builder import ResponseBuilder
from .models import Exam, Question, Course
from .serializers import ExamListSerializer, ExamDetailSerializer, CourseSerializer


class CourseService:
    @staticmethod
    def create_course(data: dict, created_by):
        serializer = CourseSerializer(data=data)
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        try:
            # Set instructor to the creator
            course = Course.objects.create(instructor=created_by, **serializer.validated_data)
            serializer = CourseSerializer(course)
            return ResponseBuilder.success("course_created", data=serializer.data)
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def list_courses():
        try:
            courses = Course.objects.filter(is_active=True).select_related("instructor")
            serializer = CourseSerializer(courses, many=True)
            return ResponseBuilder.success(
                "courses_retrieved", data={"count": len(serializer.data), "results": serializer.data}
            )
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})


class ExamService:
    @staticmethod
    def get_exam_by_uuid(exam_uuid: str):
        try:
            return Exam.objects.select_related("course", "created_by").get(uuid=exam_uuid)
        except Exam.DoesNotExist:
            raise ValueError("Exam not found")

    @staticmethod
    def get_exam_with_questions(exam_uuid: str):
        try:
            return Exam.objects.prefetch_related("questions").select_related("course", "created_by").get(uuid=exam_uuid)
        except Exam.DoesNotExist:
            raise ValueError("Exam not found")

    @staticmethod
    def get_active_exams_for_student(student):
        """Get active exams available for students."""
        from django.utils import timezone

        now = timezone.now()
        return (
            Exam.objects.filter(is_active=True)
            .filter(
                Q(start_time__isnull=True) | Q(start_time__lte=now), Q(end_time__isnull=True) | Q(end_time__gte=now)
            )
            .select_related("course")
            .prefetch_related("questions")
            .order_by("-created_at")
        )

    @staticmethod
    def list_exams(student):
        try:
            exams = ExamService.get_active_exams_for_student(student)
            serializer = ExamListSerializer(exams, many=True)
            return ResponseBuilder.success(
                "exams_retrieved", data={"count": len(serializer.data), "results": serializer.data}
            )
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def get_exam_detail(exam_uuid: str):
        try:
            exam = ExamService.get_exam_with_questions(exam_uuid)
            serializer = ExamDetailSerializer(exam)
            return ResponseBuilder.success("exam_retrieved", data=serializer.data)
        except ValueError:
            return ResponseBuilder.error("exam_not_found")
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    @transaction.atomic
    def create_exam(data: dict, created_by):
        from .serializers import ExamDetailSerializer

        serializer = ExamDetailSerializer(data=data)
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        try:
            # Get course
            course_uuid = serializer.validated_data.pop("course_uuid", None)
            if not course_uuid:
                return ResponseBuilder.error("validation", errors={"course_uuid": ["This field is required."]})

            try:
                course = Course.objects.get(uuid=course_uuid)
            except Course.DoesNotExist:
                return ResponseBuilder.error("not_found", errors={"course_uuid": ["Course not found."]})

            # Extract questions data
            questions_data = serializer.validated_data.pop("questions", [])

            # Create exam
            exam = Exam.objects.create(course=course, created_by=created_by, **serializer.validated_data)

            # Bulk create questions
            question_objects = []
            for q_data in questions_data:
                question_objects.append(Question(exam=exam, **q_data))

            if question_objects:
                Question.objects.bulk_create(question_objects)

            # Reload with questions
            exam.refresh_from_db()
            serializer = ExamDetailSerializer(exam)
            return ResponseBuilder.success("exam_created", data=serializer.data)

        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    @transaction.atomic
    def update_exam(exam_uuid: str, data: dict, updated_by):
        from .serializers import ExamDetailSerializer

        try:
            exam = Exam.objects.select_related("course", "created_by").get(uuid=exam_uuid)
        except Exam.DoesNotExist:
            return ResponseBuilder.error("exam_not_found")

        serializer = ExamDetailSerializer(exam, data=data, partial=True)
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        try:
            course_uuid = serializer.validated_data.pop("course_uuid", None)
            if course_uuid:
                try:
                    new_course = Course.objects.get(uuid=course_uuid)
                    if new_course.instructor != updated_by and updated_by.role != "ADMIN":
                        return ResponseBuilder.error(
                            "permission_denied",
                            errors={"course_uuid": ["You do not have permission to assign exams to this course."]},
                        )
                    exam.course = new_course
                except Course.DoesNotExist:
                    return ResponseBuilder.error("not_found", errors={"course_uuid": ["Course not found."]})

            # Handle questions update if provided
            questions_data = serializer.validated_data.pop("questions", None)

            # Update exam fields
            for attr, value in serializer.validated_data.items():
                setattr(exam, attr, value)
            exam.save()

            # Update questions if provided
            if questions_data is not None:
                # Delete existing questions and recreate
                Question.objects.filter(exam=exam).delete()
                question_objects = []
                for q_data in questions_data:
                    question_objects.append(Question(exam=exam, **q_data))

                if question_objects:
                    Question.objects.bulk_create(question_objects)

            # Reload with questions
            exam.refresh_from_db()
            serializer = ExamDetailSerializer(exam)
            return ResponseBuilder.success("exam_updated", data=serializer.data)

        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def delete_exam(exam_uuid: str, deleted_by):
        try:
            exam = Exam.objects.select_related("created_by", "course").get(uuid=exam_uuid)
        except Exam.DoesNotExist:
            return ResponseBuilder.error("exam_not_found")

        try:
            exam.delete()
            return ResponseBuilder.success("exam_deleted")
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})
