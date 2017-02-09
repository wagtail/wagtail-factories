from collections import defaultdict

import factory
from factory.declarations import ParameteredAttribute
from wagtail.wagtailcore import blocks
from wagtail.wagtailimages.blocks import ImageChooserBlock

from wagtail_factories.factories import ImageFactory

__all__ = [
    'CharBlockFactory',
    'IntegerBlockFactory',
    'StreamFieldFactory',
    'ListBlockFactory',
    'StructBlockFactory',
    'ImageChooserBlockFactory',
]


class StreamFieldFactory(ParameteredAttribute):
    """
        Syntax:
            <streamfield>__<index>__<block_name>__<key>='foo',

    """
    def __init__(self, factories, **kwargs):
        super(StreamFieldFactory, self).__init__(**kwargs)
        self.factories = factories

    def generate(self, sequence, obj, create, params):

        result = defaultdict(lambda: defaultdict(lambda: defaultdict()))

        for key, value in params.items():
            try:
                index, block_name, param = key.split('__', 2)
            except ValueError:
                continue
            if not index.isdigit():
                continue

            index = int(index)
            result[index][block_name][param] = value

        retval = []
        for index, block_items in sorted(result.items()):
            for block_name, block_params in block_items.items():
                try:
                    block_factory = self.factories[block_name]
                except KeyError:
                    raise ValueError(
                        "No factory defined for block `%s`" % block_name)

                value = block_factory(**block_params)
                retval.append((block_name, value))
        return retval


class ListBlockFactory(factory.SubFactory):
    def __call__(self, **kwargs):
        return self.generate(None, None, True, kwargs)

    def generate(self, sequence, obj, create, params):
        subfactory = self.get_factory()

        result = defaultdict(dict)
        for key, value in params.items():
            if key.isdigit():
                result[int(key)]['value'] = value
            else:
                prefix, label = key.split('__', 2)
                if prefix and prefix.isdigit():
                    result[int(prefix)][label] = value

        retval = []
        for index, index_params in sorted(result.items()):
            item = subfactory(**index_params)
            retval.append(item)
        return retval


class BlockFactory(factory.Factory):
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, value):
        return model_class().clean(value)

    @classmethod
    def _create(cls, model_class, value):
        return model_class().clean(value)


class CharBlockFactory(BlockFactory):
    class Meta:
        model = blocks.CharBlock


class IntegerBlockFactory(BlockFactory):
    class Meta:
        model = blocks.IntegerBlock


class ChooserBlockFactory(BlockFactory):
    pass


class ImageChooserBlockFactory(ChooserBlockFactory):

    image = factory.SubFactory(ImageFactory)

    class Meta:
        model = ImageChooserBlock

    @classmethod
    def _build(cls, model_class, image):
        return image

    @classmethod
    def _create(cls, model_class, image):
        return image


class StructBlockFactory(factory.Factory):

    class Meta:
        model = blocks.StructBlock

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        block = model_class()
        return blocks.StructValue(block, [
            (
                name,
                (kwargs[name] if name in kwargs else child_block.get_default())
            )
            for name, child_block in block.child_blocks.items()
        ])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)
