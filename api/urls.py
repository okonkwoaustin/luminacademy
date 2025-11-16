from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    UserViewSet,
    CourseViewSet,
    LessonViewSet,
    ModuleViewSet,
    EnrollmentViewSet,
    QuizViewSet,
    QuestionViewSet,
    SubmissionViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")
router.register(r"quizzes", QuizViewSet, basename="quiz")
router.register(r"questions", QuestionViewSet, basename="question")
router.register(r"submissions", SubmissionViewSet, basename="submission")


urlpatterns = [
    # Course Urls
    path("", include(router.urls)),
]