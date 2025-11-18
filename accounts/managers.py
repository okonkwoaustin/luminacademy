from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models


class CustomUserManager(BaseUserManager):

    class UserQuerySet(models.QuerySet):
        def active(self):
            return self.filter(is_deleted=False)

    def get_queryset(self):
        return self.UserQuerySet(self.model, using=self._db).active()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))

        email = self.normalize_email(email)

        # default role
        role = extra_fields.get('role', 'student')
        extra_fields['role'] = role

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # staff logic
        if role in ['admin', 'instructor']:
            user.is_staff = True
        else:
            user.is_staff = False

        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault('role', 'admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields['role'] != 'admin':
            raise ValueError("Superuser must have role='admin'")
        if extra_fields['is_staff'] is not True:
            raise ValueError(_("Superuser must have is_staff=True"))
        if extra_fields['is_superuser'] is not True:
            raise ValueError(_("Superuser must have is_superuser=True"))

        return self.create_user(email, password, **extra_fields)
