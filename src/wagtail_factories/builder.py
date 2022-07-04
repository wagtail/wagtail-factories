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


class StreamBlockBuildStep(BuildStep):
    pass


class StructBlockStepBuilder(StepBuilder):
    pass


class StreamBlockStepBuilder(StepBuilder):
    DEFAULT_SENTINEL = object()

    def __init__(self, factory_meta, extras, strategy):
        base_decls = self.get_block_declarations(extras)
        super().__init__(factory_meta, base_decls, strategy)

    def get_block_declarations(self, extras):
        base_decls = defaultdict(dict)

        def get_key(i, name):
            # The same block type might appear more than once at any given level of the
            # StreamValue, so we can't hash on the name alone. We also can't use "__" to delimit,
            # as DeclarationSet will parse that as a deep declaration.
            return f"{i}.{name}"

        for k, v in extras.items():
            if k.isdigit():
                # We got a declaration like `1="foo_block"' - index 1 should get the
                # default value for foo_block.
                base_decls[get_key(k, v)] = self.DEFAULT_SENTINEL
            else:
                try:
                    i, name, *param = k.split("__", maxsplit=2)
                except (ValueError, TypeError):
                    raise InvalidDeclaration(
                        "StreamFieldFactory declarations must be of the form "
                        "<index>=<block_name>, <index>__<block_name>=value or "
                        f"<index>__<block_name>__<param>=value, got: {k}"
                    )
                key = get_key(i, name)

                if param:
                    # We got a declaration like 1__block_name__block_param=value.  Build
                    # up a dict of params for block_name, which will be passed through to
                    # the subfactory responsible for building block_name.
                    base_decls[key][param[0]] = v
                elif key in base_decls:
                    raise DuplicateDeclaration
                else:
                    # We got a declaration like 1__block_name=value: assume block_name to
                    # be an atomic block type, receiving a scalar value.
                    base_decls[key] = v

        return base_decls

    def build(self, parent_step=None, force_sequence=None):
        # This method mostly duplicated from StepBuilder so we can get access to some of
        # the internals
        decls = {}

        for k, v in self.extras.items():
            if v is self.DEFAULT_SENTINEL:
                attr_name = k.split(".")[1]
                # TODO: raise a helpful error here - user wanted default but none declared
                # on the StreamBlockFactory
                decls[k] = self.factory_meta.base_declarations[attr_name]
            else:
                decls[k] = v

        decls = DeclarationSet(decls)

        # TODO: With this implementation we get the same number for every use of the
        # sequence at this level of nesting - revisit?
        if force_sequence is not None:
            sequence = force_sequence
        elif self.force_init_sequence is not None:
            sequence = self.force_init_sequence
        else:
            sequence = self.factory_meta.next_sequence()

        build_step = StreamBlockBuildStep(
            builder=self,
            sequence=sequence,
            parent_step=parent_step,
        )
        build_step.resolve(decls)

        args, kwargs = self.factory_meta.prepare_arguments(build_step.attributes)

        instance = self.factory_meta.instantiate(
            step=build_step,
            args=args,
            kwargs=kwargs,
        )

        # TODO: see super().build - does it make sense to process PostGeneration
        # declarations for StreamBlockFactories?
        return instance

    def recurse(self, factory_meta, extras):
        """Recurse into a sub-factory call."""
        builder_class = factory_meta.factory._builder_class
        return builder_class(factory_meta, extras, strategy=self.strategy)
