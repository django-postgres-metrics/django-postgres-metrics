try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from .views import STATS, stats_view

app_name = 'postgres_stats'
urlpatterns = [
    re_path(name + r'/$', stats_view, name=name, kwargs={'name': name})
    for name in STATS
]
