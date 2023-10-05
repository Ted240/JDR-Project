"""
Creator: Teddy Barthelemy
23/09/2022 - 10:50

main.sub
Room class
"""
from data import dependancies as dep
from data import enemy, loots
import data.screen as screen
import data.fight as fight
# import data.map as mapping
# import data.player as player


class VoidRoom:
    __slots__ = ("_pos", "_map", "_events",)

    validRoom = False
    interactive = False

    def __init__(self, pos:dep.Tuple[int, int] = (0, 0), mapon = None):
        self._pos = pos
        self._map = mapon
        self._events = {
            "enter": self.on_enter,
            "exit": self.on_enter,
            "conquire": self.on_conquire,
            "discover": self.on_discover,
            "interact": self.on_interaction
        }

    pos = property(fget=lambda self: self._pos)
    pos_x = property(fget=lambda self: self.pos[0])
    pos_y = property(fget=lambda self: self.pos[1])

    def replaceWith(self, obj) -> None:
        """
        Replace this room with another

        :param obj: Room for replacement
        """
        if self._map is not None: self._map.putRoom(*self._pos, obj=obj(self._pos, self._map))

    def setEvent(self, name: str, funct: dep.Callable) -> None:
        """
        Define new event

        :param str name: Name of the event
        :param dep.Callable funct: Function to set
        """
        if name in self._events.keys():
            self._events[name] = funct

    def callEvent(self, name: str, **kwargs) -> dep.Any:
        """
        Call an event

        :param name: Event to call
        :param kwargs: Kwargs to pass
        :return: Returned value of event
        """
        if name in self._events.keys():
            return self._events[name](**kwargs)

    def on_enter(self, **kw): pass
    def on_exit(self, **kw): pass
    def on_conquire(self, **kw): pass
    def on_discover(self, **kw): pass
    def on_interaction(self, **kw): pass

    def bakeMinimapRoom(self, xray:bool=False) -> screen.PixelImage:
        """
        Make room image for minimap

        :param bool xray: If XRay mode is activated
        :return screen.PixelImage: Image created
        """
        return screen.PixelImage((3, 3), fill=screen.PixelImage.PatternPixel("//", color=screen.colors.FG.light_black, endcolor=screen.colors.reset))

    def __repr__(self):
        return f"<{self.__class__.__name__} ({self.pos_x};{self.pos_y})>"


