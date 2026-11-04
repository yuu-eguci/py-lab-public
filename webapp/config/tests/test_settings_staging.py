"""
config.tests.test_settings_staging
"""

import importlib
import os
from unittest import mock

from django.test import SimpleTestCase


def load_staging_settings(**env: str):
    with mock.patch.dict(os.environ, env):
        from config import settings_staging

        return importlib.reload(settings_staging)


class TestStagingSettings(SimpleTestCase):
    def test_debug_is_off(self) -> None:
        self.assertFalse(load_staging_settings().DEBUG)

    def test_allowed_hosts_from_env(self) -> None:
        settings = load_staging_settings(DJANGO_ALLOWED_HOSTS=" example.com , localhost ,")
        self.assertEqual(settings.ALLOWED_HOSTS, ["example.com", "localhost"])

    def test_allowed_hosts_default(self) -> None:
        with mock.patch.dict(os.environ):
            os.environ.pop("DJANGO_ALLOWED_HOSTS", None)
            self.assertEqual(load_staging_settings().ALLOWED_HOSTS, ["localhost"])
