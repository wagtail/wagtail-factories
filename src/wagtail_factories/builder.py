from collections import defaultdict

from factory.builder import parse_declarations, BuildStep, DeclarationSet, StepBuilder


class StreamFieldFactoryException(Exception):
    pass


class InvalidDeclaration(StreamFieldFactoryException):
    pass


class DuplicateDeclaration(StreamFieldFactoryException):
    pass


class StreamFieldStepBuilder(StepBuilder):
    def __init__(self, factory_meta, extras, strategy):
        (
            # Declarations with an explicit value or nested params
            self.base_decls,
            # Declarations that should get the default for the respective child block
            self.block_default_decls,
            self.block_indices,
        ) = self.get_block_declarations(extras)
        super().__init__(factory_meta, self.base_decls, strategy)

    def validate_block_indices(self, indices):
        # Check we have a valid range of block indices: every consecutive integer from
        # 0->n. At this point expect indices to be unique - even if we got multiple declarations
        # for an index, like (0__foo__bar=1, 0__foo__baz=42), they will have been mapped into
        # base_decls like {"foo": {"bar": 1, "baz": 42}}
        unique_indices = sorted(set(indices))
        for i in range(len(unique_indices)):
            if unique_indices[i] != i:
                raise InvalidDeclaration(f"Missing block index: {i}")

    def get_block_declarations(self, extras):
        base_decls = defaultdict(dict)
        block_default_decls = set()
        block_indices = {}

        for k, v in extras.items():
            if k.isdigit():
                # We got a declaration like `1="foo_block"' - index 1 should get the
                # default value for foo_block.
                block_default_decls.add(v)

                # Store an inverse mapping so we can construct the StreamValue in order
                # later
                block_indices[v] = int(k)
            else:
                try:
                    index, block_name, *param = k.split("__", maxsplit=2)
                    index = int(index)
                except (ValueError, TypeError):
                    raise InvalidDeclaration(
                        "StreamFieldFactory declarations must be of the form "
                        "<index>=<block_name>, <index>__<block_name>=value or "
                        f"<index>__<block_name>__<param>=value, got: {k}"
                    )

                # TODO: this won't work - we might get multiple instances of the same block
                # in a definition. Maybe go back to the original representation for base_decls,
                # which was like {index: {block_name: {block_param: value}}}, or maybe can
                # rely on dicts/DeclarationSets being ordered.
                block_indices[block_name] = index

                if param:
                    # We got a declaration like 1__block_name__block_param=value.  Build
                    # up a dict of params for block_name, which will be passed through to
                    # the subfactory responsible for building block_name.
                    base_decls[block_name][param[0]] = v
                elif block_name in base_decls[index]:
                    raise DuplicateDeclaration(
                        "A value (or nested declaration) has already been declared for "
                        f"child block '{block_name}'"
                    )
                else:
                    # We got a declaration like 1__block_name=value: assume block_name to
                    # be an atomic block type, receiving a scalar value.
                    base_decls[block_name] = v

        self.validate_block_indices(block_indices.values())
        return base_decls, block_default_decls, block_indices

    def build(self, parent_step=None, force_sequence=None):
        """Build a factory instance."""
        # This method duplicated from StepBuilder so we can get access to some of the
        # internals
        pre, post = parse_declarations(
            self.extras,
            base_pre=self.factory_meta.pre_declarations,
            base_post=self.factory_meta.post_declarations,
        )

        # pre contains all fields declared on the factory class, but we're only interested
        # in those the user has declared in the instantiation.
        # TODO: do we need to apply the same logic to post?
        # TODO: what about required blocks?
        pre = DeclarationSet(
            {
                k: v
                for k, v in pre.as_dict().items()
                if k in self.base_decls or k in self.block_default_decls
            }
        )

        if force_sequence is not None:
            sequence = force_sequence
        elif self.force_init_sequence is not None:
            sequence = self.force_init_sequence
        else:
            sequence = self.factory_meta.next_sequence()

        step = BuildStep(
            builder=self,
            sequence=sequence,
            parent_step=parent_step,
        )
        step.resolve(pre)

        args, kwargs = self.factory_meta.prepare_arguments(step.attributes)

        instance = self.factory_meta.instantiate(
            step=step,
            args=args,
            kwargs=kwargs,
        )

        postgen_results = {}
        for declaration_name in post.sorted():
            declaration = post[declaration_name]
            postgen_results[declaration_name] = declaration.declaration.evaluate_post(
                instance=instance,
                step=step,
                overrides=declaration.context,
            )
        self.factory_meta.use_postgeneration_results(
            instance=instance,
            step=step,
            results=postgen_results,
        )
        return instance
