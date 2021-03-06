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
from bszgw import AutoBox, Button, CheckButton, ComboBox, Entry, SpinScale, Grid, GridChild as GC, App, Message
from discount_babl import Color
from importlib import import_module
from pkgutil import iter_modules

# puts every python module from the exporters namespace package into a list for polymorphism
EXPORTERS = [
    import_module('exporters.' + m.name) for m in iter_modules(exporters.__path__)
]

LOREM_IPSUM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."

NAME_CHARS = r"[a-zA-Z0-9_-]+"


class ColorAdjuster(Grid):
    def __init__(self, label, *vals):
        super(ColorAdjuster, self).__init__()

        self.color = Color()
        self.color_alt = Color()
        vals = list(vals) + [0] * 6
        L, C, H, LA, CA, HA = vals[:6]
        self.L_adj = SpinScale.new(L, 0, 100, 5, 10, f"{label} Lightness", 1)
        self.C_adj = SpinScale.new(C, 0, 100, 5, 10, f"{label} Chroma", 1)
        self.H_adj = SpinScale.new(H, 0, 360, 5, 15, f"{label} Hue", 1)
        self.L_alt_adj = SpinScale.new(LA, -100, 100, 5, 10, f"{label} Alt Lightness", 1)
        self.C_alt_adj = SpinScale.new(CA, -100, 100, 5, 10, f"{label} Alt Chroma", 1)
        self.H_alt_adj = SpinScale.new(HA, -180, 180, 5, 15, f"{label} Alt Hue", 1)
        self.adjusters = [self.L_adj, self.C_adj, self.H_adj, self.L_alt_adj, self.C_alt_adj, self.H_alt_adj]
        for w in self.adjusters:
            w.adjustment.connect("value-changed", self.__set)

        self.attach_all_right(*self.adjusters[:3])
        self.attach_all_right(*self.adjusters[3:], row=1)

        self.__set(None)

    def __set(self, widget):
        l, c, h, loff, coff, hoff = [w.value for w in self.adjusters]
        self.color.set_LCH(l, c, h)
        self.color_alt.set_LCH(l + loff, c + coff, h + hoff)


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


def build_colors(  # noqa: C901  fuck you its only like 50 lines they're just spaced
    fg: Color,
    bg: Color,
    fg_alt: Color,
    bg_alt: Color,
    lightness,
    chroma,
    hue,
    lightness_alt,
    chroma_alt,
    hue_alt,
    clip,
    name,
    accent,
) -> list:
    """Generates all 16 colors from Fg, Bg, and lch offsets"""

    colors = [bg]
    colors += gen_term_hues(lightness, chroma, hue)

    colors += [fg, bg_alt]

    colors += gen_term_hues(lightness + lightness_alt, chroma + chroma_alt, hue + hue_alt)

    colors += [fg_alt]

    if clip == "L":
        for x in list(range(1, 7)) + list(range(9, 15)):
            R, G, B = colors[x].as_SRGB()
            if R > 1 or G > 1 or B > 1:
                l, c, h = colors[x].as_LCH()
                colors[x].set_LCH(0, c, h)
                R, G, B = colors[x].as_SRGB()
                while R < 1 and G < 1 and B < 1:
                    l, c, h = colors[x].as_LCH()
                    colors[x].set_LCH(l + 0.1, c, h)
                    R, G, B = colors[x].as_SRGB()

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


