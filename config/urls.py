from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),  # Esta línea es la que incluye las URLs de autenticación
    path("", include("inventory.urls")),
]

