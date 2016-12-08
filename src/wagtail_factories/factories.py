import factory

from wagtail.wagtailcore.models import Collection, Page
from wagtail.wagtailimages.models import get_image_model

__all__ = [
    'CollectionFactory',
    'ImageFactory',
    'PageFactory',
]


class MP_NodeFactory(factory.DjangoModelFactory):
    path = '0001'
    depth = 1
    numchild = 0


class CollectionFactory(MP_NodeFactory):
    path = '00010001'
    depth = 2
    numchild = 0
    name = 'Test collection'

    class Meta:
        model = Collection


class PageFactory(MP_NodeFactory):
    title = 'Test page'
    slug = 'test-page'

    class Meta:
        model = Page


class ImageFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_image_model()

    collection = factory.SubFactory(CollectionFactory)
    file = factory.django.ImageField()