def save_to_file(*args):
    args = list(args)
    name = args.pop(-3)
    chooser = Gtk.FileChooserDialog()
    chooser.props.action = Gtk.FileChooserAction.SAVE
    chooser.props.do_overwrite_confirmation = True
    chooser.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_SAVE, Gtk.ResponseType.ACCEPT)
    chooser.set_current_name(name + '.color_thing')

    response = chooser.run()

    if response == Gtk.ResponseType.ACCEPT:
        with open(chooser.get_filename(), mode='w', encoding="UTF-8") as saveto:
            saveto.write("NAME:{}\n"
                         "FG_L:{:.1f}\nFG_C:{:.1f}\nFG_H:{:.1f}\n"
                         "FG_ALT_L:{:.1f}\nFG_ALT_C:{:.1f}\nFG_ALT_H:{:.1f}\n"
                         "BG_L:{:.1f}\nBG_C:{:.1f}\nBG_H:{:.1f}\n"
                         "BG_ALT_L:{:.1f}\nBG_ALT_C:{:.1f}\nBG_ALT_H:{:.1f}\n"
                         "L:{:.1f}\nC:{:.1f}\nH:{:.1f}\n"
                         "L_ALT:{:.1f}\nC_ALT:{:.1f}\nH_ALT:{:.1f}\n"
                         "ACCENT:{}\nCLIP:{}".format(name, *args))

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
                    "fg_alt_l",
                    "fg_alt_c",
                    "fg_alt_h",
                    "bg_l",
                    "bg_c",
                    "bg_h",
                    "bg_alt_l",
                    "bg_alt_c",
                    "bg_alt_h",
                    "l",
                    "c",
                    "h",
                    "l_alt",
                    "c_alt",
                    "h_alt",
                ]
                # matches one of the prefixes followed by : and any number of spaces
                # then any number size with optional preceding hyphen or single decimal
                # and finally a newline immediately after.
                # Should be eval-safe
                regex = f"name: *({NAME_CHARS})\n"
                regex += r"".join([f"{x}: *(-?\d+\.?\d*)\n" for x in prefixes])
                regex += r"accent: *(1[0-5]|[0-9])\n"
                regex += r"clip: *([ln])"
                match = re.match(regex, string.casefold())

                if match is None:
                    Message('Invalid File Content')
                else:
                    data.append(string[match.start(1):match.end(1)])
                    for x in match.groups()[1:-1]:
                        data.append(eval(x))
                    data.append(match.groups()[-1].upper())

        except UnicodeDecodeError:
            Message('Invalid File Type')
    chooser.destroy()
    return data


