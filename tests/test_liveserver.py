import os

import django
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.test import override_settings
from django.test.selenium import (
    SeleniumTestCase as BaseSeleniumTestCase,
    SeleniumTestCaseBase as BaseSeleniumTestCaseBase,
)
from django.urls import include, path, reverse
from django.utils.module_loading import import_string

from postgres_metrics.metrics import registry

urlpatterns = [
    path("admin/postgres-metrics/", include("postgres_metrics.urls")),
    path("admin/", admin.site.urls),
]

if django.VERSION[:2] < (3, 0):
    # Django 2.2 doesn't support webdriver options. We're therefore overriding the
    # `create_webdiver` method to include the options in the instantiation of the
    # webdriver.

    class SeleniumTestCaseBase(BaseSeleniumTestCaseBase):
        # Run browsers in headless mode.
        headless = False

        @classmethod
        def import_options(cls, browser):
            return import_string("selenium.webdriver.%s.options.Options" % browser)

        def create_options(self):
            options = self.import_options(self.browser)()
            if self.headless:
                try:
                    options.headless = True
                except AttributeError:
                    pass  # Only Chrome and Firefox support the headless mode.
            return options

        def create_webdriver(self):
            return self.import_webdriver(self.browser)(options=self.create_options())

    class SeleniumTestCase(BaseSeleniumTestCase, metaclass=SeleniumTestCaseBase):
        pass

else:
    SeleniumTestCase = BaseSeleniumTestCase


@override_settings(ROOT_URLCONF=__name__)
class MakeScreenshotTest(SeleniumTestCase):
    static_handler = StaticFilesHandler
    browsers = ["chrome"]
    headless = True
    counter = 0

    def setUp(self):
        User.objects.create_superuser("admin", "admin@localhost", "password")
        self.selenium.get("%s%s" % (self.live_server_url, reverse("admin:index")))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys("admin")
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys("password")
        self.selenium.find_element_by_xpath('//input[@value="Log in"]').click()
        os.makedirs("tests/output/", exist_ok=True)

    def make_screenshot(self, name):
        height = self.selenium.execute_script("return document.body.scrollHeight")
        old_size = self.selenium.get_window_size()
        self.selenium.set_window_size(1024, height)
        try:
            self.selenium.save_screenshot(
                "tests/output/%02d-%s.png" % (MakeScreenshotTest.counter, name)
            )
            MakeScreenshotTest.counter += 1
        finally:
            self.selenium.set_window_size(1024, old_size["height"])

    def test_make_screenshot_index(self):
        self.make_screenshot("index")

    def test_make_screenshot_metrics(self):
        for metric in registry.sorted:
            with self.subTest(slug=metric.slug):
                self.selenium.get(
                    "%s%s"
                    % (
                        self.live_server_url,
                        reverse("postgres-metrics:show", kwargs={"name": metric.slug}),
                    )
                )
                self.make_screenshot(metric.slug)
