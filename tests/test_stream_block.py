import pytest
from django.test import TestCase
from wagtail import blocks
from wagtail.images.blocks import ImageBlock
from wagtail.images.models import Image

import wagtail_factories
from tests.testapp.stream_block_factories import (
    PageWithNestedStreamBlockFactory,
    PageWithSimpleStructBlockNestedDeepDefaultsFactory,
    PageWithSimpleStructBlockNestedDefaultsFactory,
    PageWithSimpleStructBlockNestedFactory,
    PageWithStreamBlockFactory,
    PageWithStreamBlockInListBlockFactory,
    PageWithStreamBlockInStructBlockFactory,
)
from wagtail_factories.builder import (
    DuplicateDeclaration,
    InvalidDeclaration,
    UnknownChildBlockFactory,
)


class PageTreeTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.root_page = wagtail_factories.PageFactory(parent=None)


class PageWithStreamBlockTestCase(PageTreeTestCase):
    def test_page_with_stream_block(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0__struct_block__title="foo",
        )
        assert page.body[0].block_type == "struct_block"
        assert page.body[0].value["title"] == "foo"

    def test_stream_block_with_struct_block_lazy_attrs(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0="struct_block",
        )
        assert page.body[0].block_type == "struct_block"
        assert page.body[0].value["title"] == "lazy function foobar"

    def test_page_with_stream_block_default_value(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0="struct_block",
        )
        assert page.body[0].value["title"] == "lazy function foobar"

    def test_page_with_nested_stream_block(self):
        page = PageWithNestedStreamBlockFactory(
            parent=self.root_page,
            body__0__inner_stream__0__struct_block__title="foo",
        )
        assert page.body[0].value[0].value["title"] == "foo"

    def test_page_with_nested_stream_block_default_value(self):
        page = PageWithNestedStreamBlockFactory(
            parent=self.root_page,
            body__0__inner_stream__0="struct_block",
        )
        assert page.body[0].value[0].value["title"] == "lazy function foobar"

    def test_page_with_deeply_nested_stream_block(self):
        page = PageWithStreamBlockInStructBlockFactory(
            parent=self.root_page,
            body__0__struct_block__inner_stream__0__struct_block__title="foo",
        )
        assert page.body[0].value["inner_stream"][0].value["title"] == "foo"

    def test_page_with_deeply_nested_stream_block_defaults(self):
        page = PageWithStreamBlockInStructBlockFactory(
            parent=self.root_page,
            body__0__struct_block__inner_stream__0="char_block",
            body__1__struct_block__inner_stream__0="struct_block",
        )

        assert page.body[0].value["inner_stream"][0].block_type == "char_block"
        # Default value for the CharBlock is None
        assert page.body[0].value["inner_stream"][0].value is None

        assert page.body[1].value["inner_stream"][0].block_type == "struct_block"
        assert (
            page.body[1].value["inner_stream"][0].value["title"]
            == "lazy function foobar"
        )

    def test_page_with_deeply_nested_stream_block_in_list_block(self):
        page = PageWithStreamBlockInListBlockFactory(
            parent=self.root_page,
            body__0__list_block__0__0__struct_block__title="foo",
        )
        assert page.body[0].value[0][0].value["title"] == "foo"

    def test_computed_values_on_struct_block_in_nested_stream(self):
        page = PageWithSimpleStructBlockNestedFactory(
            body__0__inner_stream__0="simple_struct_block"
        )
        assert page.body[0].value[0].value["boolean"] is True
        assert page.body[0].value[0].value["text"][:4] == "True"
        assert page.body[0].value[0].value["text"][4:] == str(
            page.body[0].value[0].value["number"]
        )

    def test_factory_with_anonymous_stream_block_in_tree(self):
        # The inner_stream child block is defined as an "anonymous" StreamBlock (i.e. declared
        # inline like `inner_stream = StreamBlock(...)', not an explicit StreamBlock subclass) so
        # there is no declared class with which to create the nested StreamValue. This test
        # ensures we are passing a block definition down the recursive StepBuilder calls.
        text, number, boolean = "Hello world", 11, True
        page = PageWithSimpleStructBlockNestedFactory(
            body__0__inner_stream__0__simple_struct_block__text=text,
            body__0__inner_stream__0__simple_struct_block__number=number,
            body__0__inner_stream__0__simple_struct_block__boolean=boolean,
        )
        assert page.body[0].value[0].block_type == "simple_struct_block"
        assert page.body[0].value[0].value["text"] == text
        assert page.body[0].value[0].value["number"] == number
        assert page.body[0].value[0].value["boolean"] == boolean

    def test_sub_factory_defaults(self):
        page = PageWithSimpleStructBlockNestedDefaultsFactory(
            body__0__inner_stream__0="simple_struct_block",
        )
        assert page.body[0].value[0].value["text"] == "default text"
        assert page.body[0].value[0].value["number"] == 11
        assert page.body[0].value[0].value["boolean"] is False

    def test_sub_factory_deep_defaults(self):
        page = PageWithSimpleStructBlockNestedDeepDefaultsFactory(
            body__0="inner_stream",
        )
        assert page.body[0].value[0].value["text"] == "deep text"
        assert page.body[0].value[0].value["number"] == 111
        assert page.body[0].value[1].value["text"] == "deep text 2"

    def test_page_with_image_chooser_stream_block(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0="image_chooser_block",
        )
        assert page.body[0].value == Image.objects.last()

    def test_page_with_image_stream_block(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0__image_block__decorative=False,
        )
        assert isinstance(page.body[0].block, ImageBlock)
        assert page.body[0].value.pk == Image.objects.last().pk
        assert not page.body[0].value.decorative

    def test_page_with_image_stream_block_no_image(self):
        page = PageWithStreamBlockFactory(
            parent=self.root_page,
            body__0__image_block__image=None,
        )
        assert isinstance(page.body[0].block, ImageBlock)
        assert page.body[0].value is None


