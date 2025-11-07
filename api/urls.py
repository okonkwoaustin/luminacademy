from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    UserViewSet,
    EmailTokenObtainPairView,
    CourseViewSet,
    LessonViewSet,
    ModuleViewSet,
    EnrollmentViewSet,
)

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"courses", CourseViewSet, basename="course")
router.register(r"modules", ModuleViewSet, basename="module")
router.register(r"lessons", LessonViewSet, basename="lesson")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollment")


urlpatterns = [    
    path('register/', RegisterView.as_view(), name='token_obtain_pair'),
    path("token/login/", EmailTokenObtainPairView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # Course Urls
    path("", include(router.urls)),
]