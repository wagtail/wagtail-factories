try:
    from wagtail import blocks
except ImportError:
    # Wagtail<3.0
    from wagtail.core import blocks

try:
    from wagtail.fields import StreamField
except ImportError:
    # Wagtail<3.0
    from wagtail.core.fields import StreamField

try:
    from wagtail.models import Page
except ImportError:
    # Wagtail<3.0
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
    body = StreamField(
        [
            ("char_array", blocks.ListBlock(blocks.CharBlock())),
            ("int_array", blocks.ListBlock(blocks.IntegerBlock())),
            ("struct", MyBlock()),
            ("image", ImageChooserBlock()),
        ]
    )
