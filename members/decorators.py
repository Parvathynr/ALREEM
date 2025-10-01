# decorators.py
import jwt
from functools import wraps
from django.conf import settings
from django.http import JsonResponse

def branch_admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JsonResponse({"status": "failed", "message": "Missing token"}, status=401)

        try:
            # Expect header in format: "Bearer <token>"
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        except (IndexError, jwt.ExpiredSignatureError, jwt.DecodeError):
            return JsonResponse({"status": "failed", "message": "Invalid or expired token"}, status=401)

        # Attach user info to request
        request.user_id = payload.get("user_id")
        request.role = payload.get("role")
        request.branch_id = payload.get("branch_id")

        # Optionally restrict access to branch_admin only
        if request.role not in ["branch_admin", "superuser"]:
            return JsonResponse({"status": "failed", "message": "Not authorized"}, status=403)

        return view_func(request, *args, **kwargs)

    return wrapper
