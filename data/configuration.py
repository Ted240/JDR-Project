"""
Creator: Teddy Barthelemy
28/10/2022 - 03:10

main.sub
Gameplay configuration classes
"""
import data.dependancies as dep


class ConfigVar:
    __slots__ = ("_value", "_doc",)

    def __init__(self, default, doc: str = "No doc"):
        self._value = default
        self._doc = doc

    def get(self): return self._value

    def set(self, v): self._value = v

    value = v = property(get, set)
    doc = property(fget=lambda self: self._doc)

    def __repr__(self):
        return f"<Value: {self._value}>"


class Configuration:
    # Chest configuration
    chest_max_items = ConfigVar(5, "Max items a chest can contain")

    # Fight configuration
    fight_max_entity = 8, "Max entities per fights"

    def __init__(self, **kwargs):
        for k, v in self.items().items():
            if not isinstance(v, ConfigVar):
                setattr(self, k, ConfigVar(*v) if isinstance(getattr(self, k), tuple) == 1 else ConfigVar(v))
        for k, v in kwargs.items():
            if hasattr(self, k):
                if isinstance(getattr(self, k), ConfigVar):
                    getattr(self, k).v = v

    def get(self, key):
        if key in self:
            return getattr(self, key).v

    def set(self, key, v):
        getattr(self, key).v = v

    def doc(self, key):
        if key in self:
            return getattr(self, key).doc
        return "No key"

    def keys(self):
        return self.items().keys()

    def items(self):
        return {name: getattr(self, name) for name in dir(self) if
                not name.startswith("_") and not isinstance(getattr(self, name), dep.Callable)}

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, item):
        return item in self.keys()

    def __repr__(self):
        return f"<Configuration: {len(self.keys())} entries>"
