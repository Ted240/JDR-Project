"""
Creator: Teddy Barthelemy
23/09/2022 - 10:43

main.sub
Map class
"""

import data.dependancies as dep
import typing as t
import data.room as room
import data.player as player
import data.screen as screen


class Map:
    """
    Map object
    """
    __slots__ = ("_grid", "_players",)

    def __init__(self, size: t.Tuple[int, int]):
        self._players = None
        self._grid: dep.List[dep.List[room.Room]] = []
        self.create(size[0], size[1])

    def setPlayer(self, instance) -> None:
        """
        Add a player instance on the map

        :param player.Player instance: Instance to add
        """
        self._players = instance
        instance.defineMap(self)

    def create(self, x: int, y: int) -> None:
        """
        Create map and fill it with rooms

        :param x: Map size X
        :param y: Map size Y
        """
        self._grid = [[room.Room((_x, _y), self) for _x in range(x)] for _y in range(y)]

    def getRoom(self, x: int, y: int): # -> room.VoidRoom (ciruclar import)
        """
        Return tile at coords

        :param int x: X coords
        :param int y: Y coords
        :return room.Room: Corresponding room
        """
        if self.inBounds(x, y):
            return self._grid[y][x]

    def inBounds(self, x: int, y: int) -> bool:
        """
        True if coords are in

        :param int x: X coords to check
        :param int y: Y coords to check
        :return bool: Validity state
        """
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]

    def isValidRoom(self, x:int, y:int) -> bool:
        """
        Return True if a room is valid spot (is in bounds && player can enter)

        :param int x: X coords
        :param int y: Y coords
        :return bool: True if room is a valid room
        """
        if self.inBounds(x, y):
            r = self.getRoom(x, y)
            if r is not None:
                return r.validRoom

    def isAValidRoom(self, inst) -> bool:
        """
        Return True if a room is valid spot (is in bounds && player can enter)

        :param inst: Room instance to check for
        :return bool: True if room is a valid room
        """
        if inst is None: return False
        if not self.inBounds(*inst.pos): return False
        return inst.validRoom

    def patchWallsVoid(self) -> None:
        """
        Patch all walls
        > Close all walls with void behind
        """
        def _exec(r: room.Room, **_kwargs) -> None:
            if self.isAValidRoom(r):
                r.defineWalls(
                    **{k: True for k, v in self.neighborRoom(r.pos_x, r.pos_y).items() if not self.isAValidRoom(v)}
                )
        self.forEachRoom(_exec)

        """for dy in self._grid:
            for r in dy:
                if r is not None and r.validRoom:
                    r.defineWalls(
                        **{k: True for k, v in self.neighborRoom(r.pos_x, r.pos_y).items() if (True if v is None else not v.validRoom)}
                    )"""

    def patchWallsTransitons(self, prefer_mode:str="random", **kwargs) -> None:
        """
        Patch all walls
        > Chose between closing and openning a wall depending on the one on next room

        :param str prefer_mode: Replacement mode ['random','close','open']
        """
        _wall_order = {"t": "b", "l": "r", "r": "l", "b": "t"}
        def _close(r: room.Room, **_kwargs) -> None:
            if self.isAValidRoom(r):
                for side, room in self.neighborRoom(r.pos_x, r.pos_y).items():
                    if self.isAValidRoom(room):
                        if room.walls[_wall_order[side]]: # There is a wall on neighbor room
                            r.defineWalls(**{side: True})
        def _open(r: room.Room, **_kwargs) -> None:
            if self.isAValidRoom(r):
                for side, room in self.neighborRoom(r.pos_x, r.pos_y).items():
                    if self.isAValidRoom(room):
                        if not room.walls[_wall_order[side]]: # There is a wall on neighbor room
                            r.defineWalls(**{side: False})
        def _random(r: room.Room, **kwargs) -> None:
            p = kwargs.get("distribution", kwargs.get("distrib", 0.5))
            if self.isAValidRoom(r):
                for side, room in self.neighborRoom(r.pos_x, r.pos_y).items():
                    if self.isAValidRoom(room):
                        if room.walls[_wall_order[side]] != r.walls[side]:
                            c = dep.rnd.randint(0, 100) <= p * 100
                            room.defineWalls(**{_wall_order[side]: c})
                            r.defineWalls(**{side: c})

        self.forEachRoom(
            {
                "close": _close,
                "open": _open,
                "random": _random
            }.get(prefer_mode, lambda r, **kwargs: 0),
            **kwargs
        )

    @property
    def size(self) -> dep.Tuple[int, int]:
        """
        Get grid size

        :return dep.Tuple[int, int]: Grid size
        """
        return len(self._grid[0]), len(self._grid)

    @property
    def player(self):
        """
        Give players on the map

        :return player.Player: Player
        """
        return self._players

    def neighborRoom(self, x: int, y: int):
        """
        Return rooms arround coords

        :param int x: X coords
        :param int y: Y coords
        :return dep.Dict[str, room.Room]: Rooms detected
        """
        return {
            "l": self.getRoom(x-1, y),
            "r": self.getRoom(x+1, y),
            "t": self.getRoom(x, y-1),
            "b": self.getRoom(x, y+1)
        }

    def createMap(self, xray:bool=False) -> screen.PixelImage:
        minimap = screen.PixelImage((self.size[0]*3, self.size[1]*3))
        void_room = room.VoidRoom().bakeMinimapRoom(xray=xray)
        for dx in range(minimap.size[0]):
            for dy in range(minimap.size[1]):
                r = self.getRoom(dx, dy)
                minimap.paste(void_room if r is None else r.bakeMinimapRoom(xray=xray), dx * 3, dy * 3)
        return minimap

    def forEachRoom(self, funct: dep.Callable, ignoreSpawn: bool=False, **kwargs) -> dep.List[dep.List]:
        """
        Execute a function over all rooms

        :param funct: Function to execute
        :param bool ignoreSpawn: Ignore spawn room if True
        :return dep.List[dep.List]:
        """
        return [[funct(self.getRoom(dx, dy), **kwargs) for dx in range(self.size[0]) if (dx!=0 and dy!=0 if ignoreSpawn else True)] for dy in range(self.size[1])]

    def putRoom(self, x: int, y: int, obj) -> None:
        """
        Push new Room object into grid

        :param int x: X coords
        :param int y: Y coords
        :param room.Room obj: Object to push
        """
        if self.inBounds(x, y):
            self._grid[y][x] = obj

