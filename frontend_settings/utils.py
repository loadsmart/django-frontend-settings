from typing import Any, Dict, Iterable

import waffle
from constance import config as constance_config
from django.http import HttpRequest

from frontend_settings.settings import settings


class _CachedGroupsQuerySet:
    def __init__(self, group_ids):
        self._group_ids = group_ids

    def values_list(self, field_name, flat=False):
        if field_name == "pk" and flat:
            return list(self._group_ids)
        raise NotImplementedError


class _CachedGroupsManager:
    def __init__(self, group_ids):
        self._group_ids = group_ids

    def all(self):
        return _CachedGroupsQuerySet(self._group_ids)


class _CachedUser:
    def __init__(self, user, group_ids):
        self._user = user
        self.groups = _CachedGroupsManager(group_ids)

    def __getattr__(self, key):
        return getattr(self._user, key)


class _CachedRequest:
    def __init__(self, request, user):
        self._request = request
        self.user = user

    def __getattr__(self, key):
        return getattr(self._request, key)


def _request_with_cached_user_groups(request: HttpRequest) -> HttpRequest:
    """Evaluate flags without re-querying request.user.groups per flag."""
    user = getattr(request, "user", None)
    if not (user and user.is_authenticated):
        return request

    group_ids = tuple(user.groups.all().values_list("pk", flat=True))
    return _CachedRequest(request, _CachedUser(user, group_ids))


def _bind_prefetched_membership(flag) -> None:
    """
    Point waffle's per-flag users/groups lookups at already-prefetched M2M rows.

    ``Flag.is_active`` normally calls ``_get_user_ids`` / ``_get_group_ids``, which
    each do a Redis ``GET`` (and possibly a DB query). After ``prefetch_related``,
    iterating ``flag.users`` / ``flag.groups`` is in-memory; binding those id sets
    keeps ``is_active`` off the N+1 Redis path while reusing waffle's evaluation.
    """
    if not hasattr(flag, "_get_user_ids") or not hasattr(flag, "_get_group_ids"):
        return

    user_ids = frozenset(user.pk for user in flag.users.all())
    group_ids = frozenset(group.pk for group in flag.groups.all())

    # Default-arg binding avoids accidental late closure capture if refactored.
    flag._get_user_ids = lambda ids=user_ids: ids
    flag._get_group_ids = lambda ids=group_ids: ids


def _evaluate_flags(flags: Iterable, request: HttpRequest, prefix: str) -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    for flag in flags:
        _bind_prefetched_membership(flag)
        key = flag.name.replace(prefix, "", 1)
        result[key] = flag.is_active(request)
    return result


def get_flags(request: HttpRequest) -> Dict[str, bool]:
    prefix = settings.WAFFLE_FLAG_PREFIX
    request_with_cached_groups = _request_with_cached_user_groups(request)

    model = waffle.get_waffle_flag_model()
    flags = model.objects.filter(name__startswith=prefix).prefetch_related(
        "users",
        "groups",
    )
    return _evaluate_flags(flags, request_with_cached_groups, prefix)


def get_settings() -> Dict[str, Any]:
    constance_key_prefix: str = settings.CONSTANCE_KEY_PREFIX
    return {
        key.replace(constance_key_prefix, ""): getattr(constance_config, key, None)
        for key in dir(constance_config)
        if key.startswith(constance_key_prefix)
    }
