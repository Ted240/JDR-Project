# coding=utf8
"""
Creator: Teddy Barthelemy
25/09/2022 - 08:11

main.sub
Screen, Textures managment script
"""
from data import dependancies as dep

class CodeImage:
    """
    Texture stored as an encoded string
    Need to be passed in a decoder to be printed
    """
    class Decoder:
        class Colors:
            class Foreground:
                black = "\033[30m"
                red = "\033[31m"
                green = "\033[32m"
                yellow = "\033[33m"
                blue = "\033[34m"
                magenta = "\033[35m"
                cyan = "\033[36m"
                white = "\033[37m"
                reset = "\033[39m"

                light_black = "\033[90m"
                light_red = "\033[91m"
                light_green = "\033[92m"
                light_yellow = "\033[93m"
                light_blue = "\033[94m"
                light_magenta = "\033[95m"
                light_cyan = "\033[96m"
                light_white = "\033[97m"
                light_reset = "\033[99m"

            class Background:
                black = "\033[40m"
                red = "\033[41m"
                green = "\033[42m"
                yellow = "\033[43m"
                blue = "\033[44m"
                magenta = "\033[45m"
                cyan = "\033[46m"
                white = "\033[47m"
                reset = "\033[49m"

                light_black = "\033[100m"
                light_red = "\033[101m"
                light_green = "\033[102m"
                light_yellow = "\033[103m"
                light_blue = "\033[104m"
                light_magenta = "\033[105m"
                light_cyan = "\033[106m"
                light_white = "\033[107m"
                light_reset = "\033[109m"

            bold = "\033[1m"
            normal = "\033[2m"
            reset = "\033[0m"

            FG = Foreground
            BG = Background

        @classmethod
        def getDefaultDecoder(cls):
            """
            Return default decoder to use

            :return dep.Callable: Default decoder
            """
            return cls.colorDLo

        @staticmethod
        def depredicated(code: str):
            """
            /!\ Don'time use, depredicated, not working with actual code
            """
            _colors = [
                ["$w-", "\033[47m  $w"],  # except: dark white

                ["$r", "\033[41m"],  # red
                ["$g", "\033[42m"],  # green
                ["$y", "\033[43m"],  # yellow
                ["$b", "\033[44m"],  # blue
                ["$p", "\033[45m"],  # purple
                ["$c", "\033[46m"],  # cyan
                ["$w", "\033[07m"],  # white
                ["$d", "\033[40m"],  # black

                ["$.", "\033[49m\033[27m\033[39m"],  # reset

                ["%", "  "],  # normal color
                ["-", "\033[30m░░"],  # dark color
                ["+", "\033[39m░░"],  # light color
            ]

            for x, y in _colors:
                while x in code:
                    code = code.replace(x, y)
            return code

        @staticmethod
        def colorDL(code: str, raw=False) -> str:
            """
            Color + Dark + Light
            => 8 + 7 + 7
            = 22 colors

            :param str code: Image encoded string to decode and convert
            :param bool raw: If true, doesn't push a reset color char at end of returned string, keep the color to next chars
            :return str: String to print in shell
            """
            _colors = {
                "w0": ["\033[07m", "  "],
                "w-": ["\033[47m", "  "],

                "d0": ["\033[40m", "  "],
                "d+": ["\033[40m\033[39m", "░░"],

                "r0": ["\033[41m", "  "],
                "g0": ["\033[42m", "  "],
                "b0": ["\033[44m", "  "],
                "y0": ["\033[43m", "  "],
                "c0": ["\033[46m", "  "],
                "p0": ["\033[45m", "  "],

                "r-": ["\033[41m\033[30m", "░░"],
                "g-": ["\033[42m\033[30m", "░░"],
                "b-": ["\033[44m\033[30m", "░░"],
                "y-": ["\033[43m\033[30m", "░░"],
                "c-": ["\033[46m\033[30m", "░░"],
                "p-": ["\033[45m\033[30m", "░░"],

                "r+": ["\033[41m\033[39m", "░░"],
                "g+": ["\033[42m\033[39m", "░░"],
                "b+": ["\033[44m\033[39m", "░░"],
                "y+": ["\033[43m\033[39m", "░░"],
                "c+": ["\033[46m\033[39m", "░░"],
                "p+": ["\033[45m\033[39m", "░░"],

                "#": ["\033[0m", "  "],

                "_": ["\033[0m", "\n"]
            }
            c = "?"
            _return = ""
            while len(code) > 0:
                modified = False
                for char in _colors.keys():
                    if code.startswith(char) and not modified:
                        # print(char, ascii(code), code.startswith(char), c == char)
                        if c != char:
                            c = char
                            _return += ("" if code == "_" else _colors['_'][0]) + _colors[char][0]
                        _return += _colors[char][1]
                        code = code[len(char):]
                        modified = True
                # print(_return, c)
                if not modified: raise ValueError("Image miss-compilation")
            return _return + ("" if raw else _colors["_"][0])

        @staticmethod
        def colorDLo(code: str, raw=False) -> str:
            """
            Color + Dark + Light
            => 8 + 7 + 7
            = 22 colors
            Optimized

            :param str code: Image encoded string to decode and convert
            :param bool raw: If true, doesn't push a reset color char at end of returned string, keep the color to next chars
            :return str: String to print in shell
            """
            _colors = {
                "w0": ["\033[107m", "  "],
                "w-": ["\033[7m", "  "],

                "d0": ["\033[40m", "  "],
                "d+": ["\033[100m", "  "],

                "r0": ["\033[41m", "  "],
                "g0": ["\033[42m", "  "],
                "b0": ["\033[44m", "  "],
                "y0": ["\033[43m", "  "],
                "c0": ["\033[46m", "  "],
                "p0": ["\033[45m", "  "],

                "r-": ["\033[41m\033[30m", "░░"],
                "g-": ["\033[42m\033[30m", "░░"],
                "b-": ["\033[44m\033[30m", "░░"],
                "y-": ["\033[43m\033[30m", "░░"],
                "c-": ["\033[46m\033[30m", "░░"],
                "p-": ["\033[45m\033[30m", "░░"],

                "r+": ["\033[101m", "  "],
                "g+": ["\033[102m", "  "],
                "b+": ["\033[104m", "  "],
                "y+": ["\033[103m", "  "],
                "c+": ["\033[106m", "  "],
                "p+": ["\033[105m", "  "],

                "#": ["\033[0m", "  "],

                "_": ["\033[0m", "\n"]
            }
            c = "?"
            _return = ""
            while len(code) > 0:
                modified = False
                for char in _colors.keys():
                    if code.startswith(char) and not modified:
                        # print(char, ascii(code), code.startswith(char), c == char)
                        if c != char:
                            c = char
                            _return += ("" if code == "_" else _colors['_'][0]) + _colors[char][0]
                        _return += _colors[char][1]
                        code = code[len(char):]
                        modified = True
                # print(_return, c)
                if not modified: raise ValueError("Image miss-compilation")
            return _return + ("" if raw else _colors["_"][0])

    def __init__(self, code: str, decoder=None):
        """
        CodeImage constructor

        :param str code: Encoded string to store
        :param dep.Callable decoder: Decoder to use to decode encoded string and output it in shell
        """
        self._decoder = decoder if decoder is not None else CodeImage.Decoder.getDefaultDecoder()
        self._code: str = code

    def string(self) -> str:
        """
        Return the decoded string ready to be pushed in bash

        :return str: String to push
        """
        return self._decoder(self._code)

    def raw(self) -> str:
        """
        Return the raw decoded string ready to be pushed in bash
        Raw version doesn't force a color reset at the of the string

        :return str: String to push
        """
        return self._decoder(self._code, raw=True)

    def decoderEndline(self) -> str:
        """
        Return the reset colors char used in the decoder

        :return str: Reset char used in the decoder
        """
        return self._decoder("")

    @property
    def code(self) -> str:
        """
        Return encoded string texture

        :return str: Encoded string texture
        """
        return self._code

    def toScreen(self):
        """
        Convert the actual encoded string texture to a pixelized version (aka Screen)

        :return PixelImage: Pixelized version of actual texture
        """
        return PixelImage.code2img(self)

    def __str__(self):
        return f"<{self.string()}>"


