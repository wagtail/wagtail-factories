import factory

import wagtail_factories

from . import models


class MyBlockItemFactory(wagtail_factories.StructBlockFactory):
    label = "my-label"
    value = 100

    class Meta:
        model = models.MyBlockItem


class MyBlockFactory(wagtail_factories.StructBlockFactory):
    title = "my title"
    item = factory.SubFactory(MyBlockItemFactory)
    items = wagtail_factories.ListBlockFactory(MyBlockItemFactory)
    image = factory.SubFactory(wagtail_factories.ImageChooserBlockFactory)

    class Meta:
        model = models.MyBlock


class MyTestPageFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.MyTestPage


class MyTestPageGetOrCreateFactory(wagtail_factories.PageFactory):
    class Meta:
        model = models.MyTestPage
        django_get_or_create = ["slug", "parent"]


class MyTestPageWithStreamFieldFactory(wagtail_factories.PageFactory):

    body = wagtail_factories.StreamFieldFactory(
        {
            "char_array": wagtail_factories.ListBlockFactory(
                wagtail_factories.CharBlockFactory
            ),
            "int_array": wagtail_factories.ListBlockFactory(
                wagtail_factories.IntegerBlockFactory
            ),
            "struct": MyBlockFactory,
            "image": wagtail_factories.ImageChooserBlockFactory,
        }
    )

    class Meta:
        model = models.MyTestPage


class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    struct_block = factory.SubFactory(MyBlockFactory)
    char_block = factory.SubFactory(wagtail_factories.CharBlockFactory)

    class Meta:
        model = models.MyStreamBlock


class NestedStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    inner_stream = factory.SubFactory(MyStreamBlockFactory)

    class Meta:
        model = models.NestedStreamBlock


class StructBlockWithStreamBlockFactory(wagtail_factories.StructBlockFactory):
    inner_stream = factory.SubFactory(MyStreamBlockFactory)
    foo = "bar"

    class Meta:
        model = models.StructBlockWithStreamBlock


class DeeplyNestedStreamBlockInListBlockFactory(wagtail_factories.StreamBlockFactory):
    list_block = wagtail_factories.ListBlockFactory(MyStreamBlockFactory)

    class Meta:
        model = models.DeeplyNestedStreamBlockInListBlock


class DeeplyNestedStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    struct_block = factory.SubFactory(StructBlockWithStreamBlockFactory)

    class Meta:
        model = models.DeeplyNestedStreamBlock


class PageWithStreamBlockFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(MyStreamBlockFactory)

    class Meta:
        model = models.PageWithStreamBlock


class PageWithNestedStreamBlockFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(NestedStreamBlockFactory)

    class Meta:
        model = models.PageWithNestedStreamBlock


class PageWithStreamBlockInStructBlockFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(DeeplyNestedStreamBlockFactory)

    class Meta:
        model = models.PageWithStreamBlockInStructBlock


class PageWithStreamBlockInListBlockFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(
        DeeplyNestedStreamBlockInListBlockFactory
    )

    class Meta:
        model = models.PageWithStreamBlockInListBlock
