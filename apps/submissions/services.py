from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from apps.common.utils.response_builder import ResponseBuilder
from apps.exams.models import Exam, Question
from apps.submissions.models import Submission, Answer
from apps.submissions.grading.grader_factory import GraderFactory
from apps.submissions.serializers import SubmissionSerializer, SubmissionDetailSerializer, SubmissionCreateSerializer


class SubmissionService:
    @staticmethod
    @transaction.atomic
    def create_submission(data, student, request=None):
        serializer = SubmissionCreateSerializer(data=data)
        if not serializer.is_valid():
            return ResponseBuilder.error("validation", errors=serializer.errors)

        validated_data = serializer.validated_data
        exam_uuid = str(validated_data["exam_uuid"])
        answers_data = validated_data["answers"]
        started_at = validated_data.get("started_at")  # Optional: when student started the exam

        # Get IP address for audit trail
        ip_address = None
        if request:
            x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
            if x_forwarded_for:
                ip_address = x_forwarded_for.split(",")[0]
            else:
                ip_address = request.META.get("REMOTE_ADDR")

        # Get exam
        try:
            exam = Exam.objects.select_related("course").get(uuid=exam_uuid, is_active=True)
        except Exam.DoesNotExist:
            return ResponseBuilder.error("exam_not_found")

        # Validate exam availability
        now = timezone.now()
        if exam.start_time and now < exam.start_time:
            return ResponseBuilder.error("exam_not_started")
        if exam.end_time and now > exam.end_time:
            return ResponseBuilder.error("exam_ended")

        # Check for duplicate submission
        if Submission.objects.filter(student=student, exam=exam).exists():
            return ResponseBuilder.error("duplicate_submission")

        # Get all questions for the exam
        questions = Question.objects.filter(exam=exam).order_by("order")
        question_mapping = {str(q.uuid): q for q in questions}

        # Validate all questions are answered
        provided_question_uuids = {str(ans["question_uuid"]) for ans in answers_data}
        required_question_uuids = set(question_mapping.keys())

        if provided_question_uuids != required_question_uuids:
            missing = required_question_uuids - provided_question_uuids
            return ResponseBuilder.error(
                "validation", errors={"answers": [f'Missing answers for questions: {", ".join(missing)}']}
            )

        # Calculate actual time taken if started_at is provided
        if started_at:
            time_delta = timezone.now() - started_at
            time_taken = int(time_delta.total_seconds() / 60)
            # Cap at exam duration to prevent exceeding allowed time
            time_taken = min(time_taken, exam.duration_minutes)
        else:
            # Fallback: if no start time provided, use full duration
            time_taken = exam.duration_minutes

        # Create submission
        submission = Submission.objects.create(
            student=student,
            exam=exam,
            started_at=started_at,
            status="PENDING",
            time_taken_minutes=time_taken,
            ip_address=ip_address,
        )

        # Bulk create answers
        answer_objects = [
            Answer(
                submission=submission,
                question=question_mapping[str(ans["question_uuid"])],
                answer_text=ans["answer_text"],
            )
            for ans in answers_data
        ]

        Answer.objects.bulk_create(answer_objects)

        # Grade the submission
        grading_result = SubmissionService.grade_submission(str(submission.uuid))
        if not grading_result.success:
            # If grading fails, return error but submission is created
            submission.refresh_from_db()

        # Reload submission to get updated data
        submission.refresh_from_db()
        submission_data = SubmissionSerializer(submission).data
        submission_data["total_questions"] = len(answers_data)

        return ResponseBuilder.success(
            "submission_created",
            data={"submission": submission_data, "grading_status": "completed" if grading_result.success else "failed"},
        )

    @staticmethod
    @transaction.atomic
    def grade_submission(submission_uuid: str):
        try:
            submission = (
                Submission.objects.select_related("exam")
                .prefetch_related("answers__question")
                .get(uuid=submission_uuid)
            )

            # Update status to GRADING
            submission.status = "GRADING"
            submission.save()

            # Create grader based on configuration
            grader = GraderFactory.create_grader()

            # Grade the submission
            result = grader.grade_submission(submission)

            # Update submission with results
            submission.score = Decimal(str(result["total_score"]))
            submission.percentage = Decimal(str(result["percentage"]))
            submission.status = "COMPLETED"
            submission.graded_at = timezone.now()
            submission.save()

            return ResponseBuilder.success(
                "success",
                data={
                    "submission_uuid": str(submission.uuid),
                    "score": float(result["total_score"]),
                    "percentage": float(result["percentage"]),
                    "details": result["details"],
                },
            )

        except Submission.DoesNotExist:
            return ResponseBuilder.error("submission_not_found")
        except Exception as e:
            try:
                submission.status = "FAILED"
                submission.save()
            except:
                pass
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def get_student_submissions(student, query_params=None):
        from .serializers import SubmissionListQuerySerializer, SubmissionSerializer

        try:
            # Validate query parameters if provided
            if query_params:
                query_serializer = SubmissionListQuerySerializer(data=query_params)
                if not query_serializer.is_valid():
                    return ResponseBuilder.error("validation", errors=query_serializer.errors)

                filters = {key: value for key, value in query_serializer.validated_data.items() if value is not None}
            else:
                filters = {}

            queryset = (
                Submission.objects.filter(student=student)
                .select_related("exam", "exam__course")
                .order_by("-submitted_at")
            )

            # Apply filters dynamically using validated data
            exam_uuid = filters.get("exam_uuid")
            status = filters.get("status")

            if exam_uuid:
                queryset = queryset.filter(exam__uuid=exam_uuid)
            if status:
                queryset = queryset.filter(status=status)

            serializer = SubmissionSerializer(queryset, many=True)
            return ResponseBuilder.success(
                "submissions_retrieved", data={"count": len(serializer.data), "results": serializer.data}
            )
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})

    @staticmethod
    def get_submission_detail(submission_uuid: str, requesting_user):
        """Get detailed submission results including answers and statistics."""
        from django.db.models import Prefetch

        try:
            # Optimized prefetch for answers and questions
            answers_with_questions = Prefetch(
                "answers", queryset=Answer.objects.select_related("question").order_by("question__order")
            )

            submission = (
                Submission.objects.select_related("student", "exam", "exam__course")
                .prefetch_related(answers_with_questions)
                .get(uuid=submission_uuid)
            )

            # Authorization check
            if submission.student != requesting_user:
                return ResponseBuilder.error("forbidden")

            serializer = SubmissionDetailSerializer(submission)
            submission_data = serializer.data

            # Calculate statistics
            answers = list(submission.answers.all())
            correct_count = sum(1 for ans in answers if ans.is_correct)

            return ResponseBuilder.success(
                "submission_retrieved",
                data={
                    "submission": submission_data,
                    "statistics": {
                        "questions_answered": len(answers),
                        "correct_answers": correct_count,
                        "accuracy": round((correct_count / len(answers) * 100), 2) if answers else 0,
                    },
                },
            )
        except Submission.DoesNotExist:
            return ResponseBuilder.error("submission_not_found")
        except Exception as e:
            return ResponseBuilder.error("server_error", errors={"detail": [str(e)]})
