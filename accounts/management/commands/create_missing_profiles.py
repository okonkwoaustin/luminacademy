from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import UserProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Create missing user profiles for all users'

    def handle(self, *args, **kwargs):
        users_without_profile = User.objects.filter(profile=None)
        count = users_without_profile.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS('No missing profiles found.'))
            return

        for user in users_without_profile:
            UserProfile.objects.create(user=user)

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count} missing user profiles.')
        )
