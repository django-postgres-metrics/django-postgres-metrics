from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/postgres-metrics/", include("postgres_metrics.urls")),
    path("admin/", admin.site.urls),
]
