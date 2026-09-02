from django.urls import path
from .views import digital_id_by_employee, digital_id_my, verify_digital_id

urlpatterns = [
    path("digital-id/my/", digital_id_my, name="digital-id-my"),
    path("employees/<str:employee_id>/digital-id/", digital_id_by_employee, name="digital-id-by-employee"),
    path("verify/<str:token>/", verify_digital_id, name="verify-digital-id"),
]
