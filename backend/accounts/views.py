import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from .models import User, LoginSession


def get_client_ip(request):
    xff = request.META.get('HTTP_X_FORWARDED_FOR')
    if xff:
        return xff.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


# ─── POST /api/auth/login/ ────────────────────────────────────────

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return JsonResponse({"success": False, "message": "Email and password are required"}, status=400)

    from audit.utils import log_action

    user = authenticate(request, email=email, password=password)

    if user is None:
        # Log failed login
        try:
            u = User.objects.filter(email=email).first()
            if u:
                log_action(u, 'LOGIN_FAILED', 'LoginSession',
                           ip_address=get_client_ip(request),
                           details=f"Failed login from {get_client_ip(request)}")
        except Exception:
            pass
        return JsonResponse({"success": False, "message": "Invalid email or password"}, status=401)

    if not user.is_active:
        return JsonResponse({"success": False, "message": "Account is inactive. Contact HR."}, status=403)

    # Block inactive employees from logging in
    try:
        from employees.models import Employee
        emp = Employee.objects.filter(user=user).first()
        if emp and emp.employment_status not in ('active',):
            return JsonResponse(
                {"success": False, "message": "Your employee account is not active. Contact HR."},
                status=403
            )
    except Exception:
        pass

    # Django login — creates session
    login(request, user)

    # Ensure session is saved so session_key is available
    if not request.session.session_key:
        request.session.create()

    # Record login session
    try:
        expires_at = timezone.now() + timedelta(hours=8)
        LoginSession.objects.create(
            user       = user,
            session_key= request.session.session_key,
            ip_address = get_client_ip(request),
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:400],
            expires_at = expires_at,
        )
        log_action(user, 'LOGIN_SUCCESS', 'LoginSession',
                   ip_address=get_client_ip(request),
                   details=f"Login from {get_client_ip(request)}")
    except Exception:
        pass

    return JsonResponse({
        "success": True,
        "message": "Login successful!",
        "user": {
            "id":    user.id,
            "email": user.email,
            "role":  user.role,
            "name":  f"{user.first_name} {user.last_name}".strip() or user.email,
        },
    })


# ─── POST /api/auth/logout/ ───────────────────────────────────────

@csrf_exempt
def logout_view(request):
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    if request.user.is_authenticated:
        try:
            from audit.utils import log_action
            log_action(request.user, 'LOGOUT', 'LoginSession',
                       ip_address=get_client_ip(request),
                       details="User logged out")
            if request.session.session_key:
                LoginSession.objects.filter(
                    user=request.user,
                    session_key=request.session.session_key,
                ).update(is_active=False)
        except Exception:
            pass
        logout(request)

    return JsonResponse({"success": True, "message": "Logged out successfully"})


# ─── GET /api/auth/me/ ────────────────────────────────────────────

@csrf_exempt
def me_view(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Not authenticated"}, status=401)

    user = request.user
    payload = {
        "id":    user.id,
        "email": user.email,
        "role":  user.role,
        "name":  f"{user.first_name} {user.last_name}".strip() or user.email,
    }

    try:
        from employees.models import Employee
        emp = Employee.objects.select_related('department', 'designation').filter(user=user).first()
        if emp:
            payload['employee_id']  = emp.employee_id
            payload['full_name']    = emp.full_name
            payload['department']   = emp.department.name if emp.department else ''
            payload['designation']  = emp.designation.title if emp.designation else ''
    except Exception:
        pass

    return JsonResponse({"success": True, "user": payload})
