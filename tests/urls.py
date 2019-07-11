from django.conf.urls import include, url
from wagtail.core import urls as wagtail_urls

urlpatterns = []

urlpatterns += [url(r"^", include(wagtail_urls))]
