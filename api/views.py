from decimal import Decimal, InvalidOperation
from rest_framework.decorators import action
from courses.models import Lesson, Module, Course, Enrollment
from assessments.models import Quiz, Question, Submission
from .permissions import (
    IsAdmin,
    IsInstructor,
    IsInstructorOrAdmin,
    IsOwnerOrReadOnly,
    IsAdminOrSelf,
    IsStudent,
    IsAdminOrInstructorOrStudent,
    IsStudentOrInstructorOrAdmin,
    IsEnrollmentOwnerOrCourseInstructorOrAdmin,
    IsAdminOrOwnerOrReadOnly,
)
from .serializers import (
    UserSerializer,
    LessonSerializer,
    ModuleSerializer,
    CourseSerializer,
    EnrollmentSerializer,
    QuizSerializer,
    QuestionSerializer,
    SubmissionSerializer,
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework import generics
from django_filters import rest_framework as filtering
from rest_framework import filters
from django.contrib.auth import get_user_model
from .utils.response import ResponseFormatter
User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrSelf]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['email', 'role', 'is_active']
    search_fields = ['email', 'first_name', 'last_name']
    def get_queryset(self):
        user = self.request.user
        if user.role == "admin":
            return User.objects.all()
        return User.objects.filter(id=user.id)
    
    def destroy(self, request, *args, **kwargs):
        user = User.all_objects.get(pk=kwargs["pk"])
        user.delete()  # soft delete

        return Response(
            {"message": "User soft deleted successfully."},
            status=status.HTTP_200_OK
        )

class CourseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrOwnerOrReadOnly]
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['owner__email', 'title']
    search_fields = ['title', 'description', 'owner__email']

    def get_queryset(self):
        user = self.request.user

        if user.role == "admin" or user.is_superuser:
            return Course.objects.all()

        if user.role == "instructor":
            return Course.objects.filter(owner=user)

        # students will see all courses
        return Course.objects.all()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(instructor=request.user)
            return ResponseFormatter.success(
                message="Course created successfully!",
                data=serializer.data,
                status_code=status.HTTP_201_CREATED
            )
        return ResponseFormatter.error(
            message="Only instructors and admins can create courses.",
            errors=serializer.errors
        )
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return ResponseFormatter.success(
                message="Course updated successfully!",
                data=serializer.data
            )
        return ResponseFormatter.error(
            message="Failed to update course.",
            errors=serializer.errors
        )

    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return ResponseFormatter.success(
            message="Course deleted successfully!",
            data=None,
            status_code=status.HTTP_204_NO_CONTENT
        )
   

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        user = request.user
        course = self.get_object()
        if user.role != "student":
            return Response({"error": "Only students can enroll."}, status=403)
        enrollment, created = Enrollment.objects.get_or_create(
            student=user, course=course)
        if not created:
            return Response({"message": "Already enrolled."}, status=200)
        return Response({"message": "Enrolled successfully!"}, status=201)

    @action(detail=True, methods=["get"], permission_classes=[IsInstructorOrAdmin])
    def students(self, request, pk=None):
        course = self.get_object()
        enrollments = Enrollment.objects.filter(course=course)
        data = [{"student": e.student.email, "progress": e.progress}
                for e in enrollments]
        return Response(data)


class LessonViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrInstructorOrStudent, IsOwnerOrReadOnly]
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['module__course__title', 'module__title', 'title']
    search_fields = ['title', 'content',
                     'module__title', 'module__course__title']

    def perform_create(self, serializer):
        module_id = self.request.data.get("module")
        module = generics.get_object_or_404(Module, id=module_id)
        if module.course.instructor != self.request.user and self.request.user.role != "admin":
            raise permissions.PermissionDenied(
                "You do not have permission to add lessons to this module.")
        serializer.save(module=module)


class ModuleViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrInstructorOrStudent, IsOwnerOrReadOnly]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course__title', 'title']
    search_fields = ['title', 'course__title']

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        course = generics.get_object_or_404(Course, id=course_id)
        if course.instructor != self.request.user and self.request.user.role != "admin":
            raise permissions.PermissionDenied(
                "You do not have permission to add modules to this course.")
        serializer.save(course=course)


