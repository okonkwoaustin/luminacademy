import re
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model


class EmailOrPhoneBackend(ModelBackend):
    """Authentication backend that accepts either email or phone number as
    the identifier.

    How it works:
    - Try to find a user whose email matches the provided username (case-insensitive).
    - If not found, try to match phone number. We attempt a digits-only match
      (strip non-digits from the provided identifier) and a case-insensitive
      raw lookup as a fallback.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)

        if username is None:
            return None

        # Try email (case-insensitive)
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            # Normalize to digits and try phone_number exact match
            digits = re.sub(r"\D", "", username or "")
            user = None
            if digits:
                try:
                    user = UserModel.objects.get(phone_number=digits)
                except UserModel.DoesNotExist:
                    user = None

            # If still not found, try raw phone_number field (case-insensitive)
            if user is None:
                try:
                    user = UserModel.objects.get(phone_number=username)
                except UserModel.DoesNotExist:
                    return None

        # At this point we have a user object or None
        if user is None:
            return None

        # Use ModelBackend's user_can_authenticate helper (checks is_active by default)
        if not self.user_can_authenticate(user):
            return None

        if user.check_password(password):
            return user

        return None
