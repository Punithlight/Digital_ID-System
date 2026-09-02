import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db import transaction, models as django_models
from .models import Employee, Department, Designation
from .serializers import (
    EmployeeListSerializer, EmployeeDetailSerializer,
    EmployeeCreateSerializer, EmployeeUpdateSerializer,
    DepartmentSerializer, DesignationSerializer,
)
from accounts.models import User
from audit.utils import log_action


# ─── helpers ──────────────────────────────────────────────────────

def _is_auth(request):
    return request.user.is_authenticated

def _is_admin(request):
    return request.user.is_authenticated and request.user.is_hr_admin

def _unauth():
    return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

def _forbidden(msg="Access denied"):
    return JsonResponse({"success": False, "message": msg}, status=403)


# ─── /api/employees/ ──────────────────────────────────────────────

@csrf_exempt
def employee_list_create(request):
    """
    GET  /api/employees/  — list (admin only)
    POST /api/employees/  — create employee + digital ID (admin only)
    """
    if not _is_auth(request):
        return _unauth()
    if not _is_admin(request):
        return _forbidden("HR/Admin access required")

    # ── GET ──
    if request.method == 'GET':
        qs = Employee.objects.select_related('department', 'designation').order_by('-created_at')

        search = request.GET.get('search', '').strip()
        status = request.GET.get('status', '').strip()
        dept   = request.GET.get('department', '').strip()

        if search:
            qs = qs.filter(
                django_models.Q(full_name__icontains=search) |
                django_models.Q(employee_id__icontains=search) |
                django_models.Q(personal_email__icontains=search) |
                django_models.Q(official_email__icontains=search)
            )
        if status:
            qs = qs.filter(employment_status=status)
        if dept:
            qs = qs.filter(department__id=dept)

        page_size = min(int(request.GET.get('page_size', 20)), 100)
        page_num  = max(int(request.GET.get('page', 1)), 1)
        paginator = Paginator(qs, page_size)
        page      = paginator.get_page(page_num)

        return JsonResponse({
            "success":   True,
            "employees": EmployeeListSerializer(page.object_list, many=True).data,
            "total":     paginator.count,
            "pages":     paginator.num_pages,
            "page":      page_num,
        })

    # ── POST ──
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        serializer = EmployeeCreateSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse({"success": False, "errors": serializer.errors}, status=400)

        v = serializer.validated_data
        try:
            with transaction.atomic():
                parts = v['full_name'].split()
                user  = User.objects.create_user(
                    email      = v['official_email'],
                    password   = v['password'],
                    first_name = parts[0],
                    last_name  = ' '.join(parts[1:]) if len(parts) > 1 else '',
                    role       = User.ROLE_EMPLOYEE,
                )
                employee = Employee.objects.create(
                    user              = user,
                    full_name         = v['full_name'],
                    date_of_birth     = v.get('date_of_birth'),
                    gender            = v.get('gender', ''),
                    personal_email    = v['personal_email'],
                    personal_phone    = v.get('personal_phone', ''),
                    address           = v.get('address', ''),
                    department        = v['department'],
                    designation       = v['designation'],
                    joining_date      = v['joining_date'],
                    employment_type   = v.get('employment_type', 'full_time'),
                    reporting_manager = v.get('reporting_manager'),
                    official_email    = v['official_email'],
                )
                from digital_id.models import DigitalID
                digital_id = DigitalID.generate_for(employee)

                log_action(
                    request.user, 'EMPLOYEE_CREATED', 'Employee',
                    object_id=employee.id,
                    details=f"Created {employee.employee_id} — {employee.full_name}",
                )

            return JsonResponse({
                "success":    True,
                "message":    "Employee created successfully",
                "employee":   EmployeeDetailSerializer(employee).data,
                "digital_id": digital_id.digital_id_number,
            }, status=201)

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)}, status=500)

    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)


# ─── /api/employees/{employee_id}/ ────────────────────────────────

@csrf_exempt
def employee_detail(request, employee_id):
    """
    GET   /api/employees/{employee_id}/  — view (admin or own profile)
    PATCH /api/employees/{employee_id}/  — update (admin only)
    """
    if not _is_auth(request):
        return _unauth()

    try:
        employee = Employee.objects.select_related(
            'department', 'designation', 'reporting_manager'
        ).get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    # Employees can only see their own record
    if not _is_admin(request):
        own = getattr(request.user, 'employee_profile', None)
        if own is None or own.employee_id != employee_id:
            return _forbidden()

    if request.method == 'GET':
        return JsonResponse({"success": True, "employee": EmployeeDetailSerializer(employee).data})

    elif request.method == 'PATCH':
        if not _is_admin(request):
            return _forbidden("HR/Admin access required")

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

        serializer = EmployeeUpdateSerializer(employee, data=data, partial=True)
        if not serializer.is_valid():
            return JsonResponse({"success": False, "errors": serializer.errors}, status=400)

        serializer.save()
        log_action(
            request.user, 'EMPLOYEE_UPDATED', 'Employee',
            object_id=employee.id,
            details=f"Updated {employee.employee_id}",
        )

        # Sync digital ID status when employment_status changes
        if 'employment_status' in data:
            try:
                from digital_id.models import DigitalID
                did = DigitalID.objects.get(employee=employee)
                did.status = 'ACTIVE' if employee.employment_status == 'active' else 'INACTIVE'
                did.save()
            except Exception:
                pass

        return JsonResponse({
            "success":  True,
            "message":  "Employee updated successfully",
            "employee": EmployeeDetailSerializer(employee).data,
        })

    return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)


# ─── /api/departments/ ────────────────────────────────────────────

@csrf_exempt
def department_list(request):
    """GET /api/departments/ — public list (used in register form dropdowns)."""
    if not _is_auth(request):
        return _unauth()
    depts = Department.objects.all().order_by('name')
    return JsonResponse({"success": True, "departments": DepartmentSerializer(depts, many=True).data})


# ─── /api/designations/ ───────────────────────────────────────────

@csrf_exempt
def designation_list(request):
    """GET /api/designations/ — public list (used in register form dropdowns)."""
    if not _is_auth(request):
        return _unauth()
    designations = Designation.objects.select_related('department').all().order_by('title')
    return JsonResponse({"success": True, "designations": DesignationSerializer(designations, many=True).data})
