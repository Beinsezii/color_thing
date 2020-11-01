#!/usr/bin/python3

# TODO
# Try object-oriented builder instead of just using main.

import gi
import re
import os
import exporters
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk  # noqa: F401
from bszgw import Adjuster, AutoBox, Button, CheckButton, Entry, Grid, GridChild as GC, App, Message
from discount_babl import Color
from importlib import import_module
from pkgutil import iter_modules

# puts every python module from the exporters namespace package into a list for polymorphism
EXPORTERS = [
    import_module('exporters.' + m.name) for m in iter_modules(exporters.__path__)
]

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

NAME_CHARS = r"[a-zA-Z0-9 _-]+"


class ColorAdjuster(Grid):
    def __init__(self, color: Color, label=""):
        super(ColorAdjuster, self).__init__()

        self.color = color
        L, C, H = self.color.as_LCH()
        self.L_adj = Adjuster.new(f'{label} Lightness', L, -100, 200, 5, 10, 1)
        self.C_adj = Adjuster.new(f'{label} Chroma', C, -100, 200, 5, 10, 1)
        self.H_adj = Adjuster.new(f'{label} Hue', H, 0, 360, 5, 15, 1)
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


class Display(Gtk.Label):
    def __init__(self, label, value, tooltip=""):
        super(Display, self).__init__(label='oops')
        self.__label = label
        self.provider = Gtk.CssProvider()
        self.props.tooltip_text = tooltip
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, new):
        self.__value = new
        self.props.label = "{}: {}".format(self.__label, self.__value)


def gen_term_hues(lightness=50, chroma=50, hue=0) -> list:
    """Generates 6 hues for terminal colors."""
    # just iterates the hue over the term order
    return [Color().set_LCH(lightness, chroma, 60 * x + hue) for x in [0, 2, 1, 4, 5, 3]]


def build_colors(fg: Color, bg: Color, lightness, chroma, hue, dim, oled) -> list:
    """Generates all 16 colors from Fg, Bg, and lch offsets"""

    colors = [bg] if not oled else [Color(0, 0, 0)]
    colors += gen_term_hues(lightness, chroma, hue)

    bgdim = list(bg.as_LCH())
    bgdim[0] += dim
    colors += [fg, Color().set_LCH(*bgdim)]

    colors += gen_term_hues(lightness - dim, chroma, hue)

    fgdim = list(fg.as_LCH())
    fgdim[0] -= dim
    colors.append(Color().set_LCH(*fgdim))

    return colors


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


def name_valid(name: str) -> bool:  # questionable use since I save the re
    return re.match(f"^{NAME_CHARS}$", name) is not None


def save_to_file(fg, bg, l, c, h, dim, oled, name, accent):
    chooser = Gtk.FileChooserDialog()
    chooser.props.action = Gtk.FileChooserAction.SAVE
    chooser.props.do_overwrite_confirmation = True
    chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)
    chooser.set_current_name(name + '.color_thing')

    response = chooser.run()

    if response == Gtk.ResponseType.ACCEPT:
        data = [name] + list(fg.as_LCH()) + list(bg.as_LCH()) + [l, c, h, dim, oled, accent]
        with open(chooser.get_filename(), mode='w', encoding="UTF-8") as saveto:
            saveto.write("NAME:{}\n"
                         "FG_L:{:.1f}\nFG_C:{:.1f}\nFG_H:{:.1f}\n"
                         "BG_L:{:.1f}\nBG_C:{:.1f}\nBG_H:{:.1f}\n"
                         "L:{:.1f}\nC:{:.1f}\nH:{:.1f}\nDIM:{:.1f}\nOLED:{}\nACCENT:{}".format(*data))

    chooser.destroy()


