import factory
from django.utils.text import slugify
from factory.utils import extract_dict
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
    def _build(cls, model_class, *args, **kwargs):
        kwargs.pop('parent', None)
        return model_class(**kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        parent_passed = 'parent' in kwargs
        parent = kwargs.pop('parent', None)
        parent_kwargs = extract_dict('parent', kwargs)

        if parent and parent_kwargs:
            raise ValueError('Cant pass a parent instance and attributes')

        if parent_kwargs:
            parent = cls(**parent_kwargs)

        if not parent and not parent_passed:
            raise ValueError(
                "`parent` is a required kwarg. If you want to create a root " +
                "object then pass `parent=None`")

        if parent:
            instance = model_class(**kwargs)
            return parent.add_child(instance=instance)
        else:
            return model_class.add_root(**kwargs)


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
    collection = factory.SubFactory(CollectionFactory, parent=None)


class ImageFactory(CollectionMemberFactory):

    class Meta:
        model = get_image_model()

    title = 'An image'
    file = factory.django.ImageField()


class SiteFactory(factory.DjangoModelFactory):
    hostname = 'localhost'
    port = factory.Sequence(lambda n: 81 + n)
    site_name = 'Test site'
    root_page = factory.SubFactory(PageFactory, parent=None)
    is_default_site = False

    class Meta:
        model = Site
