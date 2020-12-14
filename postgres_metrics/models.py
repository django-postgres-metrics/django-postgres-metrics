from django.db import models

from .metrics import registry


class Metric(models.Model):
    class Meta:
        default_permissions = []
        permissions = [
            (metric.permission_name, "Can view metric %s" % metric.label)
            for metric in registry
        ]
