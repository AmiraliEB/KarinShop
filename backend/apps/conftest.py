import pytest


@pytest.fixture
def user_factory(db, django_user_model):
    def _create_user(username="testuser", password="password123"):
        user = django_user_model.objects.create_user(username=username, password=password)
        return user

    return _create_user


@pytest.fixture(autouse=True)
def disable_debug_toolbar(settings):
    settings.DEBUG_TOOLBAR_CONFIG = {
        "SHOW_TOOLBAR_CALLBACK": lambda request: False,
    }
    settings.MIDDLEWARE = [m for m in settings.MIDDLEWARE if "debug_toolbar" not in m]
