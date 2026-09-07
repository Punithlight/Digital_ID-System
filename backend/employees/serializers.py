from rest_framework import serializers
from .models import Employee, Department, Designation
from accounts.models import User


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Department
        fields = ['id', 'name', 'description']


class DesignationSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model  = Designation
        fields = ['id', 'title', 'department', 'department_name']


class EmployeeListSerializer(serializers.ModelSerializer):
    department_name   = serializers.CharField(source='department.name',   read_only=True)
    designation_title = serializers.CharField(source='designation.title', read_only=True)
    profile_photo     = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'personal_email',
            'department_name', 'designation_title',
            'joining_date', 'employment_status', 'employment_type',
            'blood_group', 'profile_photo', 'created_at',
        ]

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class EmployeeDetailSerializer(serializers.ModelSerializer):
    department_name        = serializers.CharField(source='department.name',             read_only=True)
    designation_title      = serializers.CharField(source='designation.title',           read_only=True)
    reporting_manager_name = serializers.CharField(source='reporting_manager.full_name', read_only=True)
    digital_id_number      = serializers.SerializerMethodField()
    profile_photo          = serializers.SerializerMethodField()

    class Meta:
        model  = Employee
        fields = [
            'id', 'employee_id', 'full_name', 'date_of_birth', 'gender',
            'blood_group', 'profile_photo',
            'personal_email', 'personal_phone', 'address',
            'department', 'department_name',
            'designation', 'designation_title',
            'joining_date', 'employment_type',
            'reporting_manager', 'reporting_manager_name',
            'official_email', 'employment_status',
            'digital_id_number',
            'created_at', 'updated_at',
        ]

    def get_digital_id_number(self, obj):
        try:
            return obj.digital_id_record.digital_id_number
        except Exception:
            return None

    def get_profile_photo(self, obj):
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class EmployeeCreateSerializer(serializers.Serializer):
    # Personal
    full_name     = serializers.CharField(max_length=150)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender        = serializers.ChoiceField(
        choices=['male', 'female', 'other'], required=False, allow_blank=True, default=''
    )
    blood_group   = serializers.ChoiceField(
        choices=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        required=False, allow_blank=True, default=''
    )
    # Contact
    personal_email = serializers.EmailField()
    personal_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    address        = serializers.CharField(required=False, allow_blank=True)
    # Employment
    department        = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all())
    designation       = serializers.PrimaryKeyRelatedField(queryset=Designation.objects.all())
    joining_date      = serializers.DateField()
    employment_type   = serializers.ChoiceField(
        choices=['full_time', 'part_time', 'contract', 'intern'], default='full_time'
    )
    reporting_manager = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), required=False, allow_null=True
    )
    official_email = serializers.EmailField()
    # Account
    password = serializers.CharField(min_length=8, write_only=True)

    def validate_personal_email(self, value):
        if Employee.objects.filter(personal_email__iexact=value).exists():
            raise serializers.ValidationError("An employee with this personal email already exists.")
        return value.lower()

    def validate_official_email(self, value):
        if Employee.objects.filter(official_email__iexact=value).exists():
            raise serializers.ValidationError("An employee with this official email already exists.")
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()


class EmployeeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Employee
        fields = [
            'full_name', 'date_of_birth', 'gender', 'blood_group',
            'personal_phone', 'address',
            'department', 'designation',
            'employment_type', 'reporting_manager',
            'employment_status',
        ]
