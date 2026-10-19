from functools import wraps
from flask import abort
from flask_login import current_user


def roles_required(*role_names):
    """Decorator: allow access only to users with one of the given role names."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*role_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    return roles_required('super_admin', 'college_admin')(f)


def super_admin_required(f):
    return roles_required('super_admin')(f)


def faculty_or_admin_required(f):
    return roles_required('super_admin', 'college_admin', 'dept_head', 'faculty')(f)
