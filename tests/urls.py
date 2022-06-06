from django.urls import include, path

try:
    from wagtail import urls as wagtail_urls
except ImportError:
    # Wagtail<3.0
    from wagtail.core import urls as wagtail_urls


urlpatterns = [
    path("", include(wagtail_urls)),
]
