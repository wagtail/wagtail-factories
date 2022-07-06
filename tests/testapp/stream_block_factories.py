import factory

import wagtail_factories

from . import models
from .factories import MyBlockFactory


class StructBlockWithLazyAttrFactory(MyBlockFactory):
    title = factory.LazyFunction(lambda: "lazy function foobar")

    class Meta:
        model = models.MyBlock


class SimpleStructBlockFactory(wagtail_factories.StructBlockFactory):
    text = factory.LazyAttribute(lambda obj: f"{obj.boolean}{obj.number}")
    number = factory.Sequence(lambda n: n)
    boolean = factory.LazyFunction(lambda: True)

    class Meta:
        model = models.SimpleStructBlock


class SimpleStructBlockInnerStreamFactory(wagtail_factories.StreamBlockFactory):
    simple_struct_block = factory.SubFactory(SimpleStructBlockFactory)


class SimpleStructBlockOuterStreamFactory(wagtail_factories.StreamBlockFactory):
    inner_stream = factory.SubFactory(SimpleStructBlockInnerStreamFactory)

    class Meta:
        model = models.SimpleStructBlockNestedStream


class PageWithSimpleStructBlockNestedFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(SimpleStructBlockOuterStreamFactory)

    class Meta:
        model = models.PageWithSimpleStructBlockNested


class MyStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    struct_block = factory.SubFactory(StructBlockWithLazyAttrFactory)
    char_block = factory.SubFactory(wagtail_factories.CharBlockFactory)

    class Meta:
        model = models.MyStreamBlock


class NestedStreamBlockFactory(wagtail_factories.StreamBlockFactory):
    inner_stream = factory.SubFactory(MyStreamBlockFactory)

    class Meta:
        model = models.NestedStreamBlock


class StructBlockWithStreamBlockFactory(wagtail_factories.StructBlockFactory):
    inner_stream = factory.SubFactory(MyStreamBlockFactory)

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
