from factory import declarations
from factory.base import FactoryOptions, OptionDefault


class BlockFactoryOptions(FactoryOptions):
    def _build_default_options(self):
        options = super()._build_default_options()
        options.append(OptionDefault("block_def", None))
        return options


class StreamBlockFactoryOptions(BlockFactoryOptions):
    def prepare_arguments(self, attributes):
        # Like the base implementation, but ignore args as they are not relevant
        # for instantiating StreamValues.

        def get_base_name(key):
            # Keys at this point will be like <index>.<block_name>
            return key.split(".")[1]

        kwargs = dict(attributes)
        # 1. Extension points
        kwargs = self.factory._adjust_kwargs(**kwargs)

        # 2. Remove hidden objects
        filtered_kwargs = {}
        for k, v in kwargs.items():
            base_name = get_base_name(k)
            if (
                base_name not in self.exclude
                and base_name not in self.parameters
                and v is not declarations.SKIP
            ):
                filtered_kwargs[k] = v

        return (), filtered_kwargs

    def get_block_definition(self):
        if self.block_def is not None:
            return self.block_def
        elif self.model is not None:
            return self.model()
