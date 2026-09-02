from django.contrib import admin
from .models import IntegrationLog


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'employee_id', 'digital_id_number', 'action', 'status']
    list_filter = ['status', 'action']
    search_fields = ['employee_id', 'digital_id_number']
    readonly_fields = ['created_at']
