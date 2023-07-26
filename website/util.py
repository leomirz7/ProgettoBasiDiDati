from functools import wraps
from flask import redirect, url_for

def restrict_user(current_user, user_type):
    def decorator(route_function):
        @wraps(route_function)
        def decorated_function(*args, **kwargs):
            if not current_user or not current_user.__class__.__name__ in str(user_type):
                return redirect(url_for('static', filename= "401.html"))
            return route_function(*args, **kwargs)
        return decorated_function
    return decorator
