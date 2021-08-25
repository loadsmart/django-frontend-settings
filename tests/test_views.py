import pytest
from django.urls import reverse
from rest_framework import status

from frontend_settings.settings import settings
from tests.factories import FlagFactory, UserFactory

url = reverse("settings")


@pytest.fixture
def user():
    return UserFactory.create()


@pytest.fixture
def flags(user):
    prefix = settings.WAFFLE_FLAG_PREFIX
    enabled = FlagFactory.create(name=f"{prefix}ENABLED", everyone=True)
    disabled = FlagFactory.create(name=f"{prefix}DISABLED", everyone=False)
    not_in_response = FlagFactory.create(name="NOT_IN_RESPONSE", everyone=True)
    only_for_admin = FlagFactory.create(name=f"{prefix}ADMIN", superusers=True)
    only_for_user = FlagFactory.create(name=f"{prefix}USER", superusers=False)
    only_for_user.users.set([user])

    return {
        "enabled": enabled,
        "disabled": disabled,
        "not_in_response": not_in_response,
        "only_for_admin": only_for_admin,
        "only_for_user": only_for_user,
    }


@pytest.mark.django_db
def test_returns_ok(client):
    response = client.get(url, format="json")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@pytest.mark.usefixtures("flags")
def test_returns_feature_flags_for_no_user(client):
    response = client.get(url)

    assert response.data["flags"]["ADMIN"] is False
    assert response.data["flags"]["USER"] is False
    assert response.data["flags"]["ENABLED"] is True
    assert response.data["flags"]["DISABLED"] is False
    assert response.data["flags"].get("NOT_IN_RESPONSE") is None


@pytest.mark.django_db
@pytest.mark.usefixtures("flags")
def test_returns_feature_flags_for_admin(admin_client):
    response = admin_client.get(url)

    assert response.data["flags"]["ADMIN"] is True
    assert response.data["flags"]["USER"] is False
    assert response.data["flags"]["ENABLED"] is True
    assert response.data["flags"]["DISABLED"] is False
    assert response.data["flags"].get("NOT_IN_RESPONSE") is None


@pytest.mark.django_db
@pytest.mark.usefixtures("flags")
def test_returns_feature_flags_for_user(client, user):
    client.force_login(user)
    response = client.get(url)

    assert response.data["flags"]["ADMIN"] is False
    assert response.data["flags"]["USER"] is True
    assert response.data["flags"]["ENABLED"] is True
    assert response.data["flags"]["DISABLED"] is False
    assert response.data["flags"].get("NOT_IN_RESPONSE") is None


@pytest.mark.django_db
def test_return_settings(client):
    response = client.get(url)
    data = response.data["settings"]

    assert data["SETTING_AAA"] == "VALUE AAA"
    assert data["SETTING_BBB"] == "VALUE BBB"
    assert data["SETTING_CCC"] == "VALUE CCC"
    assert "NOT_FRONTEND" not in data
