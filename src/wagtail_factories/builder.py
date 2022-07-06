from collections import defaultdict

from factory.builder import (
    parse_declarations,
    BuildStep,
    DeclarationSet,
    StepBuilder,
    Resolver,
)


class StreamFieldFactoryException(Exception):
    pass


class InvalidDeclaration(StreamFieldFactoryException):
    pass


class DuplicateDeclaration(StreamFieldFactoryException):
    pass


class UnknownChildBlockFactory(StreamFieldFactoryException):
    pass


class BaseBlockStepBuilder(StepBuilder):
    def recurse(self, factory_meta, extras):
        """Recurse into a sub-factory call."""
        builder_class = factory_meta.factory._builder_class
        return builder_class(factory_meta, extras, strategy=self.strategy)


class StructBlockStepBuilder(BaseBlockStepBuilder):
    pass


class ListBlockStepBuilder(BaseBlockStepBuilder):
    pass


class StreamBlockStepBuilder(BaseBlockStepBuilder):
    def __init__(self, factory_meta, extras, strategy):
        indexed_block_names, extra_declarations = self.get_block_declarations(
            factory_meta, extras
        )
        new_factory_class = self.create_factory_class(factory_meta, indexed_block_names)
        super().__init__(new_factory_class._meta, extra_declarations, strategy)

    def get_block_declarations(self, factory_meta, extras):
        # Mapping of stream value index -> block type so we can construct a StreamBlockFactory
        # subclass with a declaration for each user-requested block
        indexed_block_names = {}

        # Declarations passed at instantiation, renamed from <index>__<name>__... to
        # <index>.<block_name>__..., so we can create a unique declaration on our dynamically
        # created StreamBlockFactory subclass for each user-requested block only
        extra_declarations = {}

        for k, v in extras.items():
            if k.isdigit():
                # We got a declaration like `<index>="foo_block"' - <index> should get the
                # default value for foo_block.
                if v not in factory_meta.base_declarations:
                    raise UnknownChildBlockFactory(
                        f"No factory defined for block '{v}'"
                    )
                key = int(k)
                if key in indexed_block_names and indexed_block_names[key] != v:
                    raise DuplicateDeclaration(
                        f"Multiple declarations for index {key} at this level of nesting "
                        f"({v}, {indexed_block_names[key]})"
                    )
                indexed_block_names[key] = v

                # Don't store this key in extra_declarations, it will get the factory's default
                # value
            else:
                try:
                    i, name, *param = k.split("__", maxsplit=2)
                    key = int(i)
                except (ValueError, TypeError):
                    raise InvalidDeclaration(
                        "StreamFieldFactory declarations must be of the form "
                        "<index>=<block_name>, <index>__<block_name>=value or "
                        f"<index>__<block_name>__<param>=value, got: {k}"
                    )
                if key in indexed_block_names and indexed_block_names[key] != name:
                    raise DuplicateDeclaration(
                        f"Multiple declarations for index {key} at this level of nesting "
                        f"({name}, {indexed_block_names[key]})"
                    )
                indexed_block_names[key] = name
                extra_declarations[f"{i}." + "__".join([name, *param])] = v

        return indexed_block_names, extra_declarations

    def create_factory_class(self, old_factory_meta, indexed_block_names):
        # Create a new StreamBlockFactory subclass, with a declaration for each block the user
        # requested at instantiation. This way we can rely on the factory_boy internals for
        # object generation
        new_class_dict = {}
        for i, name in indexed_block_names.items():
            new_class_dict[f"{i}.{name}"] = old_factory_meta.base_declarations[name]

        new_meta_class = type(
            "Meta",
            (),
            {
                "model": old_factory_meta.model,
                "abstract": old_factory_meta.abstract,
                "strategy": old_factory_meta.strategy,
                "inline_args": old_factory_meta.inline_args,
                "exclude": old_factory_meta.exclude,
                "rename": old_factory_meta.rename,
            },
        )
        new_class_dict["Meta"] = new_meta_class

        from wagtail_factories.blocks import StreamBlockFactory

        return type(
            "_GeneratedStreamBlockFactory", (StreamBlockFactory,), new_class_dict
        )
