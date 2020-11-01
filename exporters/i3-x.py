NAME = "i3 (Xresources)"
FORMAT = "config"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
set_from_resource $cursor i3wm.cursorColor {colors[accent]}
set_from_resource $fg i3wm.foreground {colors[7]}
set_from_resource $bg i3wm.background {colors[0]}
set_from_resource $hl i3wm.highlightColor {colors[8]}

# class                 border  background text indicator child_border
client.focused          $cursor $cursor    $bg  $bg       $cursor
client.focused_inactive $hl     $hl        $fg  $fg       $hl
client.unfocused        $bg     $bg        $fg  $fg       $bg
client.urgent           $fg     $fg        $bg  $bg       $fg
client.placeholder      $hl     $hl        $fg  $fg       $hl
client.background               $bg

bar {{
    colors{{
        background $bg
        statusline $fg
        separator $cursor
        inactive_workspace $bg $bg $fg
        focused_workspace $cursor $cursor $bg
        urgent_workspace $cursor $bg $fg
        }}
}}
"""
    return bytes(data, encoding="UTF-8")
