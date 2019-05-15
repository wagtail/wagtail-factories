from django.conf.urls import url, include

try:
    from wagtail.wagtailcore import urls as wagtail_urls
except ImportError:
    from wagtail.core import urls as wagtail_urls

urlpatterns = []

urlpatterns += [url(r"^", include(wagtail_urls))]
