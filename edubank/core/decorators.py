from django.core.exceptions import PermissionDenied
from functools import wraps

def role_required(allowed_roles=[]):
    """
    A decorator that checks if a user has at least one of the specified roles.
    `allowed_roles` should be a list of role strings.
    e.g. @role_required(['teacher', 'lead_teacher'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Superusers should have access to everything
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.is_authenticated:
                # Check if the user has any of the allowed roles
                if request.user.roles.filter(role__in=allowed_roles).exists():
                    return view_func(request, *args, **kwargs)

            # If the user is not authenticated or doesn't have the role, deny permission.
            raise PermissionDenied
        return _wrapped_view
    return decorator
