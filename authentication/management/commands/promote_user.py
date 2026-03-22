"""
Grant staff (and optionally superuser) to a user by email.

Usage:
  python manage.py promote_user you@example.com
  python manage.py promote_user you@example.com --staff-only
  python manage.py promote_user you@example.com --create
  python manage.py promote_user you@example.com --create --password YourSecret123
"""

import secrets
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

User = get_user_model()


def _unique_username_from_email(email: str) -> str:
    local = (email.split("@")[0] or "user").strip()[:40]
    if not local:
        local = "user"
    username = local
    n = 1
    while User.objects.filter(username=username).exists():
        username = f"{local}{n}"
        n += 1
    return username


class Command(BaseCommand):
    help = "Set is_staff (and by default is_superuser) for the user with this email."

    def add_arguments(self, parser):
        parser.add_argument("email", type=str, help="User email (login email)")
        parser.add_argument(
            "--staff-only",
            action="store_true",
            help="Only set is_staff=True; do not grant is_superuser.",
        )
        parser.add_argument(
            "--create",
            action="store_true",
            help="If no user exists with this email, create one with staff+superuser.",
        )
        parser.add_argument(
            "--password",
            type=str,
            default="",
            help="With --create: set this password (min 6 chars). If omitted, a random password is generated and printed.",
        )

    def handle(self, *args, **options):
        email = (options["email"] or "").lower().strip()
        staff_only = options["staff_only"]
        create = options["create"]
        raw_password = (options.get("password") or "").strip()

        if not email:
            self.stderr.write(self.style.ERROR("Email is required."))
            return

        try:
            user = User.objects.get(email=email)
            created = False
        except User.DoesNotExist:
            if not create:
                self.stderr.write(
                    self.style.ERROR(
                        f'No user found with email "{email}". '
                        "Register on the site first, or run with --create to create this account."
                    )
                )
                return
            if raw_password and len(raw_password) < 6:
                self.stderr.write(
                    self.style.ERROR("--password must be at least 6 characters.")
                )
                return
            if not raw_password:
                alphabet = string.ascii_letters + string.digits
                raw_password = "".join(secrets.choice(alphabet) for _ in range(14))
                self.stdout.write(
                    self.style.WARNING(
                        "Generated password (save this; it will not be shown again):"
                    )
                )
                self.stdout.write(self.style.SUCCESS(raw_password))
            username = _unique_username_from_email(email)
            user = User.objects.create_user(
                email=email,
                username=username,
                password=raw_password,
            )
            created = True
            self.stdout.write(
                self.style.SUCCESS(f'Created user "{email}" with username "{username}".')
            )

        user.is_staff = True
        fields = ["is_staff"]
        if not staff_only:
            user.is_superuser = True
            fields.append("is_superuser")
        user.save(update_fields=fields)

        action = "Created and promoted" if created else "Updated"
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} "{email}": is_staff=True'
                + ("" if staff_only else ", is_superuser=True")
            )
        )
        self.stdout.write(
            "Use “Refresh permissions” on http://localhost:5173/admin or log out and log in again."
        )
