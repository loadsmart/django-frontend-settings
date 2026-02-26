from typing import Any, Dict

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


def get_flags(request: HttpRequest) -> Dict[str, bool]:
    prefix = settings.WAFFLE_FLAG_PREFIX
    request_with_cached_groups = request
    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        group_ids = tuple(user.groups.all().values_list("pk", flat=True))
        request_with_cached_groups = _CachedRequest(request, _CachedUser(user, group_ids))

    model = waffle.get_waffle_flag_model()
    flags = model.objects.filter(name__startswith=prefix).values_list("name", flat=True)
    return {name.replace(prefix, "", 1): waffle.flag_is_active(request_with_cached_groups, name) for name in flags}


def get_settings() -> Dict[str, Any]:
    constance_key_prefix: str = settings.CONSTANCE_KEY_PREFIX
    return {
        key.replace(constance_key_prefix, ""): getattr(constance_config, key, None)
        for key in dir(constance_config)
        if key.startswith(constance_key_prefix)
    }