class Room(VoidRoom):
    __slots__ = ("_conquired", "_walls", "_explored", "_discovered")

    validRoom = True

    def __init__(self, pos:dep.Tuple[int, int], mapon):
        super().__init__(pos, mapon)
        self._conquired = False
        self._explored = False
        self._discovered = False
        self._walls = {"l": False, "r": False, "t": False, "b": False}

    walls = property(fget=lambda self: self._walls)

    isDiscovered = property(fget=lambda self: self._discovered)
    isExplored = property(fget=lambda self: self._explored)
    isConquired = property(fget=lambda self: self._conquired)

    @property
    def distance(self): return dep.math.sqrt((self._pos[0]**2)+(self._pos[1]**2))

    def defineWalls(
            self,
            *,
            l:bool=None,
            r:bool=None,
            t:bool=None,
            b:bool=None
    ):
        """
        Change walls properties

        :param bool l: Set left wall presence
        :param bool r: Set right wall presence
        :param bool t: Set top wall presence
        :param bool b: Set bottom wall presence
        """
        self._walls.update(
            {
                s: v for s, v in
                {
                    "l": l,
                    "r": r,
                    "t": t,
                    "b": b
                }.items()
                if v is not None
            }
        )

    def on_enter(self, **kw):
        self._explored = True
        self._discovered = True
        for room in [r for s, r in self._map.neighborRoom(self.pos_x, self.pos_y).items() if s in [_s for _s, _w in self.walls.items() if not _w]]:
            if self._map.isAValidRoom(room):
                if not room.isDiscovered:
                    room.callEvent("discover", f=self)

    def on_discover(self, **kw):
        self._discovered = True

    def optionalsPillars(self) -> dep.Dict[str, bool]:
        """
        Return optional wall corners
        Only return True if two adjacent walls are absent
        Use `uselessPillars()` method to get a verification to actually remove the actual pillar

        :return dep.Dict[str, bool]: Dictionnary of corners with their necessery state
        """
        return {v: not self.walls[v[0]] and not self.walls[v[1]] for v in ["lt", "rt", "lb", "rb"]}

    def uselessPillars(self, *sides):
        if len(sides) == 0: sides = ["lt", "rt", "lb", "rb"]
        _data = { # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Corner checking matrix
            "lt": { (-1,  0): "rt", (-1, -1): "rb", ( 0, -1): "lb" },
            "rt": { ( 0, -1): "rb", ( 1, -1): "lb", ( 1,  0): "lt" },
            "rb": { ( 1,  0): "lb", ( 1,  1): "lt", ( 0,  1): "rt" },
            "lb": { ( 0,  1): "lt", (-1,  1): "rt", (-1,  0): "rb" }
        }
        return {
            corner:
                all([*[
                    self._map. #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Get pillar state of adjacent rooms (get map)
                    getRoom(pos[0]+self.pos_x, pos[1]+self.pos_y). #- - - - - - - - - - - - / (get room)
                    optionalsPillars()[cor] #- - - - - - - - - - - - - - - - - - - - - - -  / (get pillars state)
                    if self._map.isValidRoom(pos[0]+self.pos_x, pos[1]+self.pos_y) else # - Check each room validity
                    False # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Invalid room was detected
                    for pos, cor in _data[corner].items() # - - - - - - - - - - - - - - - - All other room with the same pillar
                ], self.optionalsPillars()[corner]]) #- - - - - - - - - - - - - - - - - - - Actual room with the pillar
                if corner in sides else # - - - - - - - - - - - - - - - - - - - - - - - - - Ignore unrequested corners (arguments)
                False # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Corner not requested (compute speed optimization)
            for corner in ["lt", "rt", "lb", "rb"]
        }

    def bakeMinimapRoom(self, xray:bool=False) -> screen.PixelImage:
        """
        Make room image for minimap

        :param bool xray: If XRay mode is activated
        :return screen.PixelImage: Image created
        """
        if self._explored and not xray: xray = True
        room_screen = super().bakeMinimapRoom(xray)
        if self._discovered:
            _ulc = self.uselessPillars() # UseLess Corners
            room_pattern = "".join([
                {(False, False): "╝", (True, False): "║", (False, True): "═", (True, True): "╔"}[(self.walls["l"], self.walls["t"])], # Top left corner design
                "════" if self.walls["t"] else "    ", # Top wall
                {(False, False): "╚", (True, False): "║", (False, True): "═", (True, True): "╗"}[(self.walls["r"], self.walls["t"])], # Top right corner design
                "\n",
                "║" if self.walls["l"] else " ", # Left wall
                "    ",
                "║" if self.walls["r"] else " ", # Right wall
                "\n",
                {(False, False): "╗", (True, False): "║", (False, True): "═", (True, True): "╚"}[(self.walls["l"], self.walls["b"])], # Bottom left corner design
                "════" if self.walls["b"] else "    ", # Bottom wall
                {(False, False): "╔", (True, False): "║", (False, True): "═", (True, True): "╝"}[(self.walls["r"], self.walls["b"])], # Bottom right corner design
            ])
            room_screen.putGrid(
                0, 0,
                screen.PixelImage.TextPixel(
                    room_pattern
                )
            )
            if _ulc["lt"]: room_screen.putGrid(0, 0, screen.PixelImage.PatternPixel("▀ ", screen.colors.FG.light_black, screen.colors.reset))
            if _ulc["rt"]: room_screen.putGrid(2, 0, screen.PixelImage.PatternPixel(" ▀", screen.colors.FG.light_black, screen.colors.reset))
            if _ulc["lb"]: room_screen.putGrid(0, 2, screen.PixelImage.PatternPixel("▄ ", screen.colors.FG.light_black, screen.colors.reset))
            if _ulc["rb"]: room_screen.putGrid(2, 2, screen.PixelImage.PatternPixel(" ▄", screen.colors.FG.light_black, screen.colors.reset))
            if self._explored:
                if self._conquired:
                    room_screen.putGrid(1, 1, screen.PixelImage.PatternPixel("✓✓", color=screen.colors.FG.green, endcolor=screen.colors.reset))
                else:
                    pass
            else:
                room_screen.putGrid(1, 1, screen.PixelImage.PatternPixel("??", color=screen.colors.FG.black, endcolor=screen.colors.reset))
            if self._map.player:
                if self._map.player.getTileOn() is self:
                    room_screen.putGrid(1, 1, self._map.player.name.pixel)
        return room_screen


class LeveledRoom(Room):
    __slots__ = ("_level",)

    validRoom = False

    def __init__(self, pos:dep.Tuple[int, int], mapon):
        super().__init__(pos, mapon)
        self._level = self.distance * (dep.rnd.randint(80, 120) / 100)

    @property
    def level(self): return self._level

    def bakeMinimapRoom(self, xray:bool=False) -> screen.PixelImage:
        """
        Make room image for minimap

        :param bool xray: If XRay mode is activated
        :return screen.PixelImage: Image created
        """
        if self._explored and not xray: xray = True
        room_screen = super().bakeMinimapRoom(xray)
        return room_screen


