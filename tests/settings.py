DEBUG = True
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "tests",
]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
