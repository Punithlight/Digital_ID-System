import uuid
from django.db import models


class DigitalID(models.Model):
    """
    Permanent Digital ID linked to an employee.
    Format: MH00{employee_id}  e.g. MH00260001
    """
    STATUS_ACTIVE   = 'ACTIVE'
    STATUS_INACTIVE = 'INACTIVE'
    STATUS_CHOICES  = [
        (STATUS_ACTIVE,   'Active'),
        (STATUS_INACTIVE, 'Inactive'),
    ]

    employee = models.OneToOneField(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='digital_id_record',
    )
    digital_id_number  = models.CharField(max_length=30, unique=True, blank=True)
    verification_token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.digital_id_number} — {self.employee.full_name}"

    # ── Generation ────────────────────────────────────────────────

    @classmethod
    def generate_for(cls, employee):
        """Create and persist a DigitalID for the given Employee instance."""
        number = f"MH00{employee.employee_id}"
        obj    = cls.objects.create(
            employee          = employee,
            digital_id_number = number,
        )
        return obj

    # ── Serialisation ─────────────────────────────────────────────

    def to_dict(self):
        emp = self.employee

        # Build photo URL safely
        photo_url = None
        if emp.profile_photo:
            try:
                photo_url = emp.profile_photo.url
            except Exception:
                photo_url = None

        return {
            "digital_id_number":  self.digital_id_number,
            "employee_id":        emp.employee_id,
            "full_name":          emp.full_name,
            "department":         emp.department.name  if emp.department  else "",
            "designation":        emp.designation.title if emp.designation else "",
            "joining_date":       str(emp.joining_date),
            "status":             self.status,
            "profile_photo":      photo_url,
            "verification_token": str(self.verification_token),
            "blood_group":        emp.blood_group or "",
            # Contact — shown on profile page, not on public card
            "personal_email":     emp.personal_email,
            "official_email":     emp.official_email,
            "personal_phone":     emp.personal_phone,
        }
