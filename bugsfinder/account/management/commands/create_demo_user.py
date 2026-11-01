import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create or refresh the optional Bugs Finder demo account."

    def handle(self, *args, **options):
        email = os.getenv("BUGSFINDER_DEMO_EMAIL", "").strip()
        password = os.getenv("BUGSFINDER_DEMO_PASSWORD", "")

        if not email and not password:
            self.stdout.write("Demo account not configured; skipping.")
            return
        if not email or not password:
            raise CommandError(
                "Set both BUGSFINDER_DEMO_EMAIL and BUGSFINDER_DEMO_PASSWORD."
            )
        if len(password) < 12:
            raise CommandError("BUGSFINDER_DEMO_PASSWORD must be at least 12 characters.")

        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            email=email,
            defaults={"name": "Bug Finder Demo"},
        )
        user.name = "Bug Finder Demo"
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=["name", "is_active", "password", "updated_at"])

        action = "Created" if created else "Updated"
        self.stdout.write(f"{action} active Bugs Finder demo account: {email}")
