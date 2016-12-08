from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.fields import StreamField
from wagtail.wagtailcore.models import Page


class MyTestPage(Page):
    body = StreamField([
        ('char_array', blocks.ListBlock(blocks.CharBlock())),
    ])
