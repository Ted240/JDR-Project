"""
Creator: Teddy Barthelemy
23/10/2022 - 17:00

main.sub
Entity class
"""
import data.dependancies as dep


class Entity:
    class Property:
        class Distribution:
            __slots__ = ("_pts", "_properties", "_results",)

            _default_properties = {
                "cost": 1,
                "min": 0,
                "max": -1,
                "weight": 1,
                "increment": 1
            }

            def __init__(self, points: float, **properties):
                """
                Distribute an amount of points randomly between properties

                properties definition:
                name = {
                    ?cost (=1): Points cost to increment this property
                    ?min (=0): Minimum property value
                    ?max (=-1): Maximum property value (-1 => inf), removed from distribute list if reached
                    ?weight (=1): Choice weight
                    ?increment (=1): Value added when choose
                }

                :param int points: Points to distribute
                :param properties: Properties do distribute with
                """
                self._pts = points
                self._properties: dep.Dict[str, dep.Dict[str, dep.Any]] = {k: {vk: v[vk] if vk in v else vv for vk, vv in self.__class__._default_properties.items()} for k, v in properties.items()}
                self._results = self._resetResults()

            def generate(self):
                self._results = self._resetResults()
                pts = self._pts
                while pts > 0:
                    choices = {_: opts.get("weight", 1) for _, opts in self._properties.items() if (True if opts.get("max") == -1 else (self._results.get(_) + opts.get("increment") <= opts.get("max"))) and opts.get("cost") <= pts}
                    if len(choices) <= 0:
                        pts = 0
                    else:
                        pick = dep.rnd.choices(list(choices.keys()), list(choices.values()))[0]
                        pts -= self._properties.get(pick).get("cost", 1)
                        self._results[pick] += self._properties.get(pick).get("increment", 1)
                return self

            def _resetResults(self) -> dep.Dict[str, int]:
                return {k: opts.get("min", 0) for k, opts in self._properties.items()}

            def push(self, *keys):
                """
                Return generated values

                :param dep.List[str] keys: Keys to return (if None return all)
                :return:
                """
                if not keys:
                    keys = self._properties.keys()
                if len(keys) == 1:
                    return self._results.get(keys[0])
                else:
                    return tuple([self._results.get(k) for k in keys])
        """
        Property definer
        """

        def __init__(self, x: dep.Union[int, dep.Callable], y: int = None):
            """
            Define propery of an object ether fix (int) or varable (int, int)

            :param dep.Union[int, dep.Callable] x: param min (int or Callable(instance))
            :param int y: ?param max
            """
            self.x = x
            self.y = y if isinstance(self.x, int) else None

        def define(self, instance=None, **kwargs) -> int:
            """
            Define value to return

            :param instance: Enemy
            :param kwargs: Additionnal values
            :return: Chosen value
            """
            if self.y is None:
                return self.x if isinstance(self.x, int) else self.x(instance=instance, kwargs=kwargs)
            else:
                return dep.rnd.randint(self.x, self.y)

        def __repr__(self):
            return f"{self.x}" if self.y is None else f"[{self.x}:{self.y}]"

    __slots__ = ("_base_health", "_health", "_attack",)

    def __init__(self,
                 *,
                 health,
                 attack
                 ):
        """
        Create new Entity

        :param Entity.Property health: Health setter
        :param Entity.Property attack: Attack setter
        """
        self._base_health = health.define()
        self._health = self._base_health
        self._attack = attack

    name = property(fget=lambda self: self.__class__.__name__)

    def prop(self, name: str):
        """
        Return a property

        :param str name: Property name
        :return: Property value
        """
        return self[name]

    def __getitem__(self, item: str):
        if f"_{item}" in [_ for _ in dir(self) if not _.startswith("__")] and item not in []:  # item not in [...] => exclude list
            return getattr(self, f"_{item}")

    def giveDamage(self, damage) -> int:
        """
        Give damage to entity

        :param int damage: Damage value
        """
        self._health = max(0, self._health - dep.math.ceil(damage))
        return dep.math.ceil(damage)

    def getDamage(self, **kwargs) -> int:
        """
        Get damage that entity give

        :return int: Damage value
        """
        return dep.math.floor(self._attack.define(**kwargs)) if self.life_percent > 0 else 0

    @property
    def is_dead(self):
        return self._health <= 0

    @property
    def life_percent(self) -> float:
        """
        Entity life pourcentage

        :return float: Pourcentage (.2f)
        """
        return round(self._health / self._base_health, 2)

    def __repr__(self):
        return f"<{self.name} : {self._health}/{self._base_health}❤>"
