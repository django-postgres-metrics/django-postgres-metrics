try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path

from .views import stats_view

app_name = 'postgres-stats'
urlpatterns = [
    re_path(r'(?P<name>[a-zA-Z0-9_-]+)/$', stats_view, name='show')
]