def load_from_file():
    data = []
    chooser = Gtk.FileChooserDialog()
    chooser.props.action = Gtk.FileChooserAction.OPEN
    chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT)

    response = chooser.run()

    if response == Gtk.ResponseType.ACCEPT:
        try:
            with open(chooser.get_filename(), mode='r', encoding="UTF-8") as loadfrom:
                string = loadfrom.read()
                prefixes = [
                    "fg_l",
                    "fg_c",
                    "fg_h",
                    "bg_l",
                    "bg_c",
                    "bg_h",
                    "l",
                    "c",
                    "h",
                    "dim",
                ]
                # matches one of the prefixes followed by : and any number of spaces
                # then any number size with optional preceding hyphen or single decimal
                # and finally a newline immediately after.
                # Should be eval-safe
                regex = f"name: *({NAME_CHARS})\n"
                regex += r"".join([f"{x}: *(-?\d+\.?\d*)\n" for x in prefixes])
                regex += r"oled: *(true|false)\n"
                regex += r"accent: *(1[0-5]|[0-9])"
                match = re.match(regex, string.casefold())

                if match is None:
                    Message('Invalid File Content')
                else:
                    data.append(string[match.start(1):match.end(1)])
                    for x in match.groups()[1:-2]:
                        data.append(eval(x))
                    data.append(eval(match.groups()[-2].capitalize()))
                    data.append(eval(match.groups()[-1]))

        except UnicodeDecodeError:
            Message('Invalid File Type')
    chooser.destroy()
    return data


def export(colors, name, accent):
    check_buttons = [CheckButton(e.NAME, False) for e in EXPORTERS]

    grid = Grid()
    grid.props.margin = 5
    grid.attach_all(*check_buttons)

    dialog = Gtk.Dialog()
    dialog.get_content_area().add(grid)
    dialog.get_content_area().show_all()

    dialog.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)

    response = dialog.run()

    if response == Gtk.ResponseType.ACCEPT:
        confirm = Gtk.Dialog()
        confirm.props.modal = True

        functions = []
        folders = []
        files = []
        create_text = "The following files will be created:\n"
        overwrite_text = "The following files will be OVERWRITTEN:\n"

        for num, cb in enumerate(check_buttons):
            if cb.value:
                functions.append(EXPORTERS[num].EXPORT)
                folder = os.path.realpath(f'./{name}/' + EXPORTERS[num].NAME) + '/'
                folders.append(folder)
                files.append(folder + EXPORTERS[num].FORMAT.format(name=name))

        for f in files:
            if os.path.exists(f):
                overwrite_text += f + '\n'
            else:
                create_text += f + '\n'

        confirm.get_content_area().add(Gtk.Label(label=create_text + '\n' + overwrite_text))
        confirm.get_content_area().show_all()
        confirm.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        response = confirm.run()

        if response == Gtk.ResponseType.ACCEPT:
            if not os.path.exists(f'./{name}/') and len(files) > 0:
                os.mkdir(f'./{name}/')
            for num, fn in enumerate(functions):
                if not os.path.exists(folders[num]):
                    os.mkdir(folders[num])
                with open(files[num], mode='wb') as target:
                    target.write(fn(colors, name, accent))

        confirm.destroy()

    dialog.destroy()