class EnrollmentViewSet(viewsets.ModelViewSet):
    # Allow authenticated students, instructors and admins at the view level.
    # Object-level permissions below will restrict unsafe actions to the
    # enrollment owner, the course instructor, or admin.
    permission_classes = [
        IsStudentOrInstructorOrAdmin,
        IsEnrollmentOwnerOrCourseInstructorOrAdmin
    ]
    serializer_class = EnrollmentSerializer
    queryset = Enrollment.objects.all()
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course__title', 'completed']
    search_fields = ['course__title', 'student__email']

    def create(self, request, *args, **kwargs):
        """
        Override create so the student is always the authenticated user and
        a course id must be provided. This prevents NOT NULL constraint
        failures when the request omits the course field.
        """
        course_id = request.data.get("course")
        if not course_id:
            return Response({"error": "Course id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        # Students enroll themselves; instructors/admins may create enrollments
        # on behalf of students by providing a student id.
        if user.role == "student":
            student = user
        elif user.role in ("instructor", "admin"):
            student_id = request.data.get("student")
            if not student_id:
                return Response({"error": "student id is required when creating enrollments as instructor/admin."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                student = User.objects.get(pk=student_id)
            except User.DoesNotExist:
                return Response({"error": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
            if student.role != "student":
                return Response({"error": "Provided user is not a student."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "You do not have permission to create enrollments."}, status=status.HTTP_403_FORBIDDEN)

        enrollment, created = Enrollment.objects.get_or_create(
            student=student, course=course)
        serializer = self.get_serializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get_queryset(self):
        return Enrollment.objects.filter(student=self.request.user)

    @action(detail=True, methods=["post"])
    def update_progress(self, request, pk=None):
        enrollment = self.get_object()
        progress = request.data.get("progress")
        if progress is None:
            return Response({"error": "Progress value is required."}, status=400)

        # Coerce to Decimal for reliable comparison and storage
        try:
            progress_decimal = Decimal(str(progress))
        except (InvalidOperation, TypeError, ValueError):
            return Response({"error": "Progress must be a numeric value between 0 and 100."}, status=400)

        # Validate range
        if progress_decimal < 0 or progress_decimal > 100:
            return Response({"error": "Progress must be between 0 and 100."}, status=400)

        enrollment.progress = progress_decimal
        enrollment.completed = progress_decimal >= Decimal("100")
        enrollment.save()
        return Response({"message": "Progress completed.", "progress": str(enrollment.progress), "completed": enrollment.completed}, status=200)

    @action(detail=False, methods=["get"])
    def my_enrollments(self, request):
        user = request.user
        if user.role == "student":
            enrollments = Enrollment.objects.filter(student=user)
        elif user.role == "instructor":
            enrollments = Enrollment.objects.filter(course__instructor=user)
        elif user.role == "admin":
            enrollments = Enrollment.objects.all()
        else:
            enrollments = Enrollment.objects.none()

        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class QuizViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrInstructorOrStudent, IsOwnerOrReadOnly]
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course__title', 'title']
    search_fields = ['title', 'description', 'course__title']

    def perform_create(self, serializer):
        course_id = self.request.data.get("course")
        course = generics.get_object_or_404(Course, id=course_id)
        if course.instructor != self.request.user and self.request.user.role != "admin":
            raise permissions.PermissionDenied(
                "You do not have permission to add quizzes to this course.")
        serializer.save(course=course)

class QuestionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrInstructorOrStudent, IsOwnerOrReadOnly]
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['quiz__title']
    search_fields = ['text', 'quiz__title']

    def perform_create(self, serializer):
        quiz_id = self.request.data.get("quiz")
        quiz = generics.get_object_or_404(Quiz, id=quiz_id)
        if quiz.course.instructor != self.request.user and self.request.user.role != "admin":
            raise permissions.PermissionDenied(
                "You do not have permission to add questions to this quiz.")
        serializer.save(quiz=quiz)

class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrInstructorOrStudent, IsOwnerOrReadOnly]
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    filter_backends = [filtering.DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['quiz__title', 'student__email']
    search_fields = ['quiz__title', 'student__email']

    def perform_create(self, serializer):
        quiz_id = self.request.data.get("quiz")
        quiz = generics.get_object_or_404(Quiz, id=quiz_id)
        user = self.request.user
        if user.role != "student":
            raise permissions.PermissionDenied(
                "Only students can submit quizzes.")
        serializer.save(quiz=quiz, student=user)