NAME = "Alacritty"
FORMAT = "alacritty.yml"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
scheme:
  {name}: &{name}
    primary:
      background: '{colors[0]}'
      foreground: '{colors[7]}'

    cursor:
      text:   '{colors[0]}'
      cursor: '{colors[accent]}'

    normal:
      black:   '{colors[0]}'
      red:     '{colors[1]}'
      green:   '{colors[2]}'
      yellow:  '{colors[3]}'
      blue:    '{colors[4]}'
      magenta: '{colors[5]}'
      cyan:    '{colors[6]}'
      white:   '{colors[7]}'

    bright:
      black:   '{colors[8]}'
      red:     '{colors[9]}'
      green:   '{colors[10]}'
      yellow:  '{colors[11]}'
      blue:    '{colors[12]}'
      magenta: '{colors[13]}'
      cyan:    '{colors[14]}'
      white:   '{colors[15]}'

colors: *{name}"""

    return bytes(data, encoding="UTF-8")
