import os

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from wagtail.models import Page
from wagtail.admin.views.pages import EditView

import wagtail_factories


class PageFeaturesTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_superuser("superuser")
        cls.default_request = cls.get_request("/")

    @classmethod
    def get_request(cls, path: str, method: str = "GET") -> HttpRequest:
        request = HttpRequest()
        request.method = method
        request.path = path
        request.user = get_user_model().objects.create_superuser("superuser")

    def assertCanRenderPageWithoutErrors(self, page: Page, route_path: str = "/"):
        full_path = os.path.join(page.get_url(self.default_request), route_path)
        request = self.get_request(full_path)
        try:
            view, args, kwargs = page.resolve_subpage(route_path)
        except AttributeError:
            page.serve(request)
        else:
            page.serve(request, view, args, kwargs)

    def assertCanEditPageWithoutErrors(self, page: Page):
        path = f"/admin/pages/{page.id}/edit/"
        request = self.get_request(path)
        EditView.as_view()(request, page.id)
        post_request = self.get_request(path, method="POST")
        EditView.as_view()(post_request, page.id)

    def assertCanPreviewPageWithoutErrors(self, page: Page, preview_mode: str = ""):
        path = f"/admin/pages/{page.id}/edit/preview/?mode={preview_mode}"
        request = self.get_request(path)
        preview_request = page.make_preview_request(request, preview_mode)
        page.serve_preview(preview_request, preview_mode)


class PageAutoTestCase(PageFeaturesTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.factories_to_test = [
            f for f in wagtail_factories.get_page_factories() if f._meta.autotest
        ]

    def test_can_render_pages_without_errors(self):
        for factory in self.factories_to_test:
            page = factory()
            for path in page.get_route_paths(page):
                with self.subTest(f"Page type: {type(page)}, Route: {path}"):
                    self.assertCanRenderPageWithoutErrors(page, path)

    def test_can_edit_pages_without_errors(self):
        for factory in self.factories_to_test:
            page = factory()
            with self.subTest(f"Page type: {type(page)}"):
                self.assertCanEditPageWithoutErrors(page)

    def test_can_preview_pages_without_errors(self):
        for factory in self.factories_to_test:
            page = factory()
            for mode, label in page.preview_modes:
                with self.subTest(f"Page type: {type(page)}, Mode: {label}"):
                    self.assertCanPreviewPageWithoutErrors(page, mode)
