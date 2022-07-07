from collections import defaultdict

import factory
from factory.declarations import ParameteredAttribute
from wagtail.images.blocks import ImageChooserBlock

try:
    from wagtail import blocks
except ImportError:
    # Wagtail<3.0
    from wagtail.core import blocks

from wagtail_factories.builder import (
    StreamBlockStepBuilder,
    StructBlockStepBuilder,
    ListBlockStepBuilder,
)
from wagtail_factories.factories import ImageFactory
from wagtail_factories.options import StreamBlockFactoryOptions

__all__ = [
    "CharBlockFactory",
    "IntegerBlockFactory",
    "StreamBlockFactory",
    "StreamFieldFactory",
    "ListBlockFactory",
    "StructBlockFactory",
    "ImageChooserBlockFactory",
]


class StreamBlockFactory(factory.Factory):
    _options_class = StreamBlockFactoryOptions
    _builder_class = StreamBlockStepBuilder

    @classmethod
    def _generate(cls, strategy, params):
        if cls._meta.abstract and not hasattr(cls, "__generate_abstract__"):
            raise factory.errors.FactoryError(
                "Cannot generate instances of abstract factory %(f)s; "
                "Ensure %(f)s.Meta.model is set and %(f)s.Meta.abstract "
                "is either not set or False." % dict(f=cls.__name__)
            )
        step = cls._builder_class(cls._meta, params, strategy)
        return step.build()

    @classmethod
    def _construct_stream(cls, block_class, *args, **kwargs):
        if not kwargs:
            return []

        def get_index(key):
            return int(key.split(".")[0])

        stream_data = [None] * (max(map(get_index, kwargs.keys())) + 1)
        for indexed_block_name, value in kwargs.items():
            i, name = indexed_block_name.split(".")
            stream_data[int(i)] = (name, value)

        if cls._meta.model is None:
            # We got an old style definition, so aren't aware of a StreamBlock class for
            # the StreamField's child blocks.
            return stream_data
        return blocks.StreamValue(cls._meta.model(), stream_data)

    @classmethod
    def _build(cls, block_class, *args, **kwargs):
        return cls._construct_stream(block_class, *args, **kwargs)

    @classmethod
    def _create(cls, block_class, *args, **kwargs):
        return cls._construct_stream(block_class, *args, **kwargs)

    class Meta:
        abstract = True


class StreamFieldFactory(ParameteredAttribute):
    """
    Syntax:
        <streamfield>__<index>__<block_name>__<key>='foo',

    Syntax to generate blocks with default factory values:
        <streamfield>__<index>=<block_name>

    """

    def __init__(self, block_types, **kwargs):
        super().__init__(**kwargs)
        if isinstance(block_types, dict):
            # Old style definition, dict mapping block name -> block factory
            self.stream_block_factory = type(
                "_GeneratedStreamBlockFactory",
                (StreamBlockFactory,),
                {**block_types, "__generate_abstract__": True},
            )
        elif isinstance(block_types, type) and issubclass(
            block_types, StreamBlockFactory
        ):
            self.stream_block_factory = block_types
        else:
            raise TypeError(
                "StreamFieldFactory argument must be a StreamBlockFactory subclass or dict "
                "mapping block names to factories"
            )

    def evaluate(self, instance, step, extra):
        return self.stream_block_factory(**extra)


class ListBlockFactory(factory.SubFactory):
    _builder_class = ListBlockStepBuilder

    def __call__(self, **kwargs):
        return self.evaluate(None, None, kwargs)

    def evaluate(self, instance, step, extra):
        subfactory = self.get_factory()

        result = defaultdict(dict)
        for key, value in extra.items():
            if key.isdigit():
                result[int(key)]["value"] = value
            else:
                prefix, label = key.split("__", maxsplit=1)
                if prefix and prefix.isdigit():
                    result[int(prefix)][label] = value

        retval = []
        for index, index_params in sorted(result.items()):
            item = subfactory(**index_params)
            retval.append(item)
        return retval


class StructBlockFactory(factory.Factory):
    _builder_class = StructBlockStepBuilder

    class Meta:
        abstract = True
        model = blocks.StructBlock

    @classmethod
    def _construct_struct_value(cls, block_class, params):
        return blocks.StructValue(
            block_class(),
            [(name, value) for name, value in params.items()],
        )

    @classmethod
    def _build(cls, block_class, *args, **kwargs):
        return cls._construct_struct_value(block_class, kwargs)

    @classmethod
    def _create(cls, block_class, *args, **kwargs):
        return cls._construct_struct_value(block_class, kwargs)


class BlockFactory(factory.Factory):
    _builder_class = factory.builder.StepBuilder

    class Meta:
        abstract = True

    @classmethod
    def _construct_block(cls, block_class, *args, **kwargs):
        if kwargs.get("value"):
            return block_class().clean(kwargs["value"])
        return block_class().get_default()

    @classmethod
    def _build(cls, block_class, *args, **kwargs):
        return cls._construct_block(block_class, *args, **kwargs)

    @classmethod
    def _create(cls, block_class, *args, **kwargs):
        return cls._construct_block(block_class, *args, **kwargs)


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
