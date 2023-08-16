import factory
import pytest
import wagtail_factories

from tests.testapp.models import MyStreamBlock, PageWithStreamBlock
from tests.testapp.stream_block_factories import (
    MyStreamBlockFactory,
    StructBlockWithLazyAttrFactory,
)

pytestmark = pytest.mark.django_db

LAZY_TEXT = "lazily evaluated text"


@pytest.fixture()
def page_factory_with_stream_field_defaults():
    class Factory(wagtail_factories.PageFactory):
        body = wagtail_factories.StreamFieldFactory(
            MyStreamBlockFactory,
            default_block_values={
                "0__char_block": "Foo bar baz",
                "1": "struct_block",
                "2__struct_block__title": "overridden title",
                "3__char_block": factory.LazyFunction(lambda: LAZY_TEXT),
            },
        )

        class Meta:
            model = PageWithStreamBlock

    return Factory


def test_create_from_stream_field_defaults(page_factory_with_stream_field_defaults):
    instance = page_factory_with_stream_field_defaults.build()
    assert instance.body[0].value == "Foo bar baz"
    assert instance.body[1].value["title"] == "lazy function foobar"
    assert instance.body[2].value["title"] == "overridden title"
    assert instance.body[3].value == LAZY_TEXT


def test_override_stream_field_defaults(page_factory_with_stream_field_defaults):
    instance = page_factory_with_stream_field_defaults.build(
        body__0__char_block="overridden",
        body__1__struct_block__title="overridden",
        body__2__struct_block__title=factory.LazyFunction(lambda: LAZY_TEXT),
    )
    assert instance.body[0].value == "overridden"
    assert instance.body[1].value["title"] == "overridden"


@pytest.fixture()
def stream_block_factory_with_meta_defaults():
    class BlockFactory(MyStreamBlockFactory):
        struct_block = factory.SubFactory(StructBlockWithLazyAttrFactory)
        char_block = factory.SubFactory(wagtail_factories.CharBlockFactory)

        class Meta:
            model = MyStreamBlock
            default_block_values = {
                "0__char_block": "meta default text",
                "1__struct_block__title": "struct block title",
                "2__char_block": "meta default text",
                "3__char_block": factory.LazyFunction(lambda: LAZY_TEXT),
            }

    return BlockFactory


@pytest.fixture()
def page_factory_with_stream_block_meta_defaults(
    stream_block_factory_with_meta_defaults,
):
    def get_page_factory(default_block_values=None):
        class PageFactory(wagtail_factories.PageFactory):
            body = wagtail_factories.StreamFieldFactory(
                stream_block_factory_with_meta_defaults,
                default_block_values=default_block_values or {},
            )

            class Meta:
                model = PageWithStreamBlock

        return PageFactory

    return get_page_factory


def test_meta_defaults_used(page_factory_with_stream_block_meta_defaults):
    instance = page_factory_with_stream_block_meta_defaults(
        {"0__char_block": "overridden text"}
    ).build()
    assert instance.body[1].value["title"] == "struct block title"
    assert instance.body[3].value == LAZY_TEXT


def test_meta_defaults_overridden(page_factory_with_stream_block_meta_defaults):
    """
    Defaults on a StreamBlockFactory Meta class should be overridden by defaults
    provided to StreamBlockFactory.__init__
    """
    instance = page_factory_with_stream_block_meta_defaults(
        {
            "0__char_block": "overridden text",
            "2__char_block": factory.LazyFunction(lambda: LAZY_TEXT),
        }
    ).build()
    assert instance.body[0].value == "overridden text"
    assert instance.body[2].value == LAZY_TEXT


def test_init_args_have_precedence(page_factory_with_stream_block_meta_defaults):
    init_arg_text = "init arg text"
    instance = page_factory_with_stream_block_meta_defaults(
        {"0__char_block": "overridden text"}
    ).build(
        body__0__char_block=init_arg_text,
        body__1__struct_block__title=init_arg_text
    )
    assert instance.body[0].value == init_arg_text
    assert instance.body[1].value["title"] == init_arg_text