def main():  # noqa: C901 I'm just gonna slap the UI code in main instead of making a class and writing self everywhere
    # Main text boxes
    main_box = Entry(label="Foreground/Background", value=LOREM_IPSUM, min_height=150, min_width=650)
    main_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    main_box.entry.props.editable = False
    main_box.entry.provider = Gtk.CssProvider()

    dim_box = Entry(label="Foreground2/Background2", value=LOREM_IPSUM, min_height=150, min_width=650)
    dim_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    dim_box.entry.props.editable = False
    dim_box.entry.provider = Gtk.CssProvider()

    accent_display = Display("Accent Color", 7, "Used for accents during export.\nClick colors to set.")

    def on_color_button(widget, num):
        accent_display.value = num[0]
        on_adj_change(widget)

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
        Button(f"color{x}", on_color_button, x) for x in range(8)
    ]

    # Dim [term 8-15]
    term_colors_dim = [
        Button(f"color{x + 8}", on_color_button, x + 8) for x in range(8)
    ]

    colors_grid = Grid()
    colors_grid.attach_all(*term_color_labels, direction=Gtk.DirectionType.RIGHT)
    colors_grid.attach_all(*term_colors_bright, row=1, direction=Gtk.DirectionType.RIGHT)
    colors_grid.attach_all(*term_colors_dim, row=2, direction=Gtk.DirectionType.RIGHT)

    term_colors = term_colors_bright + term_colors_dim

    # add providers as prop for easy management. discount polymorphism
    for widget in term_colors:
        widget.provider = Gtk.CssProvider()
        widget.props.height_request = 75
        widget.props.width_request = 75

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
        override_color(accent_display, fg=colors[0], bg=colors[accent_display.value])

    def on_adj_change(widget):
        set_all_colors(build_colors(*get_vals()[:-2]))

    def on_save(widget):
        save_to_file(*get_vals())

    def on_load(widget):
        data = load_from_file()
        widgets = [name_entry] + fg_adjuster.adjusters + bg_adjuster.adjusters + [
            l_adj,
            c_adj,
            h_adj,
            d_adj,
            oled_toggle,
            accent_display
        ]
        for num, var in enumerate(data):
            widgets[num].value = var
        # force re-load to doubly-double-check.
        on_adj_change(None)

    def on_export(widget):
        export(build_colors(*get_vals()[:-2]), *get_vals()[-2:])

    # Pickers
    fg_adjuster = ColorAdjuster(Color(1, 1, 1), "FG")
    bg_adjuster = ColorAdjuster(Color(0, 0, 0), "BG")

    # Adjusters
    l_adj = Adjuster.new("Colors Lightness", 50, -100, 100, 5, 10, 1)
    c_adj = Adjuster.new("Colors Chroma", 50, -100, 100, 5, 10, 1)
    h_adj = Adjuster.new("Colors Hue Offset", 20, -180, 180, 5, 15, 1)
    d_adj = Adjuster.new("Dim/Difference in Contrasts", 20, -100, 100, 5, 10, 1)
    color_adj_grid = Grid()
    color_adj_grid.attach_all(l_adj, h_adj)
    color_adj_grid.attach_all(c_adj, d_adj, column=1)

    for w in fg_adjuster.adjusters + bg_adjuster.adjusters + [l_adj, c_adj, h_adj, d_adj]:
        w.adjustment.connect("value-changed", on_adj_change)

    def on_ne_change(*args):
        if name_valid(name_entry.value):
            save_button.props.sensitive = True
            export_button.props.sensitive = True
        else:
            save_button.props.sensitive = False
            export_button.props.sensitive = False

    name_entry = Entry("Theme Name:", "Untitled Theme", multi_line=False)
    name_entry.props.orientation = 0
    name_entry.props.spacing = 5
    name_entry.text_buffer.connect("inserted-text", on_ne_change)
    name_entry.text_buffer.connect("deleted-text", on_ne_change)

    save_button = Button("Save", on_save, tooltip="Save current vals to file")
    load_button = Button("Load", on_load, tooltip="Load vals from file")
    oled_toggle = CheckButton("OLED Mode", False, tooltip="Make the BG pure black")
    export_button = Button("Export", on_export, tooltip="Export palette")
    action_bar = AutoBox([save_button, load_button, export_button, oled_toggle], 5, 5, 0)

    oled_toggle.connect('toggled', on_adj_change)

    def get_vals():
        return [
            fg_adjuster.color,
            bg_adjuster.color,
            l_adj.value,
            c_adj.value,
            h_adj.value,
            d_adj.value,
            oled_toggle.value,
            name_entry.value,
            accent_display.value,
        ]

    grid = Grid()

    grid.attach_all(
        GC(fg_adjuster, width=2),
        GC(bg_adjuster, width=2),
        main_box,
        dim_box,
        AutoBox([name_entry, accent_display], 5, 5, 0)
    )
    grid.attach_all(
        color_adj_grid,
        colors_grid,
        action_bar,
        column=1
    )
    grid.props.margin = 10

    app = App("Color Thing", grid)
    on_adj_change(None)
    app.launch()


if __name__ == "__main__":
    main()
