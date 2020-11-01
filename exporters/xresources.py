NAME = "X11 Resources"
FORMAT = ".Xresources"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
*background:     {colors[0]}
*foreground:     {colors[7]}
*highlightColor: {colors[8]}
*cursorColor:    {colors[accent]}
"""
    for num, c in enumerate(colors):
        data += f"\n*color{num}:" + ' ' * (9 if num < 10 else 8) + f'{c}'

    return bytes(data, encoding="UTF-8")
