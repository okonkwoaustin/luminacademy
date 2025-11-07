from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Allow access only to admin users."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"


class IsInstructor(permissions.BasePermission):
    """Allow access only to instructors."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "instructor"


class IsStudent(permissions.BasePermission):
    """Allow access only to students."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"


class IsInstructorOrAdmin(permissions.BasePermission):
    """Allow instructors or admins to modify content."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["instructor", "admin"]
        )


class IsAdminOrInstructorOrStudent(permissions.BasePermission):
    """
    Allow safe (GET) methods for everyone, 
    but restrict write actions to instructors or admins.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "admin", "instructor"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "admin", "instructor" or getattr(obj, "pk", None) == getattr(request.user, "pk", None)



class IsOwnerOrReadOnly(permissions.BasePermission):
    """Object-level permission to allow only owners to edit."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user or request.user.role == "admin"


class IsAdminOrSelf(permissions.BasePermission):
    """Allow admins full access; allow users to view/update their own user object."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "admin"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == "admin" or getattr(obj, "pk", None) == getattr(request.user, "pk", None)


class IsStudentOrInstructorOrAdmin(permissions.BasePermission):
    """Allow access to students, instructors or admins at the view level."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ["student", "instructor", "admin"]
        )


class IsEnrollmentOwnerOrCourseInstructorOrAdmin(permissions.BasePermission):
    """Object-level permission for Enrollment objects.

    Allow safe methods to everyone who passed view-level permission.
    For unsafe methods, allow if the request user is the enrollment student,
    or the instructor of the enrollment's course, or an admin.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user.is_authenticated:
            return False
        if request.user.role == "admin":
            return True
        if hasattr(obj, "student") and obj.student == request.user:
            return True
        if hasattr(obj, "course") and obj.course.instructor == request.user:
            return True
        return False