if __name__ == '__main__':
    @dep.Debug.add
    def generateStep(**kwargs):
        """Generate map step by step

        :arguments:
        - map_size(tuple[int, int])=`(10, 10)`: Define map size
        - pause(bool)=`True`: Pause between each operations
        - xray(bool)=`True`: Print map with xray
        - wall_mode(str)=`'random'`: Wall radomizing mode ['random', 'close', 'open']
        """
        @dep.Debug.silent
        def step(com: str):
            print(com)
            carte.createMap(kwargs.get("xray")).printScreen()
            input("Press enter to continue creation... ")

        carte = Map(kwargs.get("map_size"))
        step("Map object creation")
        carte.setPlayer(player.Player())
        step("Player added to map")

        def replaceRooms(r: room.Room, **kwargs):
            if not dep.rnd.randint(0, 7):
                r.replaceWith(kwargs["type"])
        carte.forEachRoom(replaceRooms, type=room.VoidRoom)
        carte.forEachRoom(replaceRooms, type=room.DungeonRoom)
        carte.forEachRoom(replaceRooms, type=room.LootRoom)
        step("Randomly generating rooms of different types")

        def randomizeWalls(r: room.Room, **_kwargs):
            if carte.isAValidRoom(r):
                r.defineWalls(**{dep.rnd.choice("lrbt"): True})
        carte.forEachRoom(randomizeWalls)
        step("Randomizing walls state")

        carte.patchWallsVoid()
        step("Patching walls against void")

        carte.patchWallsTransitons("random")
        step("Patching walls against missed transissions")
        return carte

    dep.Debug()
    exit(0)