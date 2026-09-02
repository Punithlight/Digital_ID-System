from django.contrib import admin
from .models import Employee, Department, Designation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'created_at']
    search_fields = ['name']


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'created_at']
    list_filter = ['department']
    search_fields = ['title']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'department', 'designation', 'employment_status', 'joining_date', 'created_at']
    list_filter = ['employment_status', 'department', 'employment_type']
    search_fields = ['employee_id', 'full_name', 'personal_email', 'official_email']
    readonly_fields = ['employee_id', 'created_at', 'updated_at']
