from factory import SubFactory
from factory.builder import StepBuilder

try:
    from wagtail import blocks
except ImportError:
    # Wagtail<3.0
    from wagtail.core import blocks


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
        # Mapping of StreamValue index -> block name. We will use this to create a
        # StreamBlockFactory subclass with one declaration for each pair, named
        # <index>.<block_name>
        indexed_block_names = {}

        # Extra declarations passed at instantiation, renamed from <index>__<name>__... to
        # <index>.<block_name>__..., to match the declarations on the StreamBlockFactory subclass
        # we will generate. As DeclarationSet splits parameter names on "__" the
        # <index>.<block_name> keys won't cause errors for unknown declarations (0__foo_block
        # implies a declaration "0" with context "foo_block"). They will also have the important
        # property of being uniquely hashable
        extra_declarations = {}

        for k, v in extras.items():
            if k.isdigit():
                # We got a declaration like `<index>="foo_block"' - <index> should get the
                # default value for foo_block, so don't store this item in extra_declarations
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

        block_def = old_factory_meta.get_block_definition()
        # current block should be a StreamBlock
        for i, name in indexed_block_names.items():
            declared_value = old_factory_meta.base_declarations[name]
            if block_def is not None and isinstance(declared_value, SubFactory):
                # Annotate the subfactory's factory with the correct block definition for that
                # branch of the tree, so we can construct a StreamValue if there's no explicit
                # block class defined (e.g. if a nested StreamBlock was declared inline like
                # `inner_stream = StreamBlock(...))'
                child_def = block_def.child_blocks[name]
                if isinstance(child_def, blocks.ListBlock):
                    # ListBlock is a special case as it is a concrete node in the stream block
                    # tree, but ListBlockFactory is a SubFactory subclass, making it "abstract"
                    # in the factory tree
                    child_def = child_def.child_block
                declared_value.get_factory()._meta.block_def = child_def
            new_class_dict[f"{i}.{name}"] = declared_value

        new_meta_class = type(
            "Meta",
            (),
            {
                "model": old_factory_meta.model,
                "block_def": old_factory_meta.block_def,
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
