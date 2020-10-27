NAME = "X11 Resources"
FORMAT = ".Xresources"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
*background:     {colors[0]}
*foreground:     {colors[7]}
*highlightColor: {colors[15]}
*cursorColor:    {colors[accent]}
"""
    for num, c in enumerate(colors):
        data += f"\n*color{num}:" + ' ' * (9 if num < 10 else 8) + f'{c}'

    # Rofi. May as well set it regardless, doesn't hurt anything.
    # rofi.colors-normal: bg, fg, bgalt, bgsel, fgsel
    # rofi.colors-window: background, border, separator
    data += f"""\n
rofi.color-normal:  {colors[0]} {colors[7]} {colors[8]} {colors[accent]}
rofi.colors-window: {colors[0]} {colors[7]} colors{7}
"""

    return bytes(data, encoding="UTF-8")
