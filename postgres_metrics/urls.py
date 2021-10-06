from django.urls import re_path

from .views import metrics_view

app_name = "postgres-metrics"
urlpatterns = [
    re_path(r"(?P<name>[a-zA-Z0-9_-]+)/$", metrics_view, name="show"),
]
