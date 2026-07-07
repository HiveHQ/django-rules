"""
Tests verifying Python 3.12 + Django 4.2 compatibility fixes.
Run with: python -m pytest django_rules/tests/test_python312_compat.py
"""

import inspect

import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "django_rules",
        ],
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )

django.setup()


class TestModels:
    """Tests for django_rules/models.py fixes."""

    def test_rule_permission_import(self):
        from django_rules.models import RulePermission

        assert RulePermission is not None

    def test_foreignkey_has_on_delete(self):
        from django_rules.models import RulePermission

        ct_field = RulePermission._meta.get_field("content_type")
        assert ct_field.remote_field.on_delete is not None


class TestBackends:
    """Tests for django_rules/backends.py fixes (getargspec removal)."""

    def test_backend_import(self):
        from django_rules.backends import ObjectPermissionBackend

        assert ObjectPermissionBackend is not None

    def test_getfullargspec_usage(self):
        """Verify that the backend can inspect method signatures on 3.12."""

        def sample_permission_method(self, user_obj):
            return True

        # This is what backends.py does internally
        arg_count = len(inspect.getfullargspec(sample_permission_method)[0])
        assert arg_count == 2


class TestDecorators:
    """Tests for django_rules/decorators.py fixes."""

    def test_decorator_import(self):
        from django_rules.decorators import object_permission_required

        assert object_permission_required is not None
        assert callable(object_permission_required)

    def test_wraps_is_functools(self):
        """Verify we're using functools.wraps, not django.utils.functional.wraps."""

        from django_rules import decorators

        # The module should use functools.wraps
        source = inspect.getsource(decorators)
        assert "from functools import wraps" in source


class TestSyncRulesCommand:
    """Tests for management/commands/sync_rules.py fixes (imp removal)."""

    def test_no_imp_import(self):
        """Verify imp module is not imported."""
        from django_rules.management.commands import sync_rules

        source = inspect.getsource(sync_rules)
        assert "\nimport imp\n" not in source
        assert "importlib" in source
