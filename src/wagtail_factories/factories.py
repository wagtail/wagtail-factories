import factory
from django.utils.text import slugify
from wagtail.wagtailcore.models import Collection, Page
from wagtail.wagtailimages.models import get_image_model

__all__ = [
    'CollectionFactory',
    'ImageFactory',
    'PageFactory',
]


class MP_NodeFactory(factory.DjangoModelFactory):

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent = kwargs.pop('parent', None)
        if not parent:
            return model_class.add_root(**kwargs)
        instance = model_class(**kwargs)
        return parent.add_child(instance=instance)


class CollectionFactory(MP_NodeFactory):
    name = 'Test collection'

    class Meta:
        model = Collection


class PageFactory(MP_NodeFactory):
    title = 'Test page'
    slug = factory.LazyAttribute(lambda obj: slugify(obj.title))

    class Meta:
        model = Page


class ImageFactory(factory.DjangoModelFactory):

    class Meta:
        model = get_image_model()

    collection = factory.SubFactory(CollectionFactory)
    file = factory.django.ImageField()
