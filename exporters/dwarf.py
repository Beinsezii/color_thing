NAME = "Dwarf Fortress"
FORMAT = "colors.txt"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_IRGB() for c in colors]
    dwarfy_colors = [
        "BLACK",
        "LRED",
        "LGREEN",
        "YELLOW",
        "LBLUE",
        "LMAGENTA",
        "LCYAN",
        "WHITE",
        "DGRAY",
        "RED",
        "GREEN",
        "BROWN",
        "BLUE",
        "MAGENTA",
        "CYAN",
        "LGRAY",
    ]
    # no seriously, I need anti-string comprehension therapy
    data = "\n".join(["\n".join([f"[{col}_{c}:{colors[num][i]}]" for i, c in enumerate(["R", "G", "B"])]) for num, col in enumerate(dwarfy_colors)])

    return bytes(data, encoding="UTF-8")
