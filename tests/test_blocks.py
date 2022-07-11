from collections import OrderedDict

import pytest
from wagtail.images.models import Image

import wagtail_factories
from tests.testapp.factories import MyBlockFactory, MyTestPageWithStreamFieldFactory

try:
    from wagtail.blocks import StructValue
    from wagtail.models import Page
except ImportError:
    # Wagtail<3.0
    from wagtail.core.blocks import StructValue
    from wagtail.core.models import Page


@pytest.mark.django_db
def test_list_block_factory():
    value = MyBlockFactory(
        items__0__label="label-1",
        items__0__value=1,
        items__1__label="label-2",
        items__1__value=2,
        image__image=None,
    )

    assert value == StructValue(
        None,
        [
            ("title", "my title"),
            ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
            (
                "items",
                [
                    StructValue(None, [("label", "label-1"), ("value", 1)]),
                    StructValue(None, [("label", "label-2"), ("value", 2)]),
                ],
            ),
            ("image", None),
        ],
    )


@pytest.mark.django_db
def test_block_factory():
    value = MyBlockFactory(image__image__title="blub")

    assert value == OrderedDict(
        [
            ("title", "my title"),
            ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
            ("items", []),
            ("image", Image.objects.first()),
        ]
    )

    assert value["image"].title == "blub"


def test_block_factory_build():
    value = MyBlockFactory.build(image__image__title="blub")

    image = value.pop("image")
    assert image.title == "blub"

    assert value == OrderedDict(
        [
            ("title", "my title"),
            ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
            ("items", []),
        ]
    )


@pytest.mark.django_db
def test_block_factory_subkwarg():
    value = MyBlockFactory(item__label="my-label", item__value=20, image__image=None)

    assert value == OrderedDict(
        [
            ("title", "my title"),
            ("item", OrderedDict([("label", "my-label"), ("value", 20)])),
            ("items", []),
            ("image", None),
        ]
    )


@pytest.mark.django_db
def test_custom_page_streamfield_data_complex():
    assert Image.objects.count() == 0

    root_page = wagtail_factories.PageFactory(parent=None)
    page = MyTestPageWithStreamFieldFactory(
        parent=root_page,
        body__0__char_array__0="foo",
        body__0__char_array__1="bar",
        body__2__int_array__0=100,
        body__1__struct__title="My Title",
        body__1__struct__item__value=100,
        body__1__struct__image__image=None,
        body__3__image__image__title="Blub",
    )
    assert Image.objects.count() == 1
    image = Image.objects.first()

    assert page.body[0].block_type == "char_array"
    assert page.body[0].value == ["foo", "bar"]

    assert page.body[1].block_type == "struct"
    assert page.body[1].value == StructValue(
        None,
        [
            ("title", "My Title"),
            (
                "item",
                StructValue(None, [("label", "my-label"), ("value", 100)]),
            ),
            ("items", []),
            ("image", None),
        ],
    )

    assert page.body[2].block_type == "int_array"
    assert page.body[2].value == [100]

    assert page.body[3].block_type == "image"
    assert page.body[3].value == image

    content = str(page.body)
    assert "block-image" in content


@pytest.mark.django_db
def test_custom_page_streamfield_default_blocks():
    assert Image.objects.count() == 0

    with pytest.raises(wagtail_factories.builder.UnknownChildBlockFactory) as excinfo:
        MyTestPageWithStreamFieldFactory(body__0="unknown")

    assert "No factory defined for block 'unknown'" in str(excinfo.value)

    page = MyTestPageWithStreamFieldFactory(body__0="image", body__1="image")
    assert Image.objects.count() == 2

    image1, image2 = Image.objects.all()

    assert page.body[0].block_type == "image"
    assert page.body[0].value == image1
    assert page.body[1].block_type == "image"
    assert page.body[1].value == image2

    content = str(page.body)
    assert content.count("block-image") == 2


@pytest.mark.django_db
def test_page_chooser_block():
    value = wagtail_factories.PageChooserBlockFactory()
    page = Page.objects.last()

    assert value == page


@pytest.mark.django_db
def test_image_chooser_block():
    value = wagtail_factories.ImageChooserBlockFactory()
    image = Image.objects.last()

    assert value == image
