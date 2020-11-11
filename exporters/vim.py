NAME = "Vim (Truecolor)"
FORMAT = "{name}.vim"

def col_reker_1to6(cols: list, ac: int) -> list:
    # {{{
    # trust me on this
    new_colors = [cols[ac - 1]]
    mod = 1 if ac % 2 else -1
    new_colors.append(cols[ac + mod - 1])

    cur = ac
    for x in range(2):
        cur += 2
        if cur > 6:
            cur -= 6
        new_colors.append(cols[cur - 1])
        new_colors.append(cols[cur + mod - 1])
    return new_colors
    # }}}


def color_rekerjigger(cols: list, ac: int) -> list:
    # {{{
    """Takes colors list and re-aranges them around the accent color"""
    # So basically the goal is, have the colors be in order of priority.
    # So the most used color would be the accent obviously,
    # then the second most used is the accent's compliment,
    # switch to new pair same thing.

    if ac < 8:
        return cols[0:1] + col_reker_1to6(cols[1:7], ac) + cols[7:9] + col_reker_1to6(cols[9:15], ac) + cols[15:]
    else:  # use dim colors first. im just gonna copy paste it since im lazy
        return cols[0:1] + col_reker_1to6(cols[9:15], ac) + cols[7:9] + col_reker_1to6(cols[1:7], ac) + cols[15:]
    # }}}


def EXPORT(colors: list, name: str, accent: int) -> bytes:
    if accent in [0, 7, 8, 15]:
        accent = 3
    colors = [c.as_HEX() for c in colors]
    colors = color_rekerjigger(colors, accent)
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

" Numbered colors are in order of priority, with lower being higher. Used for syntax.
"""
    for num, var in enumerate(list(range(1, 7)) + list(range(9, 15))):
        data += f"let s:c{num} = '{colors[var]}'\n"

    data += """\

" Highlight groups
" ## Basic Built-Ins ##
exe 'hi Normal guifg='.s:fg.' guibg='.s:bg
exe 'hi NormalFloat guifg='.s:fg.' guibg='.s:bga
exe 'hi NormalNC guifg='.s:fga

exe 'hi Cursor guifg='.s:bg.' guibg='.s:c0
hi! link LineNr NormalNC
exe 'hi CursorLineNr guifg='.s:c0
hi! link NonText LineNr

exe 'hi Visual guifg='.s:bg.' guibg='.s:fg
exe 'hi Search guifg='.s:bg.' guibg='.s:c1
exe 'hi IncSearch guifg='.s:bg.' guibg='.s:c2.' gui=NONE'

exe 'hi Folded guifg='.s:bga.' guibg='.s:fga

exe 'hi SignColumn guibg='.s:bga

exe 'hi Comment guifg='.s:fga

" ## Syntax ##
exe 'hi Constant guifg='.s:c0
exe 'hi Statement guifg='.s:c1
exe 'hi Type guifg='.s:c2
exe 'hi Identifier guifg='.s:c3
exe 'hi Error guifg='.s:c4.' guibg=NONE gui=bold'
exe 'hi PreProc guifg='.s:c5
exe 'hi Todo guifg='.s:c7.' guibg=NONE gui=bold'
exe 'hi Special guifg='.s:c10.' gui=bold'
exe 'hi Underlined guifg='.s:c11

" ## Misc Built-in ##
" ## Messages ##
exe 'hi Question guifg='.s:c1.' guibg=NONE'
hi! link ErrorMsg Error
hi! link WarningMsg Special

hi! link Title Type
hi! link MoreMsg Identifier

" ## Popup/completion menu ##
hi! link Pmenu NormalFloat
hi! link PmenuSel Cursor
hi! link PmenuSbar Pmenu
exe 'hi PmenuThumb guibg='.s:fga
"""

    return bytes(data, encoding='UTF-8')
