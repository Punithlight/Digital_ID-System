from django.contrib import admin
from .models import DigitalID


@admin.register(DigitalID)
class DigitalIDAdmin(admin.ModelAdmin):
    list_display = ['digital_id_number', 'employee', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['digital_id_number', 'employee__full_name', 'employee__employee_id']
    readonly_fields = ['digital_id_number', 'verification_token', 'created_at', 'updated_at']
