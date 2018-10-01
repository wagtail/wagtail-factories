try:
    from wagtail.wagtailcore import blocks
    from wagtail.wagtailcore.fields import StreamField
    from wagtail.wagtailcore.models import Page
    from wagtail.wagtailimages.blocks import ImageChooserBlock
except ImportError:
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
