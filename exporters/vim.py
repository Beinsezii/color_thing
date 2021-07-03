NAME = "Vim (Truecolor)"
FORMAT = "{name}.vim"


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
import bszgw
from color_thing import override_color, Display  # it *just works*, okay?

# Tooltips for color chooser #
# {{{
TT_C = """\
*Constant    any constant
 String        a string constant: "this is a string"
 Character    a character constant: 'c', '\n'
 Number        a number constant: 234, 0xff
 Boolean    a boolean constant: TRUE, false
 Float        a floating point constant: 2.3e10"""

TT_I = """\
*Identifier	any variable name
 Function	function name (also: methods for classes)"""

TT_S = """\
*Statement	any statement
 Conditional	if, then, else, endif, switch, etc.
 Repeat		for, do, while, etc.
 Label		case, default, etc.
 Operator	"sizeof", "+", "*", etc.
 Keyword	any other keyword
 Exception	try, catch, throw"""

TT_P = """\
*PreProc	generic Preprocessor
 Include	preprocessor #include
 Define		preprocessor #define
 Macro		same as Define
 PreCondit	preprocessor #if, #else, #endif, etc."""

TT_T = """\
*Type		int, long, char, etc.
 StorageClass	static, register, volatile, etc.
 Structure	struct, union, enum, etc.
 Typedef	A typedef"""

TT_SP = """\
*Special	any special symbol
 SpecialChar	special character in a constant
 Tag		you can use CTRL-] on this
 Delimiter	character that needs attention
 SpecialComment	special things inside a comment
 Debug		debugging statements"""

TT_U = """\
*Underlined	text that stands out, HTML links"""

TT_E = """\
*Error		any erroneous construct"""

TT_TD = """\
*Todo		anything that needs extra attention; mostly the
                keywords TODO FIXME and XXX"""
# }}}


class colorPicker(bszgw.Grid):
    # {{{
    def __init__(self, colors: list, label, value, tooltip=""):
        super(colorPicker, self).__init__(column_spacing=2, row_spacing=2)
        self.colors = colors
        self.buttons = []
        for n, c in enumerate(self.colors):
            button = bszgw.Button(f"{n}", self.on_button, n)
            button.provider = Gtk.CssProvider()
            override_color(button, fg=c, bg=colors[0])
            self.buttons.append(button)

        self.display = Display(label, value, tooltip)
        override_color(self.display, fg=self.colors[value], bg=self.colors[0])
        self.attach_all_down(bszgw.GridChild(self.display, width=8))
        self.attach_all_right(*self.buttons[:8], row=1)
        self.attach_all_right(*self.buttons[8:], row=2)

    def on_button(self, widget, val):
        self.display.value = val
        override_color(self.display, fg=self.colors[val], bg=self.colors[0])

    @property
    def value(self):
        return self.display.value
    # }}}


