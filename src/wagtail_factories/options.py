from factory import enums
from factory.base import FactoryOptions, StubObject


class StreamBlockFactoryOptions(FactoryOptions):
    def instantiate(self, step, args, kwargs):
        block_class = self.get_model_class()
        if step.builder.strategy == enums.BUILD_STRATEGY:
            return self.factory._build(
                block_class, step.builder.block_indices, step, *args, **kwargs
            )
        elif step.builder.strategy == enums.CREATE_STRATEGY:
            return self.factory._create(
                block_class, step.builder.block_indices, step, *args, **kwargs
            )
        else:
            assert step.builder.strategy == enums.STUB_STRATEGY
            return StubObject(**kwargs)
