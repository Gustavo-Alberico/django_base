from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("rest_framework.urls")),
    path("admin/", admin.site.urls),
    path("api/auth/", include("account.auth_urls")),
    path("api/account/", include("account.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
