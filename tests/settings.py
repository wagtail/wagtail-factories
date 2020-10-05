import os

from wagtail import VERSION as WAGTAIL_VERSION

MIDDLEWARE_CLASSES = []

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

ROOT_URLCONF = "tests.urls"

SECRET_KEY = "Gx8sMKAtnA69TR9lyAlLuSnozUv3kxdscHkpwEjatZRVQQ0laMY69KL4XPxvr3KY"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": os.environ.get("TEST_DB_NAME", "wagtail_factories"),
        "USER": os.environ.get("TEST_DB_USER", None),
        "PASSWORD": os.environ.get("TEST_DB_PASSWORD", None),
        "HOST": os.environ.get("TEST_DB_HOST", "localhost"),
        "PORT": os.environ.get("TEST_DB_PORT", "5432"),
    }
}

INSTALLED_APPS = [
    "taggit",
    "rest_framework",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "tests.testapp",
]


if WAGTAIL_VERSION < (2, 0):
    INSTALLED_APPS = [
        "wagtail.contrib.wagtailstyleguide",
        "wagtail.contrib.wagtailsitemaps",
        "wagtail.contrib.wagtailroutablepage",
        "wagtail.contrib.wagtailfrontendcache",
        "wagtail.contrib.wagtailapi",
        "wagtail.contrib.wagtailsearchpromotions",
        "wagtail.contrib.settings",
        "wagtail.contrib.modeladmin",
        "wagtail.contrib.table_block",
        "wagtail.wagtailforms",
        "wagtail.wagtailsearch",
        "wagtail.wagtailembeds",
        "wagtail.wagtailimages",
        "wagtail.wagtailsites",
        "wagtail.wagtailusers",
        "wagtail.wagtailsnippets",
        "wagtail.wagtaildocs",
        "wagtail.wagtailadmin",
        "wagtail.api.v2",
        "wagtail.wagtailcore",
    ] + INSTALLED_APPS
else:
    INSTALLED_APPS = [
        "wagtail.contrib.styleguide",
        "wagtail.contrib.sitemaps",
        "wagtail.contrib.routable_page",
        "wagtail.contrib.frontend_cache",
        "wagtail.contrib.search_promotions",
        "wagtail.contrib.settings",
        "wagtail.contrib.modeladmin",
        "wagtail.contrib.table_block",
        "wagtail.contrib.forms",
        "wagtail.search",
        "wagtail.embeds",
        "wagtail.images",
        "wagtail.sites",
        "wagtail.users",
        "wagtail.snippets",
        "wagtail.documents",
        "wagtail.admin",
        "wagtail.api.v2",
        "wagtail.core",
    ] + INSTALLED_APPS


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]
