import pytest


@pytest.fixture
def user_factory(db, django_user_model):
    def _create_user(username="testuser", password="password123"):
        user = django_user_model.objects.create_user(username=username, password=password)
        return user

    return _create_user
