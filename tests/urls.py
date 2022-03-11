from django.urls import include, path

from wagtail.core import urls as wagtail_urls

urlpatterns = [
    path("", include(wagtail_urls)),
]
