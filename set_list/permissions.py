"""
Custom permission classes for the SetList API.
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsComposerOrReadOnly(BasePermission):
    """
    Custom permission: Allows read-only access to any user,
    but restricts write actions to authenticated users in the 'composer' group.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and request.user.groups.filter(name="composer").exists()
        )
