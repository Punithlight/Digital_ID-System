from django.db import models


class IntegrationLog(models.Model):
    """FlowDesk synchronization tracking."""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]

    employee_id = models.CharField(max_length=30)
    digital_id_number = models.CharField(max_length=30, blank=True)
    action = models.CharField(max_length=50)  # sync, create, update
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_payload = models.JSONField(null=True, blank=True)
    response_payload = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.created_at} | {self.employee_id} | {self.action} | {self.status}"
