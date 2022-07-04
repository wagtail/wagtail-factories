import pytest

import wagtail_factories
from tests.testapp.stream_block_factories import (
    PageWithStreamBlockFactory,
    PageWithNestedStreamBlockFactory,
    PageWithStreamBlockInStructBlockFactory,
    PageWithStreamBlockInListBlockFactory,
    PageWithSimpleStreamBlockSequenceFactory,
    PageWithSimpleStreamBlockLazyFunctionFactory,
    PageWithSimpleStreamBlockLazyAttributeFactory,
    PageWithSimpleStreamBlockLazyComboFactory,
)


@pytest.mark.django_db
def test_page_with_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithStreamBlockFactory(
        parent=root_page,
        body__0__struct_block__title="foo",
    )
    assert page.body[0].block_type == "struct_block"
    assert page.body[0].value["title"] == "foo"


@pytest.mark.django_db
def test_stream_block_with_struct_block_lazy_attrs():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithStreamBlockFactory(
        parent=root_page,
        body__0="struct_block",
    )
    assert page.body[0].block_type == "struct_block"
    assert page.body[0].value["title"] == "foobar"


@pytest.mark.django_db
def test_page_with_stream_block_default_value():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithStreamBlockFactory(
        parent=root_page,
        body__0="struct_block",
    )
    assert page.body[0].value["title"] == "my title"


@pytest.mark.django_db
def test_page_with_nested_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithNestedStreamBlockFactory(
        parent=root_page,
        body__0__inner_stream__0__struct_block__title="foo",
    )
    assert page.body[0].value[0].value["title"] == "foo"


@pytest.mark.django_db
def test_page_with_nested_stream_block_default_value():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithNestedStreamBlockFactory(
        parent=root_page,
        body__0__inner_stream__0="struct_block",
    )
    assert page.body[0].value[0].value["title"] == "my title"


@pytest.mark.django_db
def test_page_with_deeply_nested_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithStreamBlockInStructBlockFactory(
        parent=root_page,
        body__0__struct_block__inner_stream__0__struct_block__title="foo",
    )
    assert page.body[0].value["inner_stream"][0].value["title"] == "foo"


@pytest.mark.django_db
def test_page_with_deeply_nested_stream_block_in_list_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithStreamBlockInListBlockFactory(
        parent=root_page,
        body__0__list_block__0__0__struct_block__title="foo",
    )
    assert page.body[0].value[0][0].value["title"] == "foo"


@pytest.mark.django_db
def test_page_with_sequence_in_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithSimpleStreamBlockSequenceFactory(
        parent=root_page,
        body__0="number",
        body__1="text",
        body__2="extra_text",
        body__3__number=42,
    )

    assert page.body[0].value == 0
    assert page.body[1].value == "foo"
    assert page.body[2].value == "bar"
    assert page.body[3].value == 42


@pytest.mark.django_db
def test_page_with_lazy_function_in_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithSimpleStreamBlockLazyFunctionFactory(
        parent=root_page,
        body__0="number",
        body__1="text",
        body__2="extra_text",
    )
    assert page.body[0].value == 42
    assert page.body[1].value == "foo"
    assert page.body[2].value == "lazy bar"


@pytest.mark.django_db
def test_page_with_lazy_attr_in_stream_block():
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithSimpleStreamBlockLazyAttributeFactory(
        parent=root_page,
        body__0="number",
        body__1="text",
        body__2="extra_text",
    )
    assert page.body[0].value == 42
    assert page.body[1].value == "foo"
    assert page.body[2].value == "foo42"


@pytest.mark.django_db
def test_page_with_lazy_combo_in_stream_block():
    # Combination of Sequence, LazyFunction and LazyAttribute
    root_page = wagtail_factories.PageFactory(parent=None)
    page = PageWithSimpleStreamBlockLazyComboFactory(
        parent=root_page,
        body__0="number",
        body__1="text",
        body__2="extra_text",
    )
    assert page.body[0].value == 0
    assert page.body[1].value == "foo"
    assert page.body[2].value == "foo0"
