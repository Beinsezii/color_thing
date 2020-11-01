NAME = "i3"
FORMAT = "config"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    colors = [c.as_HEX() for c in colors]
    data = f"""\
set $accent {colors[accent]}
set $fg     {colors[7]}
set $bg     {colors[0]}
set $fgalt  {colors[15]}
set $bgalt  {colors[8]}

# class                 border  background text indicator child_border
client.focused          $accent $accent    $bg  $fg       $accent
client.focused_inactive $fgalt  $fgalt     $bg  $fg       $fgalt
client.unfocused        $bg     $bg        $fgalt $fgalt  $bg
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
