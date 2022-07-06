import pytest
from django.test import TestCase

import wagtail_factories
from tests.testapp.stream_block_factories import (
    PageWithStreamBlockFactory,
    PageWithNestedStreamBlockFactory,
    PageWithStreamBlockInStructBlockFactory,
    PageWithStreamBlockInListBlockFactory,
    PageWithSimpleStructBlockNestedFactory,
)


class PageWithStreamBlockTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = wagtail_factories.PageFactory(parent=None)

    def test_page_with_stream_block(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0__struct_block__title="foo",
        )
        self.assertEqual(page.body[0].block_type, "struct_block")
        self.assertEqual(page.body[0].value["title"], "foo")

    def test_stream_block_with_struct_block_lazy_attrs(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0="struct_block",
        )
        self.assertEqual(page.body[0].block_type, "struct_block")
        self.assertEqual(page.body[0].value["title"], "lazy function foobar")

    def test_page_with_stream_block_default_value(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0="struct_block",
        )
        self.assertEqual(page.body[0].value["title"], "lazy function foobar")

    def test_page_with_nested_stream_block(self):
        page = PageWithNestedStreamBlockFactory(
            parent=self.root_page,
            body__0__inner_stream__0__struct_block__title="foo",
        )
        self.assertEqual(page.body[0].value[0].value["title"], "foo")

    def test_page_with_nested_stream_block_default_value(self):
        page = PageWithNestedStreamBlockFactory(
            parent=self.root_page,
            body__0__inner_stream__0="struct_block",
        )
        self.assertEqual(page.body[0].value[0].value["title"], "lazy function foobar")

    def test_page_with_deeply_nested_stream_block(self):
        page = PageWithStreamBlockInStructBlockFactory(
            parent=self.root_page,
            body__0__struct_block__inner_stream__0__struct_block__title="foo",
        )
        self.assertEqual(page.body[0].value["inner_stream"][0].value["title"], "foo")

    def test_page_with_deeply_nested_stream_block_in_list_block(self):
        page = PageWithStreamBlockInListBlockFactory(
            parent=self.root_page,
            body__0__list_block__0__0__struct_block__title="foo",
        )
        self.assertEqual(page.body[0].value[0][0].value["title"], "foo")

    @pytest.mark.xfail
    def test_computed_values_on_struct_block_in_nested_stream(self):
        page = PageWithSimpleStructBlockNestedFactory(
            body__0__inner_stream__0="simple_struct_block"
        )
        self.assertEqual(page.body[0].value[0].value["boolean"], True)
        self.assertEqual(page.body[0].value[0].value["text"][:4], "True")
        self.assertEqual(
            page.body[0].value[0].value["text"][4:],
            str(page.body[0].value[0].value["number"]),
        )
