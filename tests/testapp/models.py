from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.fields import StreamField
from wagtail.images.blocks import ImageBlock, ImageChooserBlock
from wagtail.models import Page


class MyBlockItem(blocks.StructBlock):
    label = blocks.CharBlock()
    value = blocks.IntegerBlock()


class MyBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    item = MyBlockItem()
    items = blocks.ListBlock(MyBlockItem)
    image = ImageChooserBlock(required=False)


class SimpleStructBlock(blocks.StructBlock):
    # Atomic child blocks only
    text = blocks.CharBlock()
    number = blocks.IntegerBlock()
    boolean = blocks.BooleanBlock()


class SimpleStructBlockNestedStream(blocks.StreamBlock):
    inner_stream = blocks.StreamBlock([("simple_struct_block", SimpleStructBlock())])


class PageWithSimpleStructBlockNested(Page):
    body = StreamField(SimpleStructBlockNestedStream(), use_json_field=True)


class MyTestPage(Page):
    body = StreamField(
        [
            ("char_array", blocks.ListBlock(blocks.CharBlock())),
            ("int_array", blocks.ListBlock(blocks.IntegerBlock())),
            ("struct", MyBlock()),
            ("page", blocks.PageChooserBlock()),
            ("image", ImageChooserBlock()),
            ("document", DocumentChooserBlock()),
        ],
        use_json_field=True,
    )


class MyStreamBlock(blocks.StreamBlock):
    struct_block = MyBlock()
    char_block = blocks.CharBlock()
    image_chooser_block = ImageChooserBlock()
    image_block = ImageBlock()


class NestedStreamBlock(blocks.StreamBlock):
    inner_stream = MyStreamBlock()


class StructBlockWithStreamBlock(blocks.StructBlock):
    inner_stream = MyStreamBlock()


class DeeplyNestedStreamBlock(blocks.StreamBlock):
    struct_block = StructBlockWithStreamBlock()


class DeeplyNestedStreamBlockInListBlock(blocks.StreamBlock):
    list_block = blocks.ListBlock(MyStreamBlock())


class PageWithStreamBlock(Page):
    body = StreamField(MyStreamBlock(), use_json_field=True)


class PageWithNestedStreamBlock(Page):
    body = StreamField(NestedStreamBlock(), use_json_field=True)


class PageWithStreamBlockInStructBlock(Page):
    body = StreamField(DeeplyNestedStreamBlock(), use_json_field=True)


class PageWithStreamBlockInListBlock(Page):
    body = StreamField(DeeplyNestedStreamBlockInListBlock(), use_json_field=True)
