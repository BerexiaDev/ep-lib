from functools import wraps
from flask import request
from loguru import logger
from ep_lib.auth.auth_helper import AuthHelper
from ep_lib.auth.role_helper import RoleHelper
from flask import current_app
from ep_lib.services.recaptch_service import verify_captcha



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

ADMIN_ROLE = "ADMIN"

MODE_HIERARCHY = {
    "READ": 1,
    "WRITE": 2
}

def token_required(
    roles=None,
    portal_user=False,
    accept_both=False,
    screen=None,
    mode=None
):
    """
    JWT Authentication & Authorization decorator

    Parameters (all optional):
    - roles: list of allowed roles
    - portal_user: authenticate as portal user
    - accept_both: accept portal OR back-office user
    - screen: screen permission (hierarchical)
    - mode: READ / WRITE
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            # ─── SKIP PUBLIC ROUTES ─────────────────────────
            if (
                request.path in ROUTES_TO_SKIP
                or "swagger" in request.path
                or request.method == "OPTIONS"
            ):
                return f(*args, **kwargs)

            try:
                # ─── TOKEN CHECK ────────────────────────────
                if "Authorization" not in request.headers:
                    return {"message": "Token is missing"}, 401

                # ─── AUTHENTICATION ─────────────────────────
                if accept_both:
                    try:
                        data, status = AuthHelper.get_logged_in_portal_user(request)
                        if status != 200:
                            data, status = AuthHelper.get_logged_in_user(request)
                    except Exception:
                        data, status = AuthHelper.get_logged_in_user(request)
                else:
                    if portal_user:
                        data, status = AuthHelper.get_logged_in_portal_user(request)
                    else:
                        data, status = AuthHelper.get_logged_in_user(request)

                if status != 200:
                    return {"message": "Invalid token"}, 401

                token = data.get("data")
                if not token:
                    return {"message": "Invalid token payload"}, 401

                # Get user role array
                user_roles = token.get("role", [])
                
                # Ensure it's a list
                if not isinstance(user_roles, list):
                    user_roles = [user_roles] if user_roles else []

                # ─── ADMIN BYPASS ───────────────────────────
                if ADMIN_ROLE in user_roles:
                    return f(*args, **kwargs)

                # ─── ROLE CHECK (optional) ──────────────────
                if roles is not None:
                    # Check if ANY of user's roles match required roles
                    if not any(role in roles for role in user_roles):
                        return {"message": "Permission denied (role)"}, 401

                # ─── SCREEN / MODE CHECK (optional) ─────────
                if screen is not None or mode is not None:
                    screen_access_granted = False
                    mode_access_granted = False
                    
                    # Check across ALL user roles - grant if ANY role has permission
                    for role_name in user_roles:
                        try:
                            role = RoleHelper.get_role_by_name(role_name)
                            if not role:
                                continue
                            
                            # Screen check - grant if ANY role has access
                            if screen is not None:
                                role_screens = role.screens or []
                                if screen_allowed(role_screens, screen):
                                    screen_access_granted = True
                            
                            # Mode check - grant if ANY role has sufficient mode
                            if mode is not None:
                                required = MODE_HIERARCHY.get(mode)
                                actual = MODE_HIERARCHY.get(role.mode) if role.mode else None
                                
                                if required is not None and actual is not None:
                                    if actual >= required:
                                        mode_access_granted = True
                        except Exception as e:
                            logger.warning(f"Error checking role {role_name}: {str(e)}")
                            continue
                    
                    # Final permission checks
                    if screen is not None and not screen_access_granted:
                        return {
                            "message": f"Access denied to this resource"
                        }, 401
                    
                    if mode is not None and not mode_access_granted:
                        return {
                            "message": "Insufficient permission level"
                        }, 401

                return f(*args, **kwargs)

            except Exception:
                logger.exception("Authentication / Authorization error")
                return {"message": "Authentication error"}, 401

        return decorated_function
    return decorator




def screen_allowed(role_screens, requested_screens):
    """
    Check if requested screens are allowed based on role screens.
    Handles None/empty role_screens gracefully.
    """
    if not role_screens:
        return False
    
    if isinstance(requested_screens, str):
        requested_screens = [requested_screens]
    
    if not isinstance(role_screens, list):
        role_screens = [role_screens] if role_screens else []

    for requested in requested_screens:
        for allowed in role_screens:
            if not allowed:
                continue
            # Exact match
            if requested == allowed:
                return True
            # Requested is a child of allowed
            if requested.startswith(f"{allowed}."):
                return True
            # Allowed is a child of requested (reverse)
            if allowed.startswith(f"{requested}."):
                return True
    return False


def service_token_required(header_name="X-Internal-Token"):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            SERVICE_TOKEN = current_app.config.get("INTERNAL_TOKEN")
            token = request.headers.get(header_name)
            if not token or token != SERVICE_TOKEN:
                return {"message": "Access denied"}, 401
            return f(*args, **kwargs)
        return wrapper
    return decorator


def require_recaptcha(token_field: str = "recaptcha_token"):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            body = request.get_json(silent=True) or {}
            token = body.get(token_field)

            is_token_valid = verify_captcha(token)
            if not token or not is_token_valid:
                return {
                    "status": "fail",
                    "message": "CAPTCHA invalide ou manquant. Veuillez réessayer."
                }, 400

            return fn(*args, **kwargs)
        return wrapper
    return decorator