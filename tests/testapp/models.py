from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock


class MyBlockItem(blocks.StructBlock):
    label = blocks.CharBlock()
    value = blocks.IntegerBlock()


class MyBlock(blocks.StructBlock):
    title = blocks.CharBlock(max_length=100)
    item = MyBlockItem()
    items = blocks.ListBlock(MyBlockItem)
    image = ImageChooserBlock()


class MyTestPage(Page):
    body = StreamField([
        ('char_array', blocks.ListBlock(blocks.CharBlock())),
        ('int_array', blocks.ListBlock(blocks.IntegerBlock())),
        ('struct', MyBlock()),
        ('image', ImageChooserBlock()),
    ])
