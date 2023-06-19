from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock


class MyBlockItem(blocks.StructBlock):
    label = blocks.CharBlock()
    value = blocks.IntegerBlock()


class MyBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    item = MyBlockItem()
    items = blocks.ListBlock(MyBlockItem)
    image = ImageChooserBlock()


class MyStreamBlock(blocks.StreamBlock):
    title = blocks.CharBlock(max_length=100)
    subtitle = blocks.CharBlock()
    item = MyBlockItem()


class MyCharBlock(blocks.CharBlock):
    pass


class MyTestPage(Page):
    body = StreamField([
        ('char_array', blocks.ListBlock(blocks.CharBlock())),
        ('int_array', blocks.ListBlock(blocks.IntegerBlock())),
        ('struct', MyBlock()),
        ('image', ImageChooserBlock()),
        ('stream', MyStreamBlock()),
        ('char', MyCharBlock()),
    ])
