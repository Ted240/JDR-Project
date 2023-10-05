"""
Creator: Teddy Barthelemy
29/10/2022 23:17

main.sub
Gui manager
"""

import data.dependancies as dep
import data.screen as screen


class Command:
    __slots__ = ("_path", "_funct", "condition", "_redirections", "_manager", "_auto")

    def __init__(
            self,
            path: str,
            funct: dep.Callable,
            condition: dep.Callable = None,
            redirections: dep.Callable = None,
            auto: bool=True,
            manager=None
    ):
        """
        Command Constructor

        :param str path: Command path
        :param dep.Callable[dep.List, None] funct: Function to call if condition is satisfied to execute command
        :param dep.Callable[dep.List, bool] condition: Condition to execute to test command validity
        :param dep.Callable[Command] redirections: Authorized redirection commands
        :param bool auto: Autorize automatic redirection (aka auto completion)
        :param data.gui.CommandManager manager: Master commands manager
        """
        self._path = path
        self._funct = funct
        self.condition = condition if condition else lambda *args: True
        self._redirections = redirections if redirections else lambda m, gd: self._manager.publics
        self._auto = auto
        self._manager = manager if manager else None

    def getManager(self): return self._manager

    def setManager(self, v): self._manager = v

    manager = property(fget=getManager, fset=setManager)

    isPrivate = property(fget=lambda self: self._path.startswith("#"))

    path: str = property(fget=lambda self: self._path)

    redirections: dep.List[str] = property(fget=lambda self: self._redirections)

    funct: dep.Callable = property(fget=lambda self: self._funct)

    def test(self, *args) -> bool:
        """
        Test command validity

        :param args: Argument passed
        :return bool: Command validity state
        """
        return self.condition(*args) and self._manager

    def exec(self, *args, gd) -> None:
        """
        Try executing command

        :param args: Argument passed
        :param gd: Game data passing
        """
        if self.test(*args):
            self._manager.status = self._path
            if self._auto and not self.isPrivate:
                self._manager.last = [self._path, args]
            self._funct(*args, gd=gd)


class CommandManager:
    def __init__(self, *args, **kwargs):
        """
        CommandManger Constructor

        :param data.gui.Command args: Command to add
        :param kwargs: Game data
        """
        self.commands = list(args)
        for com in self.commands:
            com.manager = self
        self.status = None
        self.last = ["main", ()]
        self._gamedata = dep.Return(**kwargs)
        self.__waitingLink: dep.Optional[Command] = None

    publics: dep.List[Command] = property(fget=lambda self: [_ for _ in self.commands if not _.isPrivate])

    @property
    def saved_data(self):
        return self._gamedata

    # def add(self, funct:dep.Callable, path:str, redirections:dep.Callable=None, condition:dep.Callable=None) -> None:
    #    """
    #    Add a command to store

    #    :param dep.Callable funct: Command function to add
    #    :param str path: Command path
    #    :param dep.Callable redirections: Redirection of command
    #    :param dep.Callable condition: Command condition
    #    """
    #    if self.__waitingLink is not None:
    #        self.commands.append(self.__waitingLink)

    #    self.__waitingLink = Command(
    #        path,
    #        funct,
    #        lambda *args: True,
    #        redirections
    #    )
    #    if condition:
    #        self.link(condition)
    #        self.__waitingLink = None

    # def link(self, funct:dep.Callable):
    #    if self.__waitingLink is not None:
    #        self.__waitingLink.condition = funct
    #        self.commands.append(self.__waitingLink)
    #    self.__waitingLink = None

    def add(self, command: Command):
        self.commands.append(command)
        if command.manager is None:
            command.manager = self

    def redirect(self, path, *args):
        if path in self:
            self[path].exec(*args, gd=self._gamedata)

    def ask(self, cout: str = ">>>", *args):
        while True:
            # _in = input(f"{cout} ")
            _in = input(f"{' '.join(self[self.status].redirections(self, self._gamedata))}\n{cout} ")
            com, v = dep.regex.findall(r"(\w+)\s?(.*)", _in)[0] if dep.regex.findall(r"(\w+)\s?(.*)", _in) else (".repeat", None)
            com: str
            v: str
            # print(f"{_in} | {com} | {v} | {self.status} | {self.last}")
            if com == ".repeat":
                com, v = self.last[0], " ".join(self.last[1])
            # print("0", ([_.path for _ in self.publics] if self.status is None else self[self.status].redirections(self, gd=self._gamedata)))
            if com not in ([_.path for _ in self.publics] if self.status is None else self[self.status].redirections(self, gd=self._gamedata)):
                continue
            # print("1")
            if com not in self:
                continue
            # print("2")
            if self[com].isPrivate:
                continue
            # print("3")
            if not self[com].test(*v.split(" ")):
                print(screen.color(self[com].funct.__doc__, screen.colors.FG.light_red))
                continue
            # print("4")
            break
        self.redirect(com, *v.split(" "))

    def __contains__(self, item: str) -> bool:
        return item in [_.path for _ in self.commands]

    def __getitem__(self, item: str) -> Command:
        if item in self:
            return {obj.path: obj for obj in self.commands}[item]
