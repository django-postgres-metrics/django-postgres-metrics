from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Permission, User
from django.test import TestCase, override_settings
from django.urls import include, re_path

urlpatterns = [
    re_path("^postgres-metrics/", include("postgres_metrics.urls")),
    re_path("^admin/", admin.site.urls),
]


@override_settings(ROOT_URLCONF=__name__)
class TestMetricsView(TestCase):
    databases = {name for name in settings.DATABASES if name != "sqlite"}

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user("user", "user@local")
        cls.superuser = User.objects.create_superuser(
            "superuser", "superuser@local", "secret"
        )
        cls.staff_denied = User.objects.create_user(
            "staff_denied", "staff_denied@local", is_staff=True
        )
        cls.staff_permitted = User.objects.create_user(
            "staff_permitted", "staff_permitted@local", is_staff=True
        )
        cls.staff_permitted.user_permissions.add(
            Permission.objects.get(codename="can_view_metric_cache_hits")
        )

    def test_anonymous_check_access(self):
        result = self.client.get("/postgres-metrics/cache-hits/")
        self.assertEqual(403, result.status_code)

    def test_authenticated_check_access(self):
        data = [
            (self.user, 403),
            (self.staff_denied, 403),
            (self.staff_permitted, 200),
            (self.superuser, 200),
        ]
        for user, expected in data:
            with self.subTest(user=user):
                self.client.force_login(user)
                result = self.client.get("/postgres-metrics/cache-hits/")
                self.assertEqual(result.status_code, expected)

    def test_anonymous_invalid_metric(self):
        result = self.client.get("/postgres-metrics/bla/")
        self.assertEqual(404, result.status_code)

    def test_authenticated_invalid_metric(self):
        data = [
            (self.user, 404),
            (self.staff_denied, 404),
            (self.staff_permitted, 404),
            (self.superuser, 404),
        ]
        for user, expected in data:
            with self.subTest(user=user):
                self.client.force_login(user)
                result = self.client.get("/postgres-metrics/bla/")
                self.assertEqual(result.status_code, expected)

    def test_anonymous_no_metric(self):
        result = self.client.get("/postgres-metrics/")
        self.assertEqual(404, result.status_code)

    def test_detail_view_sidebar(self):
        self.client.force_login(self.superuser)
        result = self.client.get("/postgres-metrics/index-size/")
        self.assertContains(
            result,
            "<h2>PostgreSQL Metrics</h2>",
            html=True,
        )
        self.assertInHTML(
            '<li><a href="/postgres-metrics/available-extensions/" '
            'title="Available Extensions">Available Extensions</a></li>',
            result.content.decode(),
        )
        self.assertInHTML(
            '<li class="selected"><a href="/postgres-metrics/index-size/" '
            'title="Index Size" aria-current="page">Index Size</a></li>',
            result.content.decode(),
        )

    def test_admin_index_list(self):
        self.client.force_login(self.superuser)
        result = self.client.get("/admin/")
        self.assertContains(
            result,
            '<th scope="row"><a href="/postgres-metrics/cache-hits/" title="Cache Hits"'
            ">Cache Hits</a></th>",
            html=True,
        )
        self.assertContains(
            result,
            '<th scope="row"><a href="/postgres-metrics/index-usage/" title="Index '
            'Usage">Index Usage</a></th>',
            html=True,
        )
