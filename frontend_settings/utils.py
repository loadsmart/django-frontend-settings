from typing import Any, Dict

import waffle
from constance import config as constance_config
from django.http import HttpRequest

from frontend_settings.settings import settings


def get_flags(request: HttpRequest) -> Dict[str, bool]:
    prefix = settings.WAFFLE_FLAG_PREFIX
    model = waffle.get_waffle_flag_model()
    flags = model.objects.filter(name__startswith=prefix).values_list("name")
    return {
        name[0].replace(prefix, "", 1): waffle.flag_is_active(request, name[0])
        for name in flags
    }


def get_settings() -> Dict[str, Any]:
    constance_key_prefix: str = settings.CONSTANCE_KEY_PREFIX
    return {
        key.replace(constance_key_prefix, ""): getattr(constance_config, key, None)
        for key in dir(constance_config)
        if key.startswith(constance_key_prefix)
    }
