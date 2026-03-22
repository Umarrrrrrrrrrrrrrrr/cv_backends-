"""Shared DRF permission classes."""
from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Only authenticated staff (is_staff) may access the view."""

    message = 'You must be a staff user to access this resource.'

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )
