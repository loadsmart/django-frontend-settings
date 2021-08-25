from django.conf import settings as dj_settings
from django.test.signals import setting_changed
from rest_framework.settings import APISettings as _APISettings

DEFAULTS = {
    "WAFFLE_FLAG_PREFIX": "FRONTEND_",
    "CONSTANCE_KEY_PREFIX": "FRONTEND_",
}

USER_SETTINGS = getattr(dj_settings, "FRONTEND_SETTINGS", None)
IMPORT_STRINGS = []
REMOVED_SETTINGS = []


class APISettings(_APISettings):
    WAFFLE_FLAG_PREFIX: str
    CONSTANCE_KEY_PREFIX: str

    @property
    def user_settings(self):
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "FRONTEND_SETTINGS", {})
        return self._user_settings


settings = APISettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)


def reload_api_settings(*_, **kwargs):
    global settings

    setting = kwargs["setting"]

    if setting == "FRONTEND_SETTINGS":
        settings.reload()


setting_changed.connect(reload_api_settings)
