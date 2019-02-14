import keyword
from collections import abc


class DevOpsJSON:
    def __new__(cls, arg):
        if isinstance(arg, abc.Mapping):
            return super().__new__(cls)
        elif isinstance(arg, abc.MutableSequence):
            return [cls(item) for item in arg]
        else:
            return arg

    def __init__(self, wrapped):
        self._data = {}

        for key, value in wrapped.items():
            if keyword.iskeyword(key):
                key += '_'
            self._data[key] = value

    def __getattr__(self, item):
        if hasattr(self._data, item):
            return getattr(self._data, item)
        return DevOpsJSON(self._data[item])

    def __getitem__(self, item):
        return self._data[item]