import django_filters
from courses .models import Course, Lesson, Module, Enrollment
from assessments.models import Quiz, Question, Submission


class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    instructor_email = django_filters.CharFilter(field_name="instructor__email", lookup_expr="icontains")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Course
        fields = ['title', 'instructor_email', 'created_after', 'created_before']
class LessonFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    module_title = django_filters.CharFilter(field_name="module__title", lookup_expr="icontains")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Lesson
        fields = ['title', 'module_title', 'created_after', 'created_before']

class ModuleFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    course_title = django_filters.CharFilter(field_name="course__title", lookup_expr="icontains")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Module
        fields = ['title', 'course_title', 'created_after', 'created_before']

class EnrollmentFilter(django_filters.FilterSet):
    student_email = django_filters.CharFilter(field_name="student__email", lookup_expr="icontains")
    course_title = django_filters.CharFilter(field_name="course__title", lookup_expr="icontains")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Enrollment
        fields = ['student_email', 'course_title', 'created_after', 'created_before']
        
class QuizFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name="title", lookup_expr="icontains")
    course_title = django_filters.CharFilter(field_name="course__title", lookup_expr="icontains")
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Quiz
        fields = ['title', 'course_title', 'created_after', 'created_before'] 