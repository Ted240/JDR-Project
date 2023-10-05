"""
Creator: Teddy Barthelemy
25/09/2022 - 15:20

other
Image to code conversion tool
"""
from PIL import Image, ImageGrab
import pyperclip

"""if __name__ == '__main__':
    def tuple2hex(r, g, b):
        return (0xff0000 if r > 128 else 0) + (0x00ff00 if g > 128 else 0) + (0x0000ff if b > 128 else 0), 2 if 192 in [r, g, b] else (1 if 64 in [r, g, b] else 0)

    colors = {
        0xc1c1c1: "$.", # void
        0x000000: "$d", # black
        0xffffff: "$w", # white
        0xff0000: "$r", # red
        0x00ff00: "$g", # green
        0x0000ff: "$b", # blue
        0xffff00: "$y", # yellow
        0xff00ff: "$p", # purple
        0x00ffff: "$c"  # cyan
    } 
    chars = "%+-"
    nl = "$.\\n"

    img: Image = ImageGrab.grabclipboard()
    txt = ""

    if img is not None:
        for y in range(img.height):
            lastcolor = -0x1
            for pos_x in range(img.width):
                p = img.getpixel((pos_x, y))
                c, v = tuple2hex(*p)
                if p == (128, 128, 128): c, v = 0xc1c1c1, 0
                if c != lastcolor:
                    if lastcolor == 0xffffff and c != :
                        txt += "$."
                    if c == 0xffffff and lastcolor != 0xffffff:
                        txt += "$."
                    txt += colors[c]
                    lastcolor = c
                txt += chars[v]
            txt += nl
        print(txt)
        pyperclip.copy(txt)
"""

"""if __name__ == '__main__':
    colors = {
        (128,   128,    128 ):  ":%",     # clear/void

        (0,     0,      0   ):  "$d:%",     # black
        (255,   255,    255 ):  "$w:%",     # white
        (255,   0,      0   ):  "$r:%",     # red
        (0,     255,    0   ):  "$g:%",     # green
        (0,     0,      255 ):  "$b:%",     # blue
        (255,   255,    0   ):  "$y:%",     # yellow
        (255,   0,      255 ):  "$p:%",     # purple
        (0,     255,    255 ):  "$c:%",     # cyan

        (192,   192,    192 ):  "$w:-",     # dark white
        (192,   0,      0   ):  "$r:-",     # dark red
        (0,     192,    0   ):  "$g:-",     # dark green
        (0,     0,      192 ):  "$b:-",     # dark blue
        (192,   192,    0   ):  "$y:-",     # dark yellow
        (192,   0,      192 ):  "$p:-",     # dark purple
        (0,     192,    192 ):  "$c:-",     # dark cyan

        (64,    64,     64  ):  "$d:+",     # light black
        (255,   64,     64  ):  "$r:+",     # light red
        (64,    255,    64  ):  "$g:+",     # light green
        (64,    64,     255 ):  "$b:+",     # light blue
        (255,   255,    64  ):  "$y:+",     # light yellow
        (255,   64,     255 ):  "$p:+",     # light purple
        (64,    255,    255 ):  "$c:+",     # light cyan
    }
    nl = "$.\\n"
    rst = "$."

    img: Image = ImageGrab.grabclipboard()
    txt = ""

    if img is not None:
        for y in range(img.height):
            lastcolor = (-1, -1, -1)
            for pos_x in range(img.width):
                c = img.getpixel((pos_x, y))
                if not c in colors.keys(): raise KeyError(f"Invalid color: {c} at ({pos_x};{y})")
                if lastcolor != c:
                    txt += rst
                    txt += colors[c].split(":")[0]
                txt += colors[c].split(":")[1]
                lastcolor = c
            txt += nl
        print(txt)
        pyperclip.copy(txt)
"""

if __name__ == '__main__':
    colors = {
        (128,   128,    128 ):  "#",     # clear/void

        (0,     0,      0   ):  "d0",     # black
        (255,   255,    255 ):  "w0",     # white
        (255,   0,      0   ):  "r0",     # red
        (0,     255,    0   ):  "g0",     # green
        (0,     0,      255 ):  "b0",     # blue
        (255,   255,    0   ):  "y0",     # yellow
        (255,   0,      255 ):  "p0",     # purple
        (0,     255,    255 ):  "c0",     # cyan

        (192,   192,    192 ):  "w-",     # dark white
        (192,   0,      0   ):  "r-",     # dark red
        (0,     192,    0   ):  "g-",     # dark green
        (0,     0,      192 ):  "b-",     # dark blue
        (192,   192,    0   ):  "y-",     # dark yellow
        (192,   0,      192 ):  "p-",     # dark purple
        (0,     192,    192 ):  "c-",     # dark cyan

        (64,    64,     64  ):  "d+",     # light black
        (255,   64,     64  ):  "r+",     # light red
        (64,    255,    64  ):  "g+",     # light green
        (64,    64,     255 ):  "b+",     # light blue
        (255,   255,    64  ):  "y+",     # light yellow
        (255,   64,     255 ):  "p+",     # light purple
        (64,    255,    255 ):  "c+",     # light cyan
    }
    nl = "_"

    img: Image = ImageGrab.grabclipboard()
    txt = ""

    if img is not None:
        for y in range(img.height):
            for x in range(img.width):
                c = img.getpixel((x, y))
                if not c in colors.keys(): raise KeyError(f"Invalid color: {c} at ({x};{y})")
                else: txt += colors[c]
            txt += nl
        print(txt)
        pyperclip.copy(txt)
