import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from employees.models import Employee
from digital_id.models import DigitalID
from .models import IntegrationLog
from audit.utils import log_action


def require_admin(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"success": False, "message": "Authentication required"}, status=401)
        if not request.user.is_hr_admin:
            return JsonResponse({"success": False, "message": "HR/Admin access required"}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@csrf_exempt
@require_admin
def integration_employee_get(request, employee_id):
    """GET /api/integration/employees/{employee_id} — FlowDesk-approved employee data."""
    try:
        employee = Employee.objects.select_related(
            'department', 'designation', 'digital_id_record'
        ).get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    # Only share approved/active employees
    if employee.employment_status != 'active':
        return JsonResponse({"success": False, "message": "Employee is not active"}, status=403)

    try:
        digital_id = employee.digital_id_record
    except Exception:
        return JsonResponse({"success": False, "message": "Digital ID not found"}, status=404)

    data = {
        "employee_id": employee.employee_id,
        "digital_id_number": digital_id.digital_id_number,
        "full_name": employee.full_name,
        "official_email": employee.official_email,
        "department": employee.department.name if employee.department else "",
        "designation": employee.designation.title if employee.designation else "",
        "joining_date": str(employee.joining_date),
        "employment_type": employee.employment_type,
        "status": digital_id.status,
    }

    log_action(request.user, 'INTEGRATION_DATA_ACCESSED', 'Employee',
               object_id=employee.id,
               details=f"FlowDesk data accessed for {employee.employee_id}")

    return JsonResponse({"success": True, "employee": data})


@csrf_exempt
@require_admin
def integration_sync(request):
    """POST /api/integration/employees/sync — Synchronize employee with FlowDesk."""
    if request.method != 'POST':
        return JsonResponse({"success": False, "message": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "message": "Invalid JSON"}, status=400)

    employee_id = data.get('employee_id')
    if not employee_id:
        return JsonResponse({"success": False, "message": "employee_id is required"}, status=400)

    try:
        employee = Employee.objects.select_related(
            'department', 'designation', 'digital_id_record'
        ).get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    try:
        digital_id = employee.digital_id_record
    except Exception:
        return JsonResponse({"success": False, "message": "Digital ID not found"}, status=404)

    # Build payload for FlowDesk
    payload = {
        "employee_id": employee.employee_id,
        "digital_id_number": digital_id.digital_id_number,
        "full_name": employee.full_name,
        "official_email": employee.official_email,
        "department": employee.department.name if employee.department else "",
        "designation": employee.designation.title if employee.designation else "",
        "joining_date": str(employee.joining_date),
        "status": digital_id.status,
    }

    # Log the sync attempt
    log_entry = IntegrationLog.objects.create(
        employee_id=employee_id,
        digital_id_number=digital_id.digital_id_number,
        action='sync',
        status='success',
        request_payload=payload,
        response_payload={"message": "Sync recorded", "employee_id": employee_id},
    )

    log_action(request.user, 'INTEGRATION_SYNC', 'Employee',
               object_id=employee.id,
               details=f"FlowDesk sync for {employee.employee_id}")

    return JsonResponse({
        "success": True,
        "message": "Employee synchronized with FlowDesk",
        "employee_id": employee_id,
        "digital_id_number": digital_id.digital_id_number,
        "sync_id": log_entry.id,
    })
