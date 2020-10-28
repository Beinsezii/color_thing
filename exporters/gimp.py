NAME = "GIMP Palette"
FORMAT = "{name}.gpl"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    data = f"""\
GIMP Palette
Name: {name}
Columns: 8
#"""
    for num, c in enumerate(colors):
        r, g, b = c.as_IRGB()
        data += "\n{:>3} {:>3} {:>3} color{}".format(r, g, b, num)
    return bytes(data, encoding="UTF-8")
