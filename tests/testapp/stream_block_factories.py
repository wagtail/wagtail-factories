import factory

import wagtail_factories

from . import models
from .factories import MyBlockFactory


class StructBlockWithLazyAttrFactory(MyBlockFactory):
    title = factory.LazyFunction(lambda: "lazy function foobar")

    class Meta:
        model = models.MyBlock


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


class SimpleStreamBlockFactoryWithSequence(wagtail_factories.StreamBlockFactory):
    number = factory.Sequence(lambda n: n)
    text = "foo"
    extra_text = "bar"

    class Meta:
        model = models.SimpleStreamBlock


class SimpleStreamBlockFactoryWithLazyFunction(wagtail_factories.StreamBlockFactory):
    number = 42
    text = "foo"
    extra_text = factory.LazyFunction(lambda: "lazy bar")

    class Meta:
        model = models.SimpleStreamBlock


class SimpleStreamBlockFactoryWithLazyAttribute(wagtail_factories.StreamBlockFactory):
    number = 42
    text = "foo"
    extra_text = factory.LazyAttribute(lambda obj: f"{obj.text}{obj.number}")

    class Meta:
        model = models.SimpleStreamBlock


class SimpleStreamBlockFactoryWithLazyCombo(wagtail_factories.StreamBlockFactory):
    number = factory.Sequence(lambda n: n)
    text = factory.LazyFunction(lambda: "foo")
    extra_text = factory.LazyAttribute(lambda obj: f"{obj.text}{obj.number}")

    class Meta:
        model = models.SimpleStreamBlock


class PageWithStreamBlockFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(MyStreamBlockFactory)

    class Meta:
        model = models.PageWithStreamBlock


class PageWithSimpleStreamBlockSequenceFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(SimpleStreamBlockFactoryWithSequence)

    class Meta:
        model = models.PageWithSimpleStreamBlock


class PageWithSimpleStreamBlockLazyFunctionFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(SimpleStreamBlockFactoryWithLazyFunction)

    class Meta:
        model = models.PageWithSimpleStreamBlock


class PageWithSimpleStreamBlockLazyAttributeFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(SimpleStreamBlockFactoryWithLazyAttribute)

    class Meta:
        model = models.PageWithSimpleStreamBlock


class PageWithSimpleStreamBlockLazyComboFactory(wagtail_factories.PageFactory):
    body = wagtail_factories.StreamFieldFactory(SimpleStreamBlockFactoryWithLazyCombo)

    class Meta:
        model = models.PageWithSimpleStreamBlock


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
