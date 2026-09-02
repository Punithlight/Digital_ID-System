from django.urls import path
from .views import integration_employee_get, integration_sync

urlpatterns = [
    # sync must be listed BEFORE the <employee_id> pattern
    path("integration/employees/sync/", integration_sync, name="integration-sync"),
    path("integration/employees/<str:employee_id>/", integration_employee_get, name="integration-employee-get"),
]