class EmptyStreamValueTestCase(PageTreeTestCase):
    # We should be able to generate a value for a StreamBlockFactory that received no parameters
    # (i.e. the empty StreamValue)

    def test_page_without_stream_field_params(self):
        page = PageWithStreamBlockFactory(parent=self.root_page)
        assert len(page.body) == 0
        assert isinstance(page.body, blocks.StreamValue)

    def test_nested_stream_block_default_value(self):
        page = PageWithNestedStreamBlockFactory(
            parent=self.root_page, body__0="inner_stream"
        )
        assert len(page.body[0].value) == 0
        assert isinstance(page.body[0].value, blocks.StreamValue)


class StreamFieldFactoryErrorsTestCase(PageTreeTestCase):
    def test_raises_missing_index(self):
        test_values = (
            ({"body__1": "struct_block"}, 0),
            ({"body__0": "struct_block", "body__2": "struct_block"}, 1),
        )
        for params, missing_index in test_values:
            with self.subTest(params=params):
                with pytest.raises(
                    InvalidDeclaration, match=f"missing required index {missing_index}"
                ):
                    PageWithStreamBlockFactory(**params)

    def test_raises_duplicate_declaration(self):
        test_values = (
            (
                {"body__0__struct_block__title": "title", "body__0": "char_block"},
                "got char_block, already have struct_block",
            ),
            (
                {
                    "body__0__struct_block__title": "foobar",
                    "body__0__char_block": "baz",
                },
                "got char_block, already have struct_block",
            ),
        )
        for params, msg in test_values:
            with self.subTest(params=params):
                with pytest.raises(DuplicateDeclaration, match=msg):
                    PageWithStreamBlockFactory(**params)

    def test_raises_unknown_child_block(self):
        with pytest.raises(
            UnknownChildBlockFactory, match="No factory defined for block 'foobar'"
        ):
            PageWithStreamBlockFactory(body__0="foobar")
