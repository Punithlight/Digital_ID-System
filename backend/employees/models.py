from django.db import models
from django.conf import settings


class Department(models.Model):
    """Department reference data."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Designation(models.Model):
    """Designation reference data."""
    title = models.CharField(max_length=100, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='designations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Employee(models.Model):
    """Full employee profile — separated from auth (User model)."""

    GENDER_CHOICES = [('male', 'Male'), ('female', 'Female'), ('other', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    EMPLOYMENT_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('intern', 'Intern'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('suspended', 'Suspended'),
        ('terminated', 'Terminated'),
    ]

    # Link to auth user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='employee_profile',
        null=True, blank=True
    )

    # System generated
    employee_id = models.CharField(max_length=30, unique=True, blank=True)

    # Personal information
    full_name = models.CharField(max_length=150)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    profile_photo = models.ImageField(upload_to='employees/photos/', blank=True, null=True)

    # Contact information
    personal_email = models.EmailField(unique=True)
    personal_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    # Employment information
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True)
    joining_date = models.DateField()
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES, default='full_time')
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    official_email = models.EmailField(unique=True, blank=True)
    employment_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee_id} — {self.full_name}"

    def save(self, *args, **kwargs):
        # Auto-generate employee_id if not set
        if not self.employee_id:
            self.employee_id = self._generate_employee_id()
        super().save(*args, **kwargs)

    def _generate_employee_id(self):
        """Generate next sequential employee ID starting from 260001."""
        last = Employee.objects.order_by('-id').first()
        if last and last.employee_id and last.employee_id.isdigit():
            return str(int(last.employee_id) + 1)
        # Start from 260001
        existing = Employee.objects.filter(employee_id__regex=r'^\d+$').order_by('-employee_id').first()
        if existing:
            try:
                return str(int(existing.employee_id) + 1)
            except ValueError:
                pass
        return '260001'
