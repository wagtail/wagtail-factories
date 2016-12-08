import factory
from django.utils.text import slugify
from wagtail.wagtailcore.models import Collection, Page, Site
from wagtail.wagtailimages.models import get_image_model

__all__ = [
    'CollectionFactory',
    'ImageFactory',
    'PageFactory',
    'SiteFactory',
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


class CollectionMemberFactory(factory.DjangoModelFactory):
    collection = factory.SubFactory(CollectionFactory)


class ImageFactory(CollectionMemberFactory):

    class Meta:
        model = get_image_model()

    file = factory.django.ImageField()


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = factory.Sequence(lambda n: 81 + n)
    site_name = 'Test site'
    root_page = factory.SubFactory(PageFactory)
    is_default_site = False

    class Meta:
        model = Site
