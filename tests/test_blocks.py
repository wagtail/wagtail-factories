from collections import OrderedDict

import pytest
from wagtail.blocks import CharBlock, StructBlock, StructValue
from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Page

import wagtail_factories
from tests.testapp.factories import (
    MyBlockFactory,
    MyBlockItemFactory,
    MyTestPageWithStreamFieldFactory,
)


def eq_list_block_values(p, q):
    """
    Direct comparison of ListValue instances fails under current versions of Wagtail (<= 4.1),
    so do a pairwise comparison of the bound blocks' values.

    With Wagtail >= 2.16 we will get ListValues, prior to that just lists.
    """

    return all(map(lambda x, y: x.value == y.value, p.bound_blocks, q.bound_blocks))


@pytest.mark.django_db
def test_list_block_factory():
    computed = MyBlockFactory(
        items__0__label="label-1",
        items__0__value=1,
        items__1__label="label-2",
        items__1__value=2,
        image__image=None,
    )

    list_item_block = MyBlockItemFactory._meta.model()

    expected = MyBlockFactory._meta.model().clean(
        OrderedDict(
            [
                ("title", "my title"),
                ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
                (
                    "items",
                    [
                        StructValue(
                            list_item_block, [("label", "label-1"), ("value", 1)]
                        ),
                        StructValue(
                            list_item_block, [("label", "label-2"), ("value", 2)]
                        ),
                    ],
                ),
            ]
        )
    )
    assert eq_list_block_values(computed["items"], expected["items"])


@pytest.mark.django_db
def test_block_factory():
    computed = MyBlockFactory(image__image__title="blub")
    expected = MyBlockFactory._meta.model().clean(
        OrderedDict(
            [
                ("title", "my title"),
                ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
                ("items", []),
                ("image", Image.objects.first()),
            ]
        )
    )
    computed_list_value = computed.pop("items")
    expected_list_value = expected.pop("items")
    assert eq_list_block_values(computed_list_value, expected_list_value)
    assert computed == expected
    assert computed["image"].title == "blub"


def test_block_factory_build():
    computed = MyBlockFactory.build(image__image__title="blub")

    image = computed.pop("image")
    assert image.title == "blub"

    expected = MyBlockFactory._meta.model().clean(
        OrderedDict(
            [
                ("title", "my title"),
                ("item", OrderedDict([("label", "my-label"), ("value", 100)])),
                ("items", []),
            ]
        )
    )

    computed_list_value = computed.pop("items")
    expected_list_value = expected.pop("items")
    assert eq_list_block_values(computed_list_value, expected_list_value)
    assert computed == expected


@pytest.mark.django_db
def test_block_factory_subkwarg():
    computed = MyBlockFactory(item__label="my-label", item__value=20, image__image=None)
    expected = MyBlockFactory._meta.model().clean(
        OrderedDict(
            [
                ("title", "my title"),
                ("item", OrderedDict([("label", "my-label"), ("value", 20)])),
                ("items", []),
                ("image", None),
            ]
        )
    )
    computed.pop("items")
    expected.pop("items")
    assert computed == expected


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
        body__4__page__page__title="Bulb",
        body__5__document__document__title="Bubl",
    )
    assert Image.objects.count() == 1
    image = Image.objects.first()

    assert Page.objects.filter(title="Bulb").exists()
    linked_page = Page.objects.get(title="Bulb")

    assert Document.objects.count() == 1
    document = Document.objects.first()

    assert page.body[0].block_type == "char_array"
    assert page.body[2].block_type == "int_array"
    assert [x.value for x in page.body[0].value.bound_blocks] == ["foo", "bar"]
    assert [x.value for x in page.body[2].value.bound_blocks] == [100]

    assert page.body[1].block_type == "struct"
    computed_struct = page.body[1].value
    expected_struct = MyBlockFactory._meta.model().clean(
        StructValue(
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
    )
    assert eq_list_block_values(
        computed_struct.pop("items"), expected_struct.pop("items")
    )
    assert computed_struct == expected_struct

    assert page.body[3].block_type == "image"
    assert page.body[3].value == image

    assert page.body[4].block_type == "page"
    assert page.body[4].value == linked_page.specific

    assert page.body[5].block_type == "document"
    assert page.body[5].value == document

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


@pytest.mark.django_db
def test_document_chooser_block():
    value = wagtail_factories.DocumentChooserBlockFactory()
    document = Document.objects.last()

    assert value == document


@pytest.mark.django_db
def test_image_block_decorative():
    value = wagtail_factories.ImageBlockFactory(decorative=True)
    image = Image.objects.last()

    assert value.pk == image.pk
    assert value.decorative
    assert value.contextual_alt_text == ""


@pytest.mark.django_db
def test_image_block_with_alt_text():
    value = wagtail_factories.ImageBlockFactory(decorative=False)
    image = Image.objects.last()

    assert value.pk == image.pk
    assert not value.decorative
    assert isinstance(value.contextual_alt_text, str)
    assert value.contextual_alt_text.startswith("Alt text")


@pytest.mark.django_db
def test_image_block_with_no_image():
    value = wagtail_factories.ImageBlockFactory(image=None)

    assert value is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("Model", "ModelChooserBlockFactory"),
    [
        (Page, wagtail_factories.PageChooserBlockFactory),
        (Image, wagtail_factories.ImageChooserBlockFactory),
        (Document, wagtail_factories.DocumentChooserBlockFactory),
    ],
)
def test_chooser_block_strategy(Model, ModelChooserBlockFactory):
    objects_count = Model.objects.count()

    # Object isn't saved in database when the strategy is build
    ModelChooserBlockFactory.build()
    assert Model.objects.count() == objects_count

    # Object is saved in database when the strategy is create
    ModelChooserBlockFactory.create()
    assert Model.objects.count() == objects_count + 1


def test_custom_struct_value_used():
    BAR_DEFAULT = "baz"

    class CustomStructValue(StructValue):
        def foo(self):
            return self["bar"]

    class CustomStructBlock(StructBlock):
        bar = CharBlock()

        class Meta:
            value_class = CustomStructValue

    class CustomStructBlockFactory(wagtail_factories.StructBlockFactory):
        bar = BAR_DEFAULT

        class Meta:
            model = CustomStructBlock

    instance = CustomStructBlockFactory.build()
    assert instance.foo() == BAR_DEFAULT
