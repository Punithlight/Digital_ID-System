from .models import AuditLog


def log_action(user, action, model_name='', object_id=None, details='', ip_address=None):
    """Helper to create an audit log entry."""
    try:
        AuditLog.objects.create(
            user=user,
            action=action,
            model_name=model_name,
            object_id=object_id,
            details=details,
            ip_address=ip_address,
        )
    except Exception:
        pass  # Never let audit logging break the main flow
