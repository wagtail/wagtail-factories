import factory
from django.utils.text import slugify
from factory.utils import extract_dict
from wagtail.wagtailcore.models import Collection, Page, Site
from wagtail.wagtailimages import get_image_model

__all__ = [
    'CollectionFactory',
    'ImageFactory',
    'PageFactory',
    'SiteFactory',
]


class MP_NodeFactory(factory.DjangoModelFactory):

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class(**kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = model_class(**kwargs)
        instance._parent_factory = cls
        return instance

    @factory.post_generation
    def parent(self, create, extracted_parent, **parent_kwargs):
        if create:
            if extracted_parent and parent_kwargs:
                raise ValueError('Cant pass a parent instance and attributes')

            if parent_kwargs:
                parent = self._parent_factory(**parent_kwargs)
            else:
                # Assume root node if no parent passed
                parent = extracted_parent

            if parent:
                parent.add_child(instance=self)
            else:
                type(self).add_root(instance=self)

            # tidy up after ourselves
            del self._parent_factory


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
