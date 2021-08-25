MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "waffle.middleware.WaffleMiddleware",
)
DEBUG_PROPAGATE_EXCEPTIONS = True
DATABASES = {
    "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"},
}
SECRET_KEY = "not very secret in tests"
ROOT_URLCONF = "tests.urls"
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "rest_framework",
    "waffle",
    "constance",
    "frontend_settings",
    "tests",
)
ALLOWED_HOSTS = ("*",)
CONSTANCE_BACKEND = "constance.backends.database.DatabaseBackend"

FRONTEND_SETTINGS = {
    "WAFFLE_FLAG_PREFIX": "TEST_",
    "CONSTANCE_KEY_PREFIX": "TEST_FRONTEND_",
}

CONSTANCE_CONFIG = {
    "TEST_FRONTEND_SETTING_AAA": ("VALUE AAA", ""),
    "TEST_FRONTEND_SETTING_BBB": ("VALUE BBB", ""),
    "TEST_FRONTEND_SETTING_CCC": ("VALUE CCC", ""),
    "NOT_FRONTEND": ("NOT ON SETTINGS", ""),
}
