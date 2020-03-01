from collections import OrderedDict


class MultiDict(OrderedDict):
    _unique = 0
    TOKEN = '_'

    def __setitem__(self, key, val):
        if isinstance(val, dict):
            self._unique += 1
            key += f"_{self._unique}"
        OrderedDict.__setitem__(self, key, val)
