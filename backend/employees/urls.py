from django.urls import path
from .views import employee_list_create, employee_detail, department_list, designation_list

urlpatterns = [
    path("employees/", employee_list_create, name="employee-list-create"),
    path("employees/<str:employee_id>/", employee_detail, name="employee-detail"),
    path("departments/", department_list, name="department-list"),
    path("designations/", designation_list, name="designation-list"),
]