def choose_colors(cols: list, ac: int) -> dict:
    # {{{
    result = {}
    constant = colorPicker(cols, "Constant", 3, TT_C)
    identifier = colorPicker(cols, "Identifier", 6, TT_I)
    statement = colorPicker(cols, "Statement", 4, TT_S)
    preproc = colorPicker(cols, "PreProc", 2, TT_P)
    type = colorPicker(cols, "Type", 5, TT_T)
    special = colorPicker(cols, "Special", 14, TT_SP)
    underlined = colorPicker(cols, "Underlined", 11, TT_U)
    error = colorPicker(cols, "Error", 1, TT_E)
    todo = colorPicker(cols, "Todo", 9, TT_TD)

    grid = bszgw.Grid()
    grid.attach_all_down(bszgw.GridChild(Gtk.Label(
        "Vim (Truecolor) export color picker. See tooltips."), width=3))
    grid.attach_all_down(constant, preproc, underlined)
    grid.attach_all_down(identifier, type, error, column=1)
    grid.attach_all_down(statement, special, todo, column=2)

    dialog = Gtk.Dialog()
    dialog.get_content_area().add(grid)
    dialog.get_content_area().show_all()
    dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
    dialog.props.modal = True

    dialog.run()

    result["constant"] = constant.value
    result["identifier"] = identifier.value
    result["statement"] = statement.value
    result["preproc"] = preproc.value
    result["type"] = type.value
    result["special"] = special.value
    result["underlined"] = underlined.value
    result["error"] = error.value
    result["todo"] = todo.value

    dialog.destroy()
    return result
    # }}}


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    # {{{
    groups = choose_colors(colors, accent)
    colors = [c.as_HEX() for c in colors]
    data = f"""\
hi clear
if exists("syntax_on")
  syn reset
endif

let g:colors_name="{name}"

" Vars for easy setting
let s:fg = '{colors[7]}'
let s:bg = '{colors[0]}'
let s:fga = '{colors[15]}'
let s:bga = '{colors[8]}'
let s:ac = '{colors[accent]}'
"""
    for k in groups:
        data += f"let s:{k} = '{colors[groups[k]]}'\n"

    data += """\

" Highlight groups
" ## Basic Built-Ins ##
exe 'hi Normal guifg='.s:fg.' guibg='.s:bg
exe 'hi NormalFloat guifg='.s:fg.' guibg='.s:bga
exe 'hi NormalNC guifg='.s:fga

exe 'hi Cursor guifg='.s:bg.' guibg='.s:ac
hi! link LineNr NormalNC
exe 'hi CursorLineNr guifg='.s:ac
hi! link NonText LineNr

exe 'hi Visual guifg='.s:bg.' guibg='.s:fga
exe 'hi Search guifg='.s:bg.' guibg='.s:identifier
exe 'hi IncSearch guifg='.s:bg.' guibg='.s:type.' gui=NONE'

exe 'hi Folded guifg='.s:bga.' guibg='.s:fga

exe 'hi SignColumn guibg='.s:bga

exe 'hi Comment guifg='.s:fga

" ## Syntax ##
exe 'hi Constant guifg='.s:constant
exe 'hi Identifier guifg='.s:identifier
exe 'hi Statement guifg='.s:statement
exe 'hi PreProc guifg='.s:preproc
exe 'hi Type guifg='.s:type
exe 'hi Special guifg='.s:special.' gui=bold'
exe 'hi Underlined guifg='.s:underlined.' guisp='.s:underlined
exe 'hi Error guifg='.s:error.' guibg=NONE gui=bold'
exe 'hi Todo guifg='.s:todo.' guibg=NONE gui=bold'

" ## Misc Built-in ##
" ## Messages ##
exe 'hi Question guifg='.s:statement' guibg=NONE'
hi! link ErrorMsg Error
hi! link WarningMsg Special

hi! link Title Type
hi! link MoreMsg Identifier

" ## Popup/completion menu ##
hi! link Pmenu NormalFloat
hi! link PmenuSel Cursor
hi! link PmenuSbar Pmenu
exe 'hi PmenuThumb guibg='.s:fga

" ## Statusbar ##
hi! link User0 Cursor
exe 'hi User1 guifg='.s:bg.' guibg='.s:constant
exe 'hi User2 guifg='.s:bg.' guibg='.s:identifier
exe 'hi User3 guifg='.s:bg.' guibg='.s:statement
exe 'hi User4 guifg='.s:bg.' guibg='.s:preproc
exe 'hi User5 guifg='.s:bg.' guibg='.s:type
exe 'hi User6 guifg='.s:bg.' guibg='.s:special
exe 'hi User7 guifg='.s:bg.' guibg='.s:error
exe 'hi User8 guifg='.s:bg.' guibg='.s:underlined
exe 'hi User9 guifg='.s:bg.' guibg='.s:todo


" ## Vim Rainbow ##
let g:rainbow_conf = {
\	'guifgs': [''.s:constant, ''.s:identifier, ''.s:statement, ''.s:preproc, ''.s:type],
\}
"""

    return bytes(data, encoding='UTF-8')
    # }}}
