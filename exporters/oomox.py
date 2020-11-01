NAME = "Oomox"
FORMAT = "{name}"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX()[1:] for c in colors]
    data = f"""\
NAME={name}
THEME_STYLE=oomox
GTK3_GENERATE_DARK=False
ROUNDNESS=0

BG={colors[0]}
FG={colors[7]}
ACCENT_BG={colors[accent]}

MENU_BG={colors[8]}
MENU_FG={colors[7]}

SEL_BG={colors[accent]}
SEL_FG={colors[0]}

BTN_BG={colors[8]}
BTN_FG={colors[7]}

TXT_BG={colors[8]}
TXT_FG={colors[7]}

ICONS_STYLE=numix_icons
ICONS_LIGHT_FOLDER={colors[15]}
ICONS_MEDIUM={colors[accent]}
ICONS_DARK={colors[0]}

TERMINAL_THEME_MODE=manual

TERMINAL_BACKGROUND={colors[0]}
TERMINAL_FOREGROUND={colors[7]}
TERMINAL_COLOR0={colors[0]}
TERMINAL_COLOR1={colors[1]}
TERMINAL_COLOR10={colors[10]}
TERMINAL_COLOR11={colors[11]}
TERMINAL_COLOR12={colors[12]}
TERMINAL_COLOR13={colors[13]}
TERMINAL_COLOR14={colors[14]}
TERMINAL_COLOR15={colors[15]}
TERMINAL_COLOR2={colors[2]}
TERMINAL_COLOR3={colors[3]}
TERMINAL_COLOR4={colors[4]}
TERMINAL_COLOR5={colors[5]}
TERMINAL_COLOR6={colors[6]}
TERMINAL_COLOR7={colors[7]}
TERMINAL_COLOR8={colors[8]}
TERMINAL_COLOR9={colors[9]}

SPOTIFY_PROTO_BG={colors[0]}
SPOTIFY_PROTO_FG={colors[7]}
SPOTIFY_PROTO_SEL={colors[accent]}
"""

    return bytes(data, encoding="UTF-8")
