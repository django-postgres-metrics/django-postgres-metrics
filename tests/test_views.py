from django.contrib import admin
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.conf.urls import include, url as path

urlpatterns = [
    path('^postgres-metrics/', include('postgres_metrics.urls')),
    path('^admin/', admin.site.urls),
]


@override_settings(ROOT_URLCONF=__name__)
class TestMetricsView(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='user1', email='user1@local', password='top_secret')

    def login(self):
        return self.client.login(username='user1', password='top_secret')

    def permit(self):
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.is_admin = True
        self.user.save()
        self.login()

    def test_unauthenticated(self):
        result = self.client.get('/postgres-metrics/aname/')
        self.assertEqual(403, result.status_code)

    def test_not_super(self):
        self.login()
        result = self.client.get('/postgres-metrics/aname/')
        self.assertEqual(403, result.status_code)

    def test_permitted_no_metric(self):
        self.permit()
        result = self.client.get('/postgres-metrics/')
        self.assertEqual(404, result.status_code)

    def test_permitted_invalid_metric(self):
        self.permit()
        result = self.client.get('/postgres-metrics/NOT_A_METRIC/')
        self.assertEqual(404, result.status_code)

    def test_permitted_metric(self):
        self.permit()
        result = self.client.get('/postgres-metrics/cache-hits/')
        self.assertEqual(200, result.status_code)
        result = self.client.get('/postgres-metrics/index-usage/')
        self.assertEqual(200, result.status_code)

    def test_metric_results(self):
        self.permit()
        result = self.client.get('/postgres-metrics/cache-hits/')
        metrics_dbs = result.context['results']
        self.assertEqual(2, len(metrics_dbs))
