from functools import wraps
from flask import request
from loguru import logger
from ep_lib.auth.auth_helper import AuthHelper
from ep_lib.auth.role_helper import RoleHelper



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

                user_role = token.get("role")

                # ─── ADMIN BYPASS ───────────────────────────
                if user_role == ADMIN_ROLE:
                    return f(*args, **kwargs)

                # ─── ROLE CHECK (optional) ──────────────────
                if roles is not None:
                    if user_role not in roles:
                        return {"message": "Permission denied (role)"}, 403

                # ─── SCREEN / MODE CHECK (optional) ─────────
                if screen is not None or mode is not None:
                    role = RoleHelper.get_role_by_name(user_role)

                    # Screen check
                    if screen is not None:
                        if not screen_allowed(role.screens, screen):
                            return {
                                "message": f"Access denied to screen '{screen}'"
                            }, 403

                    # Mode check
                    if mode is not None:
                        required = MODE_HIERARCHY.get(mode)
                        actual = MODE_HIERARCHY.get(role.mode)

                        if required is None or actual is None:
                            return {"message": "Invalid mode configuration"}, 500

                        if actual < required:
                            return {
                                "message": "Insufficient permission level"
                            }, 403

                return f(*args, **kwargs)

            except Exception:
                logger.exception("Authentication / Authorization error")
                return {"message": "Authentication error"}, 401

        return decorated_function
    return decorator




def screen_allowed(role_screens, requested_screens):
    """Check if any of the requested screens are allowed by the role's screens."""
    if isinstance(requested_screens, str):
        requested_screens = [requested_screens]

    for requested in requested_screens:
        for allowed in role_screens:
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

