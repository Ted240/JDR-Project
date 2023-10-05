"""
Creator: Teddy Barthelemy
25/09/2022 - 03:15

main.sub
Common ressources for project
"""
import re
from typing import *
import random as rnd
import math
import re as regex
import json
import time
from os import system

numeric = Union[int, float]

# Do not delete, seems to patch text colors not showing correcly
system("cls")


def rnd_cos(x: numeric) -> numeric: return math.cos(math.radians(180 * x))


def rnd_sin(x: numeric) -> numeric: return math.sin(math.radians(180 * x))


class Return:  # When need to return a dictionnary but with javascript like access
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def wait(t):
    _t0 = time.time()
    while time.time() - _t0 < t: pass


class _Debug:
    """
    Debug program
    """

    class _Silent:
        def __init__(self, funct, owner):
            """
            _Silent Constructor

            :param Callable funct: Function to silent
            :param _Debug owner: Debug instance
            """
            self.funct = funct
            self.debug_class = owner

        def __call__(self, *args, **kwargs):
            print(self.debug_class.silentScripts)
            if not self.debug_class.silentScripts:
                return self.funct(*args, **kwargs)

    def __init__(self):
        self.funct = []
        self.safemode = True
        self._returns = []
        self.silentScripts = False

    @property
    def last(self) -> Any:
        if len(self._returns) > 0:
            return self._returns[len(self._returns) - 1]

    @property
    def returns(self) -> List[Any]:
        return self._returns

    def step(self, com: str, *funct, blocking: bool = True) -> None:
        """
        Make pause durion

        :param str com: Comment to show before prints, step description
        :param dep.Callable funct: Function to execute to print what need to be print
        :param bool blocking: Is step asking before continuing
        """
        if not self.silentScripts:
            print(com)
            for f in funct:
                f()
            if blocking:
                input("Press enter to continue")

    def silent(self, funct):
        return self.__class__._Silent(funct, self)

    def _getArgs(self, funct: Callable) -> Dict[str, Any]:
        _args_regex = r"- (\w+)(?:\(([a-zA-Z_][\w\[\], ]*)\)|)(?:=`(.*)`|)(?:\: (.*)|)"  # r"- (\w+)(?:\(([
        # a-zA-Z_]\w*)\)|)(?:=`(.*)`|)(?:\: (.*)|)"
        _args_sep = "\n\n:arguments:\n"
        return {
            _name: {
                "type": _type if _type else None,
                "default": _default if _default else None,
                "doc": _doc if _doc else "No documention",
                "value": _default if _default else None
            } for _name, _type, _default, _doc in re.findall(_args_regex, "\n".join(
                [_.lstrip(" ") for _ in funct.__doc__.split("\n")]).split(_args_sep)[1] if len(
                "\n".join([_.lstrip(" ") for _ in funct.__doc__.split("\n")]).split(_args_sep)) > 1 else '')
        }

    @staticmethod
    def _docArgs2Kwargs(**args):
        return {key: eval(data.get("value")) for key, data in args.items() if data.get("value")}

    def exec(self, name: str, silent: bool = True, **kwargs) -> Any:
        """
        Direcly execute a saved test function

        :param str name: Name of function to execute
        :param bool silent: Prevent prints and inputs during function execution (Function must support it to take
        effect)
        :param Dict[str, Any] kwargs: Kwargs to pass to function to execute, default are grabbed before and replace
        if one is given
        :return Any: Returns of function
        """
        _silent_state = self.silentScripts
        _funct = {f.__name__: f for f in self.funct}.get(name, None)
        if _funct is None: return
        _args = self._docArgs2Kwargs(**self._getArgs(_funct))
        _args.update(kwargs)
        if silent:
            _args.update({"_silent": True})
            self.silentScripts = silent
        _ret = _funct(**_args)
        self.silentScripts = _silent_state
        return _ret

    def add(self, funct: Callable) -> None:
        """
        Add function to debug program

        :param Callable funct: Function to add
        """
        if funct.__doc__ is None:
            funct.__doc__ = "No documentation\n\n:arguments:\n"
        self.funct.append(funct)

    def __call__(self) -> Any:
        """
        Start debug program

        :return Any: Function _returns
        """
        _args_sep = "\n\n:arguments:\n"
        functListFormat = "\033[0m[\033[96m{index:0>2}\033[0m] \033[92m{name:<15}\033[0m : \033[90m{doc}\033[0m"
        argsListFormat = "\033[0m[\033[96m{index:0>2}\033[0m] \033[92m{name:<15}\033[0m ( \033[92m{type:^15}\033[0m ) " \
                         "= \033[92m{value:>15}\033[0m [ \033[92m{default:<15}\033[0m ] : \033[90m{doc}\033[0m"

        print("\033[1m/////////////// [DEBUGING MENU] ///////////////\033[0m\n ..")
        print(functListFormat.format(
            index="ID",
            name="Function name",
            doc="Documentation"
        ) + "\n" + '-' * 100)
        for com in self.funct:
            print(functListFormat.format(
                index=self.funct.index(com),
                name=com.__name__[:15],
                doc="\n".join([_.lstrip(" ") for _ in com.__doc__.split("\n")]).split(_args_sep)[0].replace("\n", f"\n{' ' * 2} {' ' * 15} : ") if com.__doc__ is not None else 'No doc'
            ))
        _funct = None
        while True:
            _in = input("\033[0mCommand ID: \033[94m")
            print("\033[0m", end="")
            if _in.isdecimal() and 0 <= int(_in) < len(self.funct):
                _funct = self.funct[int(_in)]
                break
            elif isinstance(_in, str) and _in in [f.__name__ for f in self.funct]:
                _funct = {f.__name__: f for f in self.funct}[_in]
                break

        args = self._getArgs(_funct)
        while True and args != {}:
            print(f"\033[1m/////////////// [DEBUGING MENU] ///////////////\033[0m\n .. > {_funct.__name__}()")
            print(argsListFormat.format(
                index="ID",
                name="Name",
                type="Type",
                default="Default",
                doc="Documentation",
                value="Value"
            ))
            for name, data in args.items():
                print(argsListFormat.format(
                    index=list(args.keys()).index(name),
                    name=name,
                    type=data.get("type") if data.get("type") else "?",
                    default=data.get("default") if data.get("default") else "?",
                    doc=data.get("doc") if data.get("doc") else "?",
                    value=data.get("value") if data.get("value") else "?",
                ))
            _in = "/"
            _arg = ""
            while _in != "":
                _in = input("\033[0mArgs ID: \033[94m")
                print("\033[0m", end="")
                if _in.isdecimal() and 0 <= int(_in) < len(args.keys()):
                    _arg = list(args.keys())[int(_in)]
                    break
                elif isinstance(_in, str) and _in in args:
                    _arg = _in
                    break
            if _in == "":
                break
            else:
                args[_arg]["value"] = input(f"\033[0mValue: {_arg}=\033[94m")
                print("\033[0m", end="")
        kwargs = self._docArgs2Kwargs(**args)
        print("\033[0m >>>\t\033[1m{funct}(\n{args}\n\t)\033[0m".format(
            funct=_funct.__name__,
            args=',\n'.join([f"\t\t{k}={v}" for k, v in kwargs.items()])
        ))
        exit(-1) if input("Press enter to execute or write something to cancel:") else 0
        _ret = _funct(**kwargs)
        print("\033[0m <<<\t{ret}\033[0m".format(ret=_ret))
        self._returns.append(_ret)
        return _ret


Debug = _Debug()


def spaceScreen():
    print("\n" * 50)

def clearScreen():
    system("cls")
