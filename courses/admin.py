from django.contrib import admin

from .models import Enrollment, Course, Lesson, Module

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "owner", "published", "category", "price", "created_date")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "owner__email", "category")
    list_filter = ("published", "category", "created_date")

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "order")
    search_fields = ("title", "course__title")
    list_filter = ("course",)

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "module", "order")
    search_fields = ("title", "module__title")
    list_filter = ("module",)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "enrolled_date", "progress", "completed")
    search_fields = ("student__email", "course__title")
    list_filter = ("completed", "enrolled_date")