class PixelImage:
    """
    Texture stored as pixels
    """
    class ColorPixel:
        """
        PixelImage.component

        Pixel with a color
        """
        __slots__ = ("_char",)

        def __init__(self, char="#"):
            self._char = char

        def __repr__(self):
            return CodeImage(self._char, decoder=CodeImage.Decoder.getDefaultDecoder()).string()

        def copy(self): return self.__class__(self._char)

        @property
        def print(self): return CodeImage(self._char, decoder=CodeImage.Decoder.getDefaultDecoder()).string()

    class PatternPixel:
        """
        PixelImage.component

        Pixel with chars in it (2 max)
        Color can be specified
        """
        __slots__ = ("_char", "incolor", "endcolor")

        def __init__(self, char:str="", color:str="", endcolor:str=""):
            """
            PatternPixel constructor

            :param char: Chars to input (max 2)
            :param color: Color pushed before chars
            :param endcolor: Color pushed after chars
            """
            self._char = ""
            self.incolor = color
            self.endcolor = endcolor
            self.char = char

        def setChar(self, v): self._char = (v + "  ")[0:2]
        def getChar(self): return self._char
        char = property(fget=getChar, fset=setChar)

        def __repr__(self):
            return f"<{self._char}>"

        def copy(self): return self.__class__(self._char, self.incolor, self.endcolor)

        @property
        def print(self): return self.incolor + self._char + self.endcolor

    class TextPixel:
        """
        PixelImage.subcomponent

        Pixels with text
        Converted to PixelImage.PatternPixel after being pushed into screen
        """
        __slots__ = ("_text", "_indent", "_color", "_endcolor",)

        def __init__(self, text:str="", *, indent=False, color:str="", endcolor:str=""):
            """
            TextPixel Constructor

            :param text: Text to input
            :param indent: If all text is move 1 char away
            :param color: Color setted before text
            :param endcolor: Color setted after text
            """
            self._text = text
            self._indent = indent
            self._color = color
            self._endcolor = CodeImage.Decoder.getDefaultDecoder()("") if color != "" and endcolor == "" else endcolor

        def setText(self, v): self._text = v
        def getText(self): return self._text
        char = property(fget=getText, fset=setText)

        def __repr__(self):
            return f"<{ascii(self._text)}>"

        def copy(self): return self.__class__(self._text, indent=self._indent)

        def generate(self):
            """
            Create each PatternPixel with correct text inside

            :return: ~List of ~List of ~PixelImage.PatternPixel
            """
            def splitText(txt):
                # print(len(txt), f"'{txt}'")
                for i in range(0, len(txt), 2):
                    # print(i)
                    yield f"{txt[i]}{txt[i+1] if i < len(txt) - 1 else ' '}"

            lines = [f"{' ' if self._indent else ''}{txt}" for txt in self._text.split("\n")]
            return [[PixelImage.PatternPixel(stripped, self._color, self._endcolor) for stripped in splitText(l)] for l in lines]

    class BlankPixel:
        """
        PixelImage.component

        Pixel with no content (define the transparency for pasting)
        """
        def __init__(self):
            pass
        def __repr__(self):
            return "<Blank>"

        def copy(self): return self.__class__()

        @property
        def print(self): return PixelImage.PatternPixel().print

    @classmethod
    def code2img(cls, obj: CodeImage):
        """
        Convert an encoded string image to it's pixelized version

        :param CodeImage obj: Encoded string image to convert
        :return PixelImage: Converted version
        """
        _return = cls()
        _return.fromCodeImage(obj)
        return _return

    __slots__ = ("_size", "_grid")

    def __init__(self, size: dep.Tuple[int, int] = (1, 1), fill = None):
        """
        PixelImage constructor

        :param tuple[int, int] size: Image size
        :param fill: Pixel used to fill the screen
        """
        self._size = list(size)
        self._grid = []
        self._generateGrid(fill)
    
    size = property(fget=lambda self: self._size)

    def _generateGrid(self, filling = None):
        self._grid = [[(self.__class__.BlankPixel() if filling is None else filling) for _x in range(self._size[0])] for _y in range(self._size[1])]

    def fromCodeImage(self, coded_image: CodeImage):
        """
        Convert coded image (~CodeImage) to a pixel version (~PixelImage)

        :param CodeImage coded_image: String to convert
        :return PixelImage: Converted image
        """

        def getSize(data: str):
            return [
                sum([data.split("_")[0].count(_char) for _char in ["0", "+", "-", "#"]]),
                data.count("_")
            ]

        self._size = getSize(coded_image.code)
        self._generateGrid()
        _colors = ["w0", "w-", "d0", "d+", "r0", "g0", "b0", "y0", "c0", "p0", "r-", "g-", "b-", "y-", "c-", "p-", "r+", "g+", "b+", "y+", "c+", "p+"]
        _nl = "_"
        _blank = "#"
        _x, _y, _code = 0, 0, coded_image.code
        while len(_code) > 0:
            # print(len(_code), _code)
            if _code.startswith(_nl):
                _y += 1
                _x = 0
                _code = _code[len(_nl):]
                # print(f"{_x}:{_y} => {_nl}")
            elif _code.startswith(_blank):
                self.putGrid(_x, _y, self.__class__.BlankPixel())
                _x += 1
                _code = _code[len(_blank):]
                # print(f"{_x}:{_y} => {_blank}")
            else:
                if any([_code.startswith(_c) for _c in _colors]):
                    color = {_code.startswith(_c): _c for _c in _colors}[True]
                    self.putGrid(_x, _y, self.__class__.ColorPixel(color))
                    _code = _code[len(color):]
                    # print(f"{_x}:{_y} => {color}")
                _x += 1
        # print("EXIT")

    def printScreen(self, autoclear=True) -> None:
        """
        Print object in shell

        :param bool autoclear: Auto clearing screen
        """
        if autoclear: dep.spaceScreen()
        print("\n".join(["".join([__.print for __ in _]) for _ in self._grid]))


    def putGrid(self, x:int, y:int, obj) -> None:
        """
        Inject color/pattern/blank pixel into grid

        :param x: X coord
        :param y: Y coord
        :param obj: Object to inject
        """
        if isinstance(obj, (self.__class__.PatternPixel, self.__class__.ColorPixel, self.__class__.BlankPixel)) and 0 <= x < self._size[0] and 0 <= y < self._size[1]:
            if self.inBound(x, y):
                self._grid[y][x] = obj
        elif isinstance(obj, self.__class__.TextPixel):
            objs = obj.generate()
            for dy in range(len(objs)):
                for dx in range(len(objs[dy])):
                    self.putGrid(x + dx, y + dy, objs[dy][dx])
                    # print(dx, dy, objs[dy][dx])

    def fillGrid(self, x1: int, y1: int, x2: int, y2: int, obj, copy:bool=False) -> None:
        """
        Fill rect with a pixel

        :param int x1: 1st corner X coord
        :param int y1: 1st corner Y coord
        :param int x2: 2nd corner X coord
        :param int y2: 2nd corner Y coord
        :param obj: Pixel user to fill
        :param bool copy: Make copy of given object to avoid cloned pixels
        """
        for dy in range(y1, y2+1):
            for dx in range(x1, x2+1):
                self.putGrid(dx, dy, obj.copy() if copy else obj)

    def getGrid(self, x:int, y:int, copy:bool=True):
        """
        Retrieve pixel object at coords X;Y

        :param x: X coord
        :param y: Y coord
        :param copy: If True return a copy of pixel object else the orignal
        :return: Pixel object
        """
        return self._grid[y][x].copy() if copy else self._grid[y][x]
    
    def paste(self, screen, x:int=0, y:int=0) -> None:
        """
        Paste an image on this one

        :param screen: Image to paste on this one
        :param x: Paste origin X
        :param y: Paste origin Y
        """
        screen: PixelImage
        for _y in range(screen.size[1]):
            for _x in range(screen.size[0]):
                v = screen.getGrid(_x, _y)
                if not isinstance(v, self.__class__.BlankPixel):
                    self.putGrid(x+_x, y+_y, v)

    def inBound(self, x:int, y:int) -> bool:
        """
        Return True if coords are on screen and in bounds

        :param int x: X coords
        :param int y: Y coords
        :return bool: Validity state of coords
        """
        return 0 <= x < self.size[0] and 0 <= y < self.size[1]


def testModule() -> bool:
    """
    Test shell color compatibility

    :return bool: True if shell is compatible
    """
    return True if input("\033[41m  \033[42m  \033[44m  \033[49m\nDo you see red green and blue colors above ? > ").lower() in ["yes", "y", "o", "oui"] else testModule()

colors = CodeImage.Decoder.Colors
def color(txt:str, in_color:str, out_color:str=None):
    """
    Return colored text

    :param str txt: Text to color
    :param str in_color: Incomming color
    :param str out_color: Outcomming color
    :return str: Colored text
    """
    if out_color is None: out_color = CodeImage.Decoder.getDefaultDecoder()("")
    return f"{in_color}{txt}{out_color}"
