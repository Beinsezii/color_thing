#!/usr/bin/python3

import color_transform as ct
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk
from bszgw import Entry, Grid, GridChild as GC, App


LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."


class Color():
    def __init__(self, r: float = 1.0, g: float = 1.0, b: float = 1.0):
        self.R = r
        self.G = g
        self.B = b

    def as_SRGB(self):
        return (self.R, self.G, self.B)

    def as_HEX(self):
        return ct.IRGBtoHEX(*ct.SRGBtoIRGB(*self.as_SRGB()))


def override_color(widget: Gtk.Widget, fg: Color = None, bg: Color = None):
    """Widget needs provider prop"""
    if fg:
        fg = f"color: {fg.as_HEX()};"
    else:
        fg = ""
    if bg:
        bg = f"background-color: {bg.as_HEX()};"
    else:
        bg = ""
    css = f"""
.override {{ {fg} {bg} }}
textview text {{ {fg} {bg} }}
"""
    widget.provider.load_from_data(bytes(css, encoding="UTF-8"))
    widget.get_style_context().add_provider(widget.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
    widget.get_style_context().add_class("override")


def main():
    main_box = Entry(label="Foreground/Background", value=LOREM_IPSUM, min_height=300)
    main_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    main_box.entry.props.editable = False
    main_box.entry.provider = Gtk.CssProvider()

    term_color_labels = [
        Gtk.Label(label="Black"),
        Gtk.Label(label="Red"),
        Gtk.Label(label="Green"),
        Gtk.Label(label="Yellow"),
        Gtk.Label(label="Blue"),
        Gtk.Label(label="Magenta"),
        Gtk.Label(label="Cyan"),
        Gtk.Label(label="White"),
    ]

    term_colors_bright = [
        Gtk.Label(label=f"color{x}") for x in range(len(term_color_labels))
    ]

    term_colors_dim = [
        Gtk.Label(label=f"color{x + 8}") for x in range(len(term_color_labels))
    ]

    # add providers as prop for easy management. discount polymorphism
    for widget in [main_box] + term_colors_bright + term_colors_dim:
        widget.provider = Gtk.CssProvider()

    # colors test. Out of order, just a rainbow.
    for x in range(8):
        if x == 0:
            col = Color(0.0, 0.0, 0.0)
        elif x == 7:
            col = Color()
        else:
            col = Color(*ct.LCHtoSRGB(50, 30, x * 60 - 60))
        override_color(term_colors_bright[x], fg=col)

    grid = Grid()
    grid.attach_all(*term_color_labels, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(*term_colors_bright, row=1, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(*term_colors_dim, row=2, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(GC(main_box, width=8))

    app = App("Color Thing", grid)
    app.launch()


if __name__ == "__main__":
    main()
