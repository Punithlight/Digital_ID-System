"""
Management command: seed_data
Usage: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== Seeding Digital ID System ===\n'))

        with transaction.atomic():
            self._seed_departments()
            self._seed_designations()
            self._seed_superadmin()
            self._seed_admin()

        self.stdout.write(self.style.SUCCESS('\n✓ Seeding complete!\n'))

    def _seed_departments(self):
        from employees.models import Department
        departments = [
            ('Technology',      'Software and IT teams'),
            ('Human Resources', 'HR and Talent team'),
            ('Finance',         'Finance and Accounts team'),
            ('Operations',      'Business Operations'),
            ('Marketing',       'Marketing and Communications'),
        ]
        for name, desc in departments:
            _, created = Department.objects.get_or_create(name=name, defaults={'description': desc})
            self.stdout.write(f'  Department: {name} [{"created" if created else "exists"}]')

    def _seed_designations(self):
        from employees.models import Department, Designation
        desigs = [
            ('Python Developer',    'Technology'),
            ('Frontend Developer',  'Technology'),
            ('Full Stack Developer','Technology'),
            ('Team Lead',           'Technology'),
            ('HR Manager',          'Human Resources'),
            ('HR Executive',        'Human Resources'),
            ('Finance Manager',     'Finance'),
            ('Accountant',          'Finance'),
            ('Operations Manager',  'Operations'),
            ('Marketing Manager',   'Marketing'),
        ]
        for title, dept_name in desigs:
            dept = Department.objects.filter(name=dept_name).first()
            _, created = Designation.objects.get_or_create(title=title, defaults={'department': dept})
            self.stdout.write(f'  Designation: {title} [{"created" if created else "exists"}]')

    def _seed_superadmin(self):
        from accounts.models import User
        email = 'superadmin@flowdesk.com'
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'  Super Admin: {email} [exists]')
            return
        User.objects.create_superuser(
            email=email,
            password='superadmin',
            first_name='Super',
            last_name='Admin',
            role=User.ROLE_SUPERADMIN,
        )
        self.stdout.write(self.style.SUCCESS(
            f'  Super Admin created\n'
            f'    Email   : {email}\n'
            f'    Password: superadmin'
        ))

    def _seed_admin(self):
        from accounts.models import User
        from employees.models import Employee

        email = 'hr@flowdesk.com'
        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            self.stdout.write(f'  HR Admin user: {email} [exists]')
            user = User.objects.get(email=email)
        else:
            user = User.objects.create_user(
                email=email,
                password='Hr@1234',
                first_name='HR',
                last_name='Manager',
                role=User.ROLE_ADMIN,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS(
                f'  HR Admin created\n'
                f'    Email   : {email}\n'
                f'    Password: Hr@1234'
            ))

        # Create Employee + DigitalID if not already there
        if Employee.objects.filter(user=user).exists():
            self.stdout.write(f'  HR Employee record: [exists]')
        else:
            self._create_hr_employee(user)

    def _create_hr_employee(self, user):
        from employees.models import Employee, Department, Designation
        from digital_id.models import DigitalID

        dept  = Department.objects.filter(name='Human Resources').first()
        desig = Designation.objects.filter(title='HR Manager').first()

        employee = Employee.objects.create(
            user              = user,
            full_name         = 'HR Manager',
            personal_email    = 'hr.personal@flowdesk.com',
            personal_phone    = '+91 9000000000',
            blood_group       = 'O+',
            address           = 'Bengaluru, Karnataka',
            department        = 'Human Resources',
            designation       = 'HR EXECUTIVE',
            joining_date      = '2026-01-01',
            employment_type   = 'full_time',
            official_email    = user.email,
            employment_status = 'active',
        )

        digital_id = DigitalID.generate_for(employee)
        self.stdout.write(self.style.SUCCESS(
            f'  HR Employee record created\n'
            f'    Employee ID : {employee.employee_id}\n'
            f'    Digital ID  : {digital_id.digital_id_number}'
        ))
