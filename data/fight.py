"""
Creator: Teddy Barthelemy
28/10/2022 - 04:03

main.sub
Gameplay configuration classes
"""
import data.dependancies as dep
import data.screen as screen
import threading as thrd
import time


class AccuracyBar:
    class Target:
        __slots__ = ("_x", "_funct", "_size", "_name", "_color")

        def __init__(self, size: int, x: int, name: dep.Union[str, dep.Callable] = "", funct: dep.Callable = None,
                     color: dep.Callable = None):
            """
            Target on an accuracy bar

            :param int size: Target size
            :param int x: X coords
            :param dep.Union[str, dep.Callable] funct: Accuracy function (return accuracy result) { funct(self,
            cursor_x) }
            :param dep.Callable x: Color function
            """
            self._size = size
            self._x = x
            self._name = (lambda self: name) if isinstance(name, str) else name
            self._funct = (lambda self, x: 1.0 if self.on(x) else 0.0) if funct is None else funct
            self._color = color if color else lambda self: ""

        pos_x = property(fget=lambda self: self._x)
        size = property(fget=lambda self: self._size)
        name = property(fget=lambda self: self._name(self))

        def on(self, x: int) -> float:
            return abs(self.pos_x - x) <= self.size

        def verify(self, x: dep.numeric) -> float:
            """
            Verify accuracy of a cursor

            :param int x: X cursor coords
            :return float: Accuracy result
            """
            return max(0.0, self._funct(self, x))

        def display(self, width: int, hitbox: bool = True) -> str:
            if hitbox:
                return "".join([" █"[dep.math.ceil(min(self.verify(x), 1.0) * 1)] * 2 for x in range(width)])
            else:
                return "".join(
                    [(" ▁▂▃▄▅▆▇█"[dep.math.floor(self.verify(x) * 8)] if self.verify(x) <= 1.0 else "↑") * 2 for x in
                     range(width)])

        def displayAsPixel(self, width: int, hitbox: bool = True) -> screen.PixelImage.TextPixel:
            return screen.PixelImage.TextPixel(self.display(width, hitbox), color=self._color(self),
                                               endcolor="" if self._color(self) == "" else screen.colors.reset)

    class CreatureTarget(Target):
        def __init__(self, entity, x: int, name: dep.Union[str, dep.Callable] = lambda self: self._entity.name,
                     funct: dep.Callable = None, color: dep.Callable = None):
            """
            CreatureTarget Constructor

            :param data.enemy.Enemy entity: Creature instance linked to target
            :param int x: X coords of target
            :param dep.Union[str, dep.Callable] name: Target name
            :param dep.Callable funct: Verify function
            :param dep.Callable color: Target color function
            """
            self._entity = entity
            super().__init__(
                self._entity.fight_data.size.define(self._entity),
                x,
                name=name,
                funct=funct if funct else self._entity.fight_data.funct,
                color=color
            )

        entity = property(fget=lambda self: self._entity)

    __slots__ = ("speed", "timeout", "_targets", "_screen", "layers", "_running")

    _name_w = 16  # Width for targets names area
    _cursor_w = 100  # Width for cursor area

    def __init__(self, speed: float, layers: int = 1, timeout: float = -1):
        """
        AccuracyBar Constructor

        :param float speed: In pixels per second (pxls/s), define cursor speed
        :param float layers: In pixels per second (pxls/s), define cursor speed
        :param float timeout: Time before auto lose, if -1 time is infinite
        """
        self.speed = speed
        self.timeout = timeout
        self.layers = layers
        self._targets: dep.List[AccuracyBar.Target] = []
        self._screen: screen.PixelImage
        self._running = False
        self._generateScreen()

    def defineTargets(self, items):
        self._targets = items[:self.layers]
        self._generateScreen()

    screen = property(fget=lambda self: self._screen)
    targets = property(fget=lambda self: self._targets, fset=defineTargets)

    def _generateScreen(self, time: float = None, hits_r: int = 1, hits_n: int = 1) -> None:
        """
        Generate screen depending on number of layers

        :param float time: Timeout
        """
        if time is None:
            time = self.timeout
        self._screen = screen.PixelImage((self._name_w + self._cursor_w + 3, self.layers + 2))
        gui = screen.PixelImage.TextPixel(
            f"""╔═{'══' * self._name_w}═╦{'[ Time : {time: <12} | Hits : {hits_r: >2}/{hits_n: <2}]'.format(
                time=('{h:0>2.0f}:{m:0>2.0f}:{s:0>2.0f}.{f:0<3.0f}' if time != -1 else 'Infinite').format(
                    h=time // 3600,
                    m=time % 3600 // 60,
                    s=time % 3600 % 60 // 1,
                    f=time % 3600 % 60 % 1 * 1000
                ),
                hits_r=hits_r,
                hits_n=hits_n
            )}═{'══' * (self._cursor_w - 19)}╗ \n""" +
            f"║ {'  ' * self._name_w} ║{'  ' * self._cursor_w}║ \n" * self.layers +
            f"╚═{'══' * self._name_w}═╩{'══' * self._cursor_w}╝ \n"
        )
        self._screen.putGrid(0, 0, gui)
        for dy, obj in enumerate(self._targets):
            dy: int
            obj: AccuracyBar.Target
            self._screen.putGrid(1, self.layers - dy, screen.PixelImage.TextPixel(obj.name[:self._name_w * 2]))
            self._screen.putGrid(2 + self._name_w, self.layers - dy, obj.displayAsPixel(self._cursor_w, hitbox=False))

    @staticmethod
    def _runInput(firstRun: bool = False):
        # Spam overflow prevent
        # Prevent previous validation to be counted as hit
        if firstRun:
            _start = time.perf_counter()
            while True:
                input()
                if time.perf_counter()-_start > 5e-2:
                    return
        else:
            input()

    def _runPrint(self, cursor_x: int = -1, time: float = -1, hits: dep.List[int] = None, hits_n: int = 1):
        if hits is None:
            hits = []
        self._generateScreen(time, hits_n - len(hits), hits_n)

        for hit in hits:
            if 0 <= hit < self._cursor_w:
                for dy in range(self.layers):
                    pxl = self._screen.getGrid(2 + self._name_w + hit, 1 + dy, False)
                    if isinstance(pxl, screen.PixelImage.PatternPixel):
                        pxl.incolor = screen.colors.BG.green
                        pxl.endcolor = screen.colors.reset

        if cursor_x != -1 and 0 <= cursor_x < self._cursor_w:
            for dy in range(self.layers):
                pxl = self._screen.getGrid(2 + self._name_w + cursor_x, 1 + dy, False)
                if isinstance(pxl, screen.PixelImage.PatternPixel):
                    pxl.incolor = screen.colors.BG.white
                    pxl.endcolor = screen.colors.reset
        self._screen.printScreen()

    def run(self, hits_n: int = 1, pause: float = 1) -> dep.List[dep.List[float]]:
        """
        Start Accuracy bar action

        :param int hits_n: Hits count autorized
        :param float pause: Time before starting cursor mouvement, like an observation moment
        :return dep.List[dep.List[float]]: Accuracy results per targets per hits
        """
        step = dep.math.ceil(self.speed / 100)
        input_thread = thrd.Thread(target=self._runInput, args=(True,))
        move_right = True
        cursor_x = 0
        frames = 0
        hits = []

        dep.clearScreen()
        if pause > 0:
            self._runPrint(
                -1,
                self.timeout,
                [],
                hits_n
            )
            dep.wait(pause)
        input_thread.start()
        while len(hits) < hits_n and (True if self.timeout == -1 else (frames / self.speed < self.timeout)):
            frames += 1
            if not frames % step:
                self._runPrint(
                    cursor_x,
                    self.timeout - frames / self.speed,
                    hits,
                    hits_n
                )
            # print(self.timeout - frames/self.speed, frames/self.speed, frames, self.speed, self.timeout)
            cursor_x += 1 if move_right else -1
            if cursor_x >= self._cursor_w - 1:
                move_right = False
            if cursor_x <= 0:
                move_right = True
            dep.wait(1 / self.speed)
            if not input_thread.is_alive():
                hits.append(cursor_x)
                if len(hits) < hits_n:
                    input_thread = thrd.Thread(target=self._runInput)
                    input_thread.start()
        self._runPrint(
            -1,
            self.timeout - frames / self.speed,
            hits,
            hits_n
        )
        if frames / self.speed >= self.timeout:
            print(screen.color("[TIMEOUT] Press enter to coninue", screen.colors.FG.light_red + screen.colors.bold,
                               screen.colors.reset))
            while input_thread.is_alive():
                pass
        return [[i.verify(hit) for i in self._targets] for hit in hits] + [[0] * self.layers for _ in range(hits_n - len(hits))]


if __name__ == '__main__':
    @dep.Debug.add
    def simple(**kwargs):
        """Simple bar, void targets, timer ?, hits ?

        :arguments:
        - speed(int)=`150`: Cursor speed
        - layers(int)=`5`: Screen layer count
        - targets(int)=`3`: Target count
        - time(float)=`10`: Timeout (-1 = inf)
        - hits(int)=`3`: Hits count
        """
        bar = AccuracyBar(kwargs.get("speed"), kwargs.get("layers"), kwargs.get("time"))
        bar.targets = [AccuracyBar.Target(
            dep.rnd.randint(1, 10),
            dep.rnd.randint(1, 100),
            "".join([dep.rnd.choice("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in
                     range(dep.rnd.randint(5, 15))]),
            lambda self, x: (self.size - abs(self.pos_x - x)) / self.size
        ) for _ in range(kwargs.get("targets"))]
        return bar.run(kwargs.get("hits"), 3)


    dep.Debug()
