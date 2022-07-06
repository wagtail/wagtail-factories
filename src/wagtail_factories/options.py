from factory import enums, declarations
from factory.base import FactoryOptions, StubObject


class StreamBlockFactoryOptions(FactoryOptions):
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
        kwargs = {
            k: v
            for k, v in kwargs.items()
            if (_k := get_base_name(k)) not in self.exclude
            and _k not in self.parameters
            and v is not declarations.SKIP
        }

        return (), kwargs
