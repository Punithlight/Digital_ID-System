from django.urls import path
from .views import audit_log_list

urlpatterns = [
    path("audit-logs/", audit_log_list, name="audit-logs"),
]