class DungeonRoom(LeveledRoom):
    __slots__ = ("_creatures",)

    validRoom = True
    interactive = True

    def __init__(self, pos:dep.Tuple[int, int], mapon):
        super().__init__(pos, mapon)
        self._creatures: dep.List[enemy.Enemy] = []
        self.generate()

    def on_conquire(self, **kw):
        self._conquired = True

    @property
    def creatures_level(self): return sum([_.level for _ in self._creatures])

    @property
    def creatures(self): return self._creatures

    def generate(self):
        while self.creatures_level < dep.math.floor(self.level) and len(self._creatures) < 8:
            valids = [obj for obj in enemy.Enemy.__subclasses__() if self.creatures_level + obj.level <= self.level]
            # noinspection PyArgumentList
            self._creatures.append(
                dep.rnd.choices(
                    valids,
                    weights=[_.weight for _ in valids]
                )[0]()
            )
        # print(self._creatures, len(self._creatures) == 0)
        if len(self._creatures) == 0:
            self.replaceWith(Room)

    def bakeMinimapRoom(self, xray:bool=False) -> screen.PixelImage:
        """
        Make room image for minimap

        :param bool xray: If XRay mode is activated
        :return screen.PixelImage: Image created(
        """
        if self._explored and not xray: xray = True
        room_screen = super().bakeMinimapRoom(xray)
        if xray:
            for wall_side, pattern in {"t": ["──", [1, 0]], "l": ["▕ ", [0, 1]], "r": [" ▏", [2, 1]], "b": ["──", [1, 2]]}.items():
                if not self.walls[wall_side]: room_screen.putGrid(pattern[1][0], pattern[1][1], screen.PixelImage.PatternPixel(pattern[0], screen.colors.FG.red, screen.colors.reset))
        return room_screen

    def fight(self, gd):
        for enemy in self._creatures:
            enemy.getTexture().toScreen().printScreen()
            dep.wait(1)
        while True:
            # Player attacks enemies
            attackBar = fight.AccuracyBar(100, len(self._creatures), 5)
            attackBar.targets = [e.makeAttackTarget() for e in self._creatures]
            damages = attackBar.run(1)
            print(damages)
            sum_damage = []
            for _ in damages:
                _sum_damage = []
                for enemy_i, damage in enumerate(_):
                    _sum_damage.append(
                        self._creatures[enemy_i].giveDamage(
                            gd.carte.player.getStats().get("attack", 0) *
                            damage
                        ) if not self._creatures[enemy_i].is_dead else 0
                    )
                sum_damage.append(str(sum(_sum_damage)))
            print(screen.color(f"Damage given: {', '.join(sum_damage)}", screen.colors.bold + screen.colors.FG.light_green, screen.colors.reset))
            if all([_.is_dead for _ in self._creatures]):
                self.callEvent("conquire")
                total_money = sum([_.drops(player=gd.carte.player)[1] for _ in self._creatures])
                gd.carte.player.earnMoney(total_money)
                print(screen.color(f"Money earned: {total_money}$", screen.colors.bold + screen.colors.FG.light_green, screen.colors.reset))
                dep.wait(2)
                break
            dep.wait(1)

            # Enemies attack player
            attackBar.targets = [e.makeDamageTarget() for e in self._creatures]
            damages = attackBar.run(len([_ for _ in self._creatures if _.life_percent > 0]))
            # print(damages, [max([damage[entity_i] for damage in damages]) for entity_i in range(len(self._creatures))])
            sum_damage = []
            for enemy_i, damage in enumerate([max([damage[entity_i] for damage in damages]) for entity_i in range(len(self._creatures))]):
                sum_damage.append(
                    gd.carte.player.giveDamage(
                        self._creatures[enemy_i].getDamage() *
                        (1-damage) *
                        round(gd.carte.player.getStats().get("toughness", 0)/100, 2)
                    )
                )
            print(screen.color(f"Damage taken: {(', '.join([str(_) for _ in sum_damage if _ > 0])) if len([_ for _ in sum_damage if _ > 0]) > 0 else '0'}\nHealth: {gd.carte.player.prop('health')}❤ ", screen.colors.bold + screen.colors.FG.light_green, screen.colors.reset))
            if gd.carte.player.is_dead:
                print("Vous êtes mort :(")
                exit(0)
            dep.wait(1)
        dep.clearScreen()


class LootRoom(LeveledRoom):
    __slots__ = ("_chests",)

    validRoom = True
    interactive = True

    def __init__(self, pos:dep.Tuple[int, int], mapon):
        super().__init__(pos, mapon)
        self._chests: dep.List[loots.Chest] = []
        self.generate()

    def generate(self):
        self._chests = [loots.Chest(self) for i in range(1)]
        for chest in self._chests:
            chest.generate()

    def bakeMinimapRoom(self, xray:bool=False) -> screen.PixelImage:
        """
        Make room image for minimap

        :param bool xray: If XRay mode is activated
        :return screen.PixelImage: Image created(
        """
        if self._explored and not xray: xray = True
        room_screen = super().bakeMinimapRoom(xray)
        if xray:
            for wall_side, pattern in {"t": ["──", [1, 0]], "l": ["▕ ", [0, 1]], "r": [" ▏", [2, 1]], "b": ["──", [1, 2]]}.items():
                if not self.walls[wall_side]: room_screen.putGrid(pattern[1][0], pattern[1][1], screen.PixelImage.PatternPixel(pattern[0], screen.colors.FG.light_yellow, screen.colors.reset))
        return room_screen

    def on_interaction(self, **kw):
        # Chest opening
        def _lootChest():
            for chest in self._chests:
                for item in [_ for _ in chest.content]:
                    if self._map.player.pickItem(item):
                        chest.pop(item)
                    else:
                        return False
            return True

        # print([_.content for _ in self._chests])
        if not _lootChest():
            print("Inventory filled")
        dep.wait(1)
