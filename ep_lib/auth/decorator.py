from functools import wraps
from flask import request
from loguru import logger
from ep_lib.auth.auth_helper import AuthHelper

ROUTES_TO_SKIP = [
    "/auth/login",
    "/auth/register",
    "/auth/logout",
    "/auth/refresh",
    "/auth/forgot_password",
    "/auth/reset-password",
    
    # health check
    "/auth/halth",
    "/api/health",
]


def token_required(portal_user=False, roles=None, accept_both=False):
    """
    Decorator to protect routes with JWT.
    - portal_user: if True, uses AuthHelper.get_logged_in_portal_user
                   else uses AuthHelper.get_logged_in_user
    - roles: list/set of roles required to access the route
    - accept_both: if True, tries both portal_user and regular user authentication
                   (useful for endpoints used by both ep-fo and ep-bo)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Skip authentication for specified routes, swagger, and OPTIONS requests
            if request.path in ROUTES_TO_SKIP or "swagger" in request.path or request.method == "OPTIONS":
                return f(*args, **kwargs)

            try:
                if 'Authorization' not in request.headers:
                    return {"message": "Token is missing"}, 401
                
                data = None
                status = None
                
                # If accept_both is True
                if accept_both:
                    # Try portal_user authentication first
                    try:
                        data, status = AuthHelper.get_logged_in_portal_user(request)
                        if status == 200 and data.get('data'):
                            pass
                        else:
                            # Portal user failed, try regular user
                            data, status = AuthHelper.get_logged_in_user(request)
                    except Exception:
                        # If portal_user auth fails, try regular user
                        try:
                            data, status = AuthHelper.get_logged_in_user(request)
                        except Exception as e:
                            logger.debug(f"Both authentication methods failed: {str(e)}")
                            return {"message": "Invalid token"}, 401
                else:
                    # Fetch logged-in user data based on portal_user flag
                    if portal_user:
                        data, status = AuthHelper.get_logged_in_portal_user(request)
                    else:
                        data, status = AuthHelper.get_logged_in_user(request)
                
                # Check authentication status
                if status != 200:
                    return {"message": "Invalid token"}, 401

                token = data.get('data')
                if token is None:
                    return {"message": "Token is missing"}, 401

                # Check if the token has the required role
                if roles is None:
                    return f(*args, **kwargs)

                user_role = token.get('role')
                if user_role not in roles:
                    return {"message": "Permission denied"}, 403
                    
                return f(*args, **kwargs)
            
            except Exception as e:
                logger.debug(f"Authentication error: {str(e)}")
                return {"message": f"Authentication error: {str(e)}"}, 401
        return decorated_function
    return decorator