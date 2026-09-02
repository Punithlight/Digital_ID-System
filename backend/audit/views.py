from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from .models import AuditLog


@csrf_exempt
def audit_log_list(request):
    """GET /api/audit-logs/ — Super admin only."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "Authentication required"}, status=401)
    if not request.user.is_hr_admin:
        return JsonResponse({"success": False, "message": "Admin access required"}, status=403)

    qs = AuditLog.objects.select_related('user').all().order_by('-timestamp')

    search = request.GET.get('search', '')
    action = request.GET.get('action', '')
    if search:
        qs = qs.filter(user__email__icontains=search) | qs.filter(details__icontains=search)
    if action:
        qs = qs.filter(action=action)

    page_size = int(request.GET.get('page_size', 50))
    page_num = int(request.GET.get('page', 1))
    paginator = Paginator(qs, page_size)
    page = paginator.get_page(page_num)

    logs = []
    for log in page.object_list:
        logs.append({
            "id": log.id,
            "user": log.user.email if log.user else "System",
            "action": log.action,
            "model_name": log.model_name,
            "object_id": log.object_id,
            "details": log.details,
            "ip_address": log.ip_address,
            "timestamp": log.timestamp.isoformat(),
        })

    return JsonResponse({
        "success": True,
        "logs": logs,
        "total": paginator.count,
        "pages": paginator.num_pages,
        "page": page_num,
    })
