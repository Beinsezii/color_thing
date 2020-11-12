NAME = "Dunst"
FORMAT = "dunstrc"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
[urgency_low]
    background = "{colors[0]}"
    foreground = "{colors[15]}"
    frame_color = "{colors[15]}"

[urgency_normal]
    background = "{colors[0]}"
    foreground = "{colors[7]}"
    frame_color = "{colors[7]}"

[urgency_critical]
    background = "{colors[0]}"
    foreground = "{colors[7]}"
    frame_color = "{colors[accent]}"
"""

    return bytes(data, "UTF-8")
