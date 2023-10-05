"""
Creator: Teddy Barthelemy
23/10/2022 - 17:00

main.sub
Player class
"""
import data.dependancies as dep
import data.entity as entity
import data.map as mapping
import data.room as room
import data.screen as screen
import data.loots as loots


class Player(entity.Entity):
    colorName = [
        [ screen.colors.FG.light_white,     "w0" ],
        [ screen.colors.FG.light_red,       "r+" ],
        [ screen.colors.FG.light_green,     "g+" ],
        [ screen.colors.FG.light_blue,      "b+" ],
        [ screen.colors.FG.light_yellow,    "y+" ],
        [ screen.colors.FG.light_cyan,      "c+" ],
        [ screen.colors.FG.light_magenta,   "p+" ]
    ]

    __slots__ = ("_money", "_inventory", "_equiped", "_pos", "_toughness", "_luck", "_speed", "_drop", "_coin", "_loot", "_map", "_username", "_username_color")

    def __init__(self, mapon=None):
        props = self.__class__.Property.Distribution(
            30,
            health = { "min": 5, "max": 25, "weight": 2 },
            attack = { "min": 2, "max": 7, "weight": 2 },
            toughness = { "min": 0, "max": 20, "increment": 5},
            luck = { "min": 0, "max": 20, "increment": 5 },
            speed = { "min": 90, "max": 110, "increment": 5 },
            coin = { "min": 50, "max": 200, "increment": 10 },
            loot = { "min": 1, "max": 5}
        ).generate()
        super().__init__(
            health=self.__class__.Property(x=lambda instance, kwargs: props.push("health")),
            attack=self.__class__.Property(x=lambda instance, kwargs: props.push("attack") * kwargs.get("pourcentage", 1))
        )
        self._toughness = 100 - props.push("toughness")
        self._luck = props.push("luck")
        self._speed = props.push("speed")
        self._coin = props.push("coin")
        self._loot = props.push("loot")
        self._map: mapping.Map = mapon
        self._money: int = 0

        self._inventory: dep.List[dep.Dict[str, dep.Any]] = [] # [ { 'item': <loot.<Loot>, 'equiped': <bool>=False }, ...]
        self._pos = [0, 0]
        self._username = "Sylvain Pierre Durif"
        self._username_color = 0

    pos = property(fget=lambda self: self._pos)
    pos_x = property(fget=lambda self: self.pos[0])
    pos_y = property(fget=lambda self: self.pos[1])

    inventory: dep.List[dep.Dict[str, dep.Any]] = property(fget=lambda self: self._inventory)

    equiped = property(fget=lambda self: [i.get("item") for i in self._inventory if i.get("equiped", False) and i.get("item", None) is not None])

    def equip(self, item: loots.Loot) -> None:
        if self.hasItem(item):
            for i in range(len(self._inventory)):
                if self._inventory[i].get("item", None) is item and not self._inventory[i].get("equiped", False) and len(self.equiped) < 10:
                    self._inventory[i]["equiped"] = True

    def earnMoney(self, v: int):
        self._money += v

    def disequip(self, item: loots.Loot) -> None:
        if self.hasItem(item):
            for i in range(len(self._inventory)):
                if self._inventory[i].get("item", None) is item and self._inventory[i].get("equiped", False):
                    self._inventory[i]["equiped"] = False

    def apply(self, item) -> None:
        """
        Apply active item effects to player

        :param loots.Loot item: Item to apply
        """
        if self.hasItem(item):
            if item.type == "active":
                for stat, value in item.effects.items():
                    if stat == "health":
                        if value[0] == "+":
                            setattr(self, f"_{stat}", min(getattr(self, f"_{stat}") + value[1], self._base_health))
                        elif value[0] == "*":
                            setattr(self, f"_{stat}", min(getattr(self, f"_{stat}") + value[1], self._base_health))
                    else:
                        if value[0] == "+":
                            setattr(self, f"_{stat}", getattr(self, f"_{stat}") + value[1])
                        elif value[0] == "*":
                            setattr(self, f"_{stat}", getattr(self, f"_{stat}") * value[1])
            self.removeItem(item)

    def removeItem(self, item) -> bool:
        """
        Remove item from inventory

        :param loots.Loot item: Item to remove
        :return bool: If item was successfully removed
        """
        if self.hasItem(item):
            for i in self._inventory:
                if i.get("item", None) is item:
                    self._inventory.remove(i)
                    return True
        return False

    def pickItem(self, item) -> bool:
        """
        Add item into inventory

        :param loots.Loot item: Item to add
        :return bool: If item was picked up (inventory can be full)
        """
        if not self.hasItem(item) and len(self._inventory) < 40:
            self._inventory.append({"item": item, "equiped": False})
            return True
        return False

    def hasItem(self, item) -> bool:
        """
        Check for item in inventory

        :param loots.Loot item: Item to search for in inventory
        :return bool: Item presence
        """
        return item in [_.get("item", None) for _ in self._inventory]

    def getStats(self, raw:bool=False) -> dep.Dict[str, dep.numeric]:
        """
        Return raw or total stats

        :param bool raw: If true only return base stats else return base stats with equiped items effects applied
        :return dep.Dict[str, dep.numeric]: Returned stats
        """
        _return = {
            "base_health": self._base_health,
            "health": self._health,
            "attack": self._attack.define(),
            "toughness": self._toughness,
            "luck": self._luck,
            "speed": self._speed,
            "loot": self._loot,
            "coin": self._coin
        }
        if raw: return _return
        _effect_add = []
        _effect_mult = []
        for obj in self.equiped:
            obj: loots.Loot
            if obj.type == "passive":
                for stat, value in obj.effects.items():
                    if value[0] == "*":
                        _effect_mult.append((stat, value[1]))
                    elif value[0] == "+":
                        _effect_add.append((stat, value[1]))
        for stat, value in _effect_add:
            _return[stat] += dep.math.ceil(value)
        for stat, value in _effect_mult:
            _return[stat] *= value
        return _return

    def _username_getter(self): return self._username
    def _username_setter(self, v): self._username = v

    username = property(fget=_username_getter, fset=_username_setter)

    @property
    def name(self):
        _return = dep.Return()
        _return.name = self.username
        _return.color = self.colorName[self._username_color]
        _return.display = f"{screen.CodeImage.Decoder.Colors.bold}{_return.color[0]}{self.username}{screen.CodeImage.Decoder.Colors.reset}"
        _return.pixel = screen.PixelImage.ColorPixel(_return.color[1])
        return _return

    def getTileOn(self):
        """
        Return actual tile player sitting on

        :return data.room.Room: Room to return
        """
        return self._map.getRoom(self._pos[0], self._pos[1])

    def defineMap(self, mapon, trigg_event:bool=True) -> None:
        """
        Define actual map

        :param mapping.Map mapon: Map
        :param bool trigg_event: Trigg event 'enter' on spawn
        """
        self._map = mapon


    def move(self, dx: int, dy: int, trigg_events:bool = True, forced:bool = False) -> None:
        """
        Move player in the grid

        :param int dx: delta X coords
        :param int dy: delta Y coords
        :param boot trigg_events: Trigg event on room change
        :param bool forced: Ignore moving restriction (1 tile / move && walls restriction), keep room validity verification
        """
        _moves = {(1, 0): "r", (-1, 0): "l", (0, 1): "b", (0, -1): "t"}
        if not forced:
            if (dx, dy) not in _moves.keys():
                return
            if self.getTileOn().walls[_moves[(dx, dy)]]:
                return
        if self._map.isValidRoom(self._pos[0] + dx, self._pos[1] + dy):
            if trigg_events: self.getTileOn().callEvent("exit")
            self._pos = [self.pos_x + dx, self.pos_y + dy]
            if trigg_events: self.getTileOn().callEvent("enter")

    def createMinimap(self, xray:bool=False, size:dep.List[int]=None) -> screen.PixelImage:
        if size is None: size = [2, 2]
        minimap = screen.PixelImage((3*(size[0]*2+1), 3*(size[1]*2+1)))
        void_room = room.VoidRoom().bakeMinimapRoom(xray=xray)
        for dx in range(minimap.size[0]):
            for dy in range(minimap.size[1]):
                room_x, room_y = dx - size[0] + self._pos[0], dy - size[1] + self._pos[1]
                r = self._map.getRoom(room_x, room_y)
                minimap.paste(void_room if r is None else r.bakeMinimapRoom(xray=xray), dx * 3, dy * 3)
        return minimap

    def __repr__(self):
        return f"<{self.__class__.__name__} : {self._health}❤ {self._attack.define()}⚔️>"
