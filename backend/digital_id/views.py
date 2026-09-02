from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import DigitalID
from employees.models import Employee


@csrf_exempt
def digital_id_by_employee(request, employee_id):
    """GET /api/employees/{employee_id}/digital-id/"""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

    if not request.user.is_hr_admin:
        if not hasattr(request.user, 'employee_profile') or request.user.employee_profile.employee_id != employee_id:
            return JsonResponse({"success": False, "message": "Access denied"}, status=403)

    try:
        employee = Employee.objects.select_related('department', 'designation').get(employee_id=employee_id)
    except Employee.DoesNotExist:
        return JsonResponse({"success": False, "message": "Employee not found"}, status=404)

    try:
        digital_id = DigitalID.objects.get(employee=employee)
        return JsonResponse({"success": True, "digital_id": digital_id.to_dict()})
    except DigitalID.DoesNotExist:
        return JsonResponse({"success": False, "message": "Digital ID not found"}, status=404)


@csrf_exempt
def digital_id_my(request):
    """GET /api/digital-id/my/ — Current user's digital ID."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required"}, status=401)

    try:
        employee   = request.user.employee_profile
        digital_id = DigitalID.objects.select_related('employee', 'employee__department', 'employee__designation').get(employee=employee)
        return JsonResponse({"success": True, "digital_id": digital_id.to_dict()})
    except Exception:
        return JsonResponse({"success": False, "message": "Digital ID not found. Contact HR."}, status=404)


@csrf_exempt
def verify_digital_id(request, token):
    """
    GET /api/verify/{token}/ — Public QR verification.
    Accepts UUID verification_token or Digital ID number (e.g. MH00260001).
    """
    # Try UUID token first
    digital_id = None
    import uuid as uuid_mod

    try:
        uuid_obj = uuid_mod.UUID(str(token))
        digital_id = DigitalID.objects.select_related(
            'employee', 'employee__department', 'employee__designation'
        ).get(verification_token=uuid_obj)
    except (ValueError, DigitalID.DoesNotExist):
        pass

    # Fallback: try as digital_id_number
    if digital_id is None:
        try:
            digital_id = DigitalID.objects.select_related(
                'employee', 'employee__department', 'employee__designation'
            ).get(digital_id_number__iexact=str(token))
        except DigitalID.DoesNotExist:
            pass

    if digital_id is None:
        return JsonResponse({
            "success": False,
            "verified": False,
            "message": "Invalid or unrecognised Digital ID / token."
        }, status=404)

    emp = digital_id.employee
    return JsonResponse({
        "success":  True,
        "verified": True,
        "employee": {
            "full_name":         emp.full_name,
            "employee_id":       emp.employee_id,
            "digital_id_number": digital_id.digital_id_number,
            "department":        emp.department.name if emp.department else "",
            "designation":       emp.designation.title if emp.designation else "",
            "status":            digital_id.status,
            "joining_date":      str(emp.joining_date),
        }
    })
