#!/usr/bin/python3

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk
from bszgw import Adjuster, Entry, Grid, GridChild as GC, App
from discount_babl import Color


LOREM_IPSUM_MINI = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."


class ColorAdjuster(Grid):
    def __init__(self, color: Color):
        super(ColorAdjuster, self).__init__()

        self.color = color
        L, C, H = self.color.as_LCH()
        self.L_adj = Adjuster.new('L', L, -100, 200, 5, 10, 1)
        self.C_adj = Adjuster.new('C', C, -100, 200, 5, 10, 1)
        self.H_adj = Adjuster.new('H', H, 0, 360, 5, 15, 1)
        self.adjusters = [self.L_adj, self.C_adj, self.H_adj]
        for w in self.adjusters:
            w.adjustment.connect("value-changed", self.__set)

        self.attach_all(
                self.L_adj,
                self.C_adj,
                self.H_adj,
                direction=Gtk.DirectionType.RIGHT,
                )

        self.__set(None)

    def __set(self, widget):
        self.color.set_LCH(*[w.value for w in self.adjusters])


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


def gen_term_hues(lightness=50, chroma=50, hue=0) -> list:
    """Generates 6 hues for terminal colors."""
    # just iterates the hue over the term order
    return [Color().set_LCH(lightness, chroma, 60*x+hue) for x in [0, 2, 1, 4, 5, 3]]


def build_colors(fg: Color, bg: Color, lightness, chroma, hue, dim) -> list:
    """Generates all 16 colors from Fg, Bg, and lch offsets"""

    colors = [bg]
    colors += gen_term_hues(lightness, chroma, hue)

    bgdim = list(bg.as_LCH())
    bgdim[0] += dim
    colors += [fg, Color().set_LCH(*bgdim)]

    colors += gen_term_hues(lightness-dim, chroma, hue)

    fgdim = list(fg.as_LCH())
    fgdim[0] -= dim
    colors.append(Color().set_LCH(*fgdim))

    return colors


def main():
    # Main text boxes
    main_box = Entry(label="Foreground/Background", value=LOREM_IPSUM_MINI, min_height=75)
    main_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    main_box.entry.props.editable = False
    main_box.entry.provider = Gtk.CssProvider()

    dim_box = Entry(label="Foreground2/Background2", value=LOREM_IPSUM_MINI, min_height=75)
    dim_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    dim_box.entry.props.editable = False
    dim_box.entry.provider = Gtk.CssProvider()

    # Labels
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

    # Bright [term 0-7]
    term_colors_bright = [
        Gtk.Label(label=f"color{x}") for x in range(len(term_color_labels))
    ]

    # Dim [term 8-15]
    term_colors_dim = [
        Gtk.Label(label=f"color{x + 8}") for x in range(len(term_color_labels))
    ]

    term_colors = term_colors_bright + term_colors_dim

    # add providers as prop for easy management. discount polymorphism
    for widget in [main_box] + term_colors_bright + term_colors_dim:
        widget.provider = Gtk.CssProvider()

    def set_all_colors(colors: list):
        # term color labels
        for num, c in enumerate(colors):
            # change bg to be appropriate
            bg = colors[0]
            if num == 0:
                bg = colors[7]
            elif num == 8:
                bg = colors[15]
            elif num > 8:
                bg = colors[8]
            override_color(term_colors[num], fg=c, bg=bg)
        # main boxes
        override_color(main_box.entry, fg=colors[7], bg=colors[0])
        override_color(dim_box.entry, fg=colors[15], bg=colors[8])

    def on_adj_change(widget):
        set_all_colors(gen_colors())

    # Pickers
    fg_adjuster = ColorAdjuster(Color(1.0, 1.0, 1.0))
    bg_adjuster = ColorAdjuster(Color(0.0, 0.0, 0.0))

    # Adjusters
    l_adj = Adjuster.new("Colors Lightness", 50, -100, 100, 5, 10, 1)
    c_adj = Adjuster.new("Colors Chroma", 50, -100, 100, 5, 10, 1)
    h_adj = Adjuster.new("Colors Hue Offset", 20, -180, 180, 5, 15, 1)
    d_adj = Adjuster.new("Dim/Difference in Contrasts", 20, -100, 100, 5, 10, 1)

    for w in fg_adjuster.adjusters+bg_adjuster.adjusters + [l_adj, c_adj, h_adj, d_adj]:
        w.adjustment.connect("value-changed", on_adj_change)

    # convert UI vals to Color list
    def gen_colors():
        return build_colors(
                fg_adjuster.color,
                bg_adjuster.color,
                l_adj.value,
                c_adj.value,
                h_adj.value,
                d_adj.value,
                )

    grid = Grid()
    # attach displays
    grid.attach_all(*term_color_labels, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(*term_colors_bright, row=1, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(*term_colors_dim, row=2, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(GC(main_box, width=8), GC(dim_box, width=8))

    # attach janky-ass custom fg/bg adjusters
    grid.attach_all(GC(Gtk.Label("Foreground/Background Adjusters"), width=2), direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(GC(fg_adjuster, width=2), GC(bg_adjuster, width=2), column=8)

    # attach other adjusters
    grid.attach_all(l_adj, c_adj, row=3, direction=Gtk.DirectionType.RIGHT)
    grid.attach_all(h_adj, d_adj, row=4, direction=Gtk.DirectionType.RIGHT)
    grid.props.margin=10

    app = App("Color Thing", grid)
    on_adj_change(None)
    app.launch()


if __name__ == "__main__":
    main()
