NAME = "Rofi"
FORMAT = "config.rasi"


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    # I have list comprehension addiction
    colors = [f"rgba ({c.as_IRGB()[0]}, {c.as_IRGB()[1]}, {c.as_IRGB()[2]}, 100%)" for c in colors]
    data = f"""\
/* cannibalized from solarized_alternate.rasi */
* {{
    fg:      {colors[7]};
    bg:      {colors[0]};
    fgalt:   {colors[15]};
    bgalt:   {colors[8]};
    accent:  {colors[accent]};
    active:  {colors[4]};
    urgent:  {colors[1]};

    background-color: @bg;
    foreground-color: @fg;
    text-color:       @fg;
    border-color:     @accent;
}}""" + """
window {
    background-color: @accent;
    border:           2px;
}
mainbox {
}
message {
    border:       1px dash 0px 0px;
    padding:      1px;
}
listview {
    border:       2px 0px 0px;
    spacing:      2px;
    scrollbar:    true;
}
element {
    padding: 5px;
}
element.normal.normal {
    background-color: @bg;
    text-color:       @fg;
}
element.normal.urgent {
    background-color: @bg;
    text-color:       @urgent;
}
element.normal.active {
    background-color: @bg;
    text-color:       @active;
}
element.selected.normal {
    background-color: @bgalt;
    text-color:       @fg;
}
element.selected.urgent {
    background-color: @bgalt;
    text-color:       @urgent;
}
element.selected.active {
    background-color: @bgalt;
    text-color:       @active;
}
element.alternate.normal {
    background-color: @bg;
    text-color:       @fg;
}
element.alternate.urgent {
    background-color: @bg;
    text-color:       @urgent;
}
element.alternate.active {
    background-color: @bg;
    text-color:       @active;
}
scrollbar {
    handle-color: @accent;
    handle-width: 12px;
}
mode-switcher {
    border:       2px 0px 0px;
}
button.selected {
}
inputbar {
    spacing:    0px;
    padding:    5px;
}
case-indicator {
    spacing:    0;
    text-color: @urgent;
}
entry {
    spacing:    0;
}
prompt {
    spacing:    0;
}
textbox-prompt-colon {
    expand:     false;
    str:        ":";
    margin:     0px 5px 0px 0px;
}
inputbar {
    children:   [ prompt,textbox-prompt-colon,entry,case-indicator ];
}
"""

    return bytes(data, encoding='UTF-8')
