from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/", include("src.authentication.urls")),
    path("api/", include("src.api.urls")),
]
