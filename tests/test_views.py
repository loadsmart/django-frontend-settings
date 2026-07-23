import re

import pytest
import waffle
from django.contrib.auth.models import Group
from django.db import connection
from django.test.utils import CaptureQueriesContext
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


@pytest.mark.django_db
def test_avoids_n_plus_one_on_user_groups(client):
    prefix = settings.WAFFLE_FLAG_PREFIX
    user = UserFactory.create()
    group = Group.objects.create(name="frontend-settings-group")
    user.groups.add(group)

    for index in range(5):
        flag = FlagFactory.create(name=f"{prefix}GROUP_FLAG_{index}")
        flag.groups.add(group)

    client.force_login(user)

    with CaptureQueriesContext(connection) as captured:
        response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert all(response.data["flags"].values())

    user_group_queries = [
        query
        for query in captured.captured_queries
        if re.search(r"\bauth_user_groups\b", query["sql"], re.IGNORECASE)
    ]
    assert len(user_group_queries) <= 2


def _select_queries_matching(captured, pattern: str):
    return [
        query
        for query in captured.captured_queries
        if re.search(pattern, query["sql"], re.IGNORECASE)
        and re.search(r"^\s*SELECT\b", query["sql"], re.IGNORECASE)
    ]


@pytest.mark.django_db
def test_avoids_n_plus_one_on_flag_evaluation(client):
    """
    Batch-load FRONTEND_* flags once (plus M2M prefetch) instead of one
    Flag.get() / Redis round-trip per flag via waffle.flag_is_active.
    """
    prefix = settings.WAFFLE_FLAG_PREFIX
    user = UserFactory.create()
    group = Group.objects.create(name="frontend-settings-batch-group")
    user.groups.add(group)

    flag_count = 12
    for index in range(flag_count):
        flag = FlagFactory.create(name=f"{prefix}BATCH_FLAG_{index}")
        flag.groups.add(group)

    client.force_login(user)

    with CaptureQueriesContext(connection) as captured:
        response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["flags"]) >= flag_count
    assert all(
        response.data["flags"][f"BATCH_FLAG_{index}"] for index in range(flag_count)
    )

    # Primary flag table: a single filtered SELECT (not one get-by-name per flag).
    primary_flag_selects = _select_queries_matching(
        captured, r'FROM\s+"?waffle_flag"?\s'
    )
    assert len(primary_flag_selects) == 1

    # M2M membership loaded in bulk via prefetch_related, not per flag.
    flag_users_selects = _select_queries_matching(captured, r"\bwaffle_flag_users\b")
    flag_groups_selects = _select_queries_matching(captured, r"\bwaffle_flag_groups\b")
    assert len(flag_users_selects) <= 1
    assert len(flag_groups_selects) <= 1


@pytest.mark.django_db
def test_flag_query_count_does_not_grow_with_flag_count(client):
    prefix = settings.WAFFLE_FLAG_PREFIX
    user = UserFactory.create()
    client.force_login(user)

    def measure(count: int) -> int:
        FlagModel = waffle.get_waffle_flag_model()
        FlagModel.objects.filter(name__startswith=f"{prefix}SCALE_").delete()
        for index in range(count):
            FlagFactory.create(name=f"{prefix}SCALE_{index}", everyone=True)

        with CaptureQueriesContext(connection) as captured:
            response = client.get(url)

        assert response.status_code == status.HTTP_200_OK
        return len(captured.captured_queries)

    few = measure(3)
    many = measure(15)
    # Bounded evaluation: adding flags must not add a linear number of queries.
    assert many - few <= 2
