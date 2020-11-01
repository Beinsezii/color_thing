NAME = "i3 (Xresources)"
FORMAT = "config"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
set_from_resource $accent i3wm.cursorColor {colors[accent]}
set_from_resource $fg i3wm.foreground {colors[7]}
set_from_resource $bg i3wm.background {colors[0]}
set_from_resource $bgalt i3wm.highlightColor {colors[8]}

# class                 border  background text indicator child_border
client.focused          $accent $accent    $bg  $fg       $accent
client.focused_inactive $bgalt  $bgalt     $fg  $fg       $bgalt
client.unfocused        $bg     $bg        $fg  $bgalt    $bg
client.urgent           $fg     $fg        $bg  $accent   $fg
client.placeholder      $bgalt  $bgalt     $fg  $bg       $bgalt
client.background               $bg

bar {{
    colors{{
        background $bg
        statusline $fg
        separator $accent
        inactive_workspace $bg $bg $fg
        focused_workspace $accent $accent $bg
        urgent_workspace $accent $bg $fg
        }}
}}
"""
    return bytes(data, encoding="UTF-8")
