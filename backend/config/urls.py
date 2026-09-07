from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    # digital_id MUST come before employees because employees has a catch-all <str:employee_id>
    path("api/", include("digital_id.urls")),
    path("api/", include("integrations.urls")),
    path("api/", include("employees.urls")),
    path("api/", include("audit.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
