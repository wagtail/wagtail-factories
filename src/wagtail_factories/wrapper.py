from flatdict import FlatterDict


class DictToParameteredAttribute:

    def __new__(self, factory, params):
        flat_params = dict(FlatterDict(params, delimiter='__'))
        return factory(**flat_params)
