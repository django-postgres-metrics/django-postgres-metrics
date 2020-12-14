"""example URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/dev/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import django
from django.contrib import admin

if django.VERSION >= (2, 0):
    from django.urls import include, path

    urlpatterns = [
        path("admin/postgres-metrics/", include("postgres_metrics.urls")),
        path("admin/", admin.site.urls),
    ]
else:
    # Remove when dropping Django 1.11
    from django.conf.urls import include, url

    urlpatterns = [
        url(r"^admin/postgres-metrics/", include("postgres_metrics.urls")),
        url(r"^admin/", admin.site.urls),
    ]