def export(colors, name, accent):
    check_buttons = [CheckButton(e.NAME, False) for e in EXPORTERS]

    grid = Grid()
    grid.props.margin = 5
    grid.attach_all_down(*check_buttons)

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
    main_box = Entry(label="Foreground/Background", value=LOREM_IPSUM, min_height=150, min_width=650, multi_line=True)
    main_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    main_box.entry.props.editable = False
    main_box.entry.provider = Gtk.CssProvider()

    dim_box = Entry(label="Foreground2/Background2", value=LOREM_IPSUM, min_height=150, min_width=650, multi_line=True)
    dim_box.entry.props.wrap_mode = Gtk.WrapMode.WORD
    dim_box.entry.props.editable = False
    dim_box.entry.provider = Gtk.CssProvider()

    accent_display = Display("Accent Color", 7, "Used for accents during export.\nClick colors to set.")
    reverse_check = CheckButton("Reverse Preview", False)

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
    colors_grid.attach_all_right(*term_color_labels)
    colors_grid.attach_all_right(*term_colors_bright, row=1)
    colors_grid.attach_all_right(*term_colors_dim, row=2)

    term_colors = term_colors_bright + term_colors_dim

    # add providers as prop for easy management. discount polymorphism
    for widget in term_colors:
        widget.provider = Gtk.CssProvider()
        widget.props.height_request = 75
        widget.props.width_request = 75
        widget.props.expand = True

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
            if reverse_check.value:
                c, bg = bg, c
            override_color(term_colors[num], fg=c, bg=bg)
        # main boxes
        override_color(main_box.entry, fg=colors[7], bg=colors[0])
        override_color(dim_box.entry, fg=colors[15], bg=colors[8])
        override_color(accent_display, fg=colors[0], bg=colors[accent_display.value])

    def on_adj_change(widget):
        set_all_colors(build_colors(*get_vals()))

    reverse_check.connect('toggled', on_adj_change)

    def on_save(widget):
        save_to_file(
            *[w.value for w in fg_adjuster.adjusters + bg_adjuster.adjusters + [
                l_adj,
                c_adj,
                h_adj,
                l2_adj,
                c2_adj,
                h2_adj,
                name_entry,
                accent_display,
                clip_combo,
            ]],
        )

    def on_load(widget):
        data = load_from_file()
        widgets = [name_entry] + fg_adjuster.adjusters + bg_adjuster.adjusters + [
            l_adj,
            c_adj,
            h_adj,
            l2_adj,
            c2_adj,
            h2_adj,
            accent_display,
            clip_combo,
        ]
        for num, var in enumerate(data):
            widgets[num].value = var
        # force re-load to doubly-double-check.
        on_adj_change(None)

    def on_export(widget):
        export(build_colors(*get_vals()), *get_vals()[-2:])

    # Pickers
    fg_adjuster = ColorAdjuster("FG", 100, 0, 0, -20)
    bg_adjuster = ColorAdjuster("BG", 0, 0, 0, 10)

    # Adjusters
    l_adj = SpinScale.new(50, 0, 100, 5, 10, "Colors Lightness", 1)
    c_adj = SpinScale.new(50, 0, 100, 5, 10, "Colors Chroma", 1)
    h_adj = SpinScale.new(20, -180, 180, 5, 15, "Colors Hue Offset", 1)
    l2_adj = SpinScale.new(-20, -100, 100, 5, 10, "Colors Alt Lightness", 1)
    c2_adj = SpinScale.new(0, -100, 100, 5, 10, "Colors Alt Chroma", 1)
    h2_adj = SpinScale.new(0, -180, 180, 5, 15, "Colors Alt Hue", 1)
    color_adj_grid = Grid()
    color_adj_grid.attach_all_down(l_adj, h_adj, c2_adj)
    color_adj_grid.attach_all_down(c_adj, l2_adj, h2_adj, column=1)

    for w in fg_adjuster.adjusters + bg_adjuster.adjusters + [l_adj, c_adj, h_adj, l2_adj, h2_adj, c2_adj]:
        w.adjustment.connect("value-changed", on_adj_change)

    def on_ne_change(*args):
        if name_valid(name_entry.value):
            save_button.props.sensitive = True
            export_button.props.sensitive = True
        else:
            save_button.props.sensitive = False
            export_button.props.sensitive = False

    name_entry = Entry("Untitled_Theme")
    name_entry.props.tooltip_text = "Theme Name"
    name_entry.text_buffer.connect("inserted-text", on_ne_change)
    name_entry.text_buffer.connect("deleted-text", on_ne_change)
    clip_tt = """\
Clipping affects the auto-gened colors, aka 1-6 and 9-14
since the user doesn't have individual control.

Clip L: Reduces lightness until all RGB vals are < 100%. 'Dumb' method. Doesn't account for vals <0%
"""
    clip_combo = ComboBox.new_dict({"Don't Clip": 'N', "Clip Lightness": 'L'}, 'N')
    clip_combo.props.tooltip_text = clip_tt
    name_clip_grid = Grid()
    name_clip_grid.attach_all_right(name_entry, clip_combo)

    clip_combo.connect("changed", on_adj_change)

    save_button = Button("Save", on_save)
    save_button.props.tooltip_text = "Save current vals to file"
    load_button = Button("Load", on_load)
    load_button.props.tooltip_text = "Load vals from file"
    export_button = Button("Export", on_export)
    export_button.props.tooltip_text = "Export palette"
    action_bar = AutoBox([reverse_check, accent_display, save_button, load_button, export_button], 5, 5, 0)

    def get_vals():
        return [
            fg_adjuster.color,
            bg_adjuster.color,
            fg_adjuster.color_alt,
            bg_adjuster.color_alt,
            l_adj.value,
            c_adj.value,
            h_adj.value,
            l2_adj.value,
            c2_adj.value,
            h2_adj.value,
            clip_combo.value,
            name_entry.value,
            accent_display.value,
        ]

    grid = Grid()

    grid.attach_all_down(
        GC(fg_adjuster, width=2),
        GC(bg_adjuster, width=2),
        main_box,
        dim_box,
        name_clip_grid,
    )
    grid.attach_all_down(
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
