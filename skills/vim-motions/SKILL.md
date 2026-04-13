---
name: vim-motions
description: Vim keybindings, motions, text objects, operators, macros, registers, and modal editing for efficient text editing. Use when user asks about "vim commands", "vim motions", "text objects", "vim keybindings", "vim cheat sheet", "learn vim", "vim in VS Code", "neovim", "IdeaVim", "vim macros", "vim registers", "vim search and replace", "vimrc", "vim splits", or any Vim editing tasks.
---

# Vim Motions

Motions, operators, text objects, registers, macros, and configuration for efficient editing.

## Modal Editing Fundamentals

```
Normal    ESC or Ctrl-[    Navigate, manipulate, compose commands
Insert    i, a, o, etc.    Type text directly
Visual    v, V, Ctrl-v     Select text for operations
Command   :                Execute ex commands, search/replace
Replace   R                Overtype existing text
```

Normal mode is home base. Every other mode is entered for a specific purpose, then exited back to Normal.

## Basic Motions

### Character/Line

```
h j k l       Left, Down, Up, Right
0             Start of line
^             First non-blank character
$             End of line
g_            Last non-blank character
```

### Word

```
w / W         Next word/WORD start
b / B         Previous word/WORD start
e / E         Next word/WORD end
ge            Previous word end
```

word = letters/digits/underscores. WORD = anything non-blank. Use W/B/E for fast movement through punctuation-heavy code.

### Line and File Navigation

```
gg            First line
G             Last line
5G or :5      Go to line 5
H / M / L     Top / Middle / Bottom of screen
%             Jump to matching bracket/paren/brace
{ / }         Previous / Next blank line (paragraph boundary)
( / )         Previous / Next sentence
```

### Search and Find

```
f{char}       Find char forward on line
F{char}       Find char backward on line
t{char}       Till char forward (stop before)
T{char}       Till char backward
;             Repeat last f/F/t/T
,             Repeat last f/F/t/T (reverse)
/{pattern}    Search forward
?{pattern}    Search backward
n / N         Next / Previous match
*             Search word under cursor forward
#             Search word under cursor backward
gd            Go to local definition
gf            Go to file under cursor
```

### Scrolling

```
Ctrl-d / Ctrl-u     Scroll half page down / up
Ctrl-f / Ctrl-b     Scroll full page down / up
zz / zt / zb        Center / Top / Bottom current line
Ctrl-e / Ctrl-y     Scroll one line down / up
```

## Operators

```
d     Delete          c     Change (delete + insert)
y     Yank (copy)     >     Indent right
<     Indent left      =     Auto-indent
gq    Format/rewrap   gu    Lowercase
gU    Uppercase        g~    Toggle case
```

### Operator + Motion = Action

```
dw            Delete to next word start
d$ or D       Delete to end of line
dG / dgg      Delete to end / start of file
d3j           Delete current + 3 lines down
cw            Change to next word start
c$ or C       Change to end of line
ct)           Change till closing paren
yy            Yank entire line
y$            Yank to end of line
>>            Indent line right
3>>           Indent 3 lines
=ap           Auto-indent around paragraph
gqip          Reformat inside paragraph
gUiw          Uppercase inner word
```

## Text Objects

```
i = inner (inside delimiters)    a = around (including delimiters)

iw / aw       Word               iW / aW       WORD
is / as       Sentence           ip / ap       Paragraph
i" / a"       Double quotes      i' / a'       Single quotes
i` / a`       Backticks          i( / a(       Parentheses
i[ / a[       Brackets           i{ / a{       Braces
i< / a<       Angle brackets     it / at       HTML/XML tag
```

### Common Text Object Actions

```
ciw           Change inner word
ci"           Change inside double quotes
ci(           Change inside parentheses
da"           Delete around quotes (including the quotes)
dap           Delete around paragraph
dit           Delete inside HTML tag
vit           Select inside HTML tag
yiw           Yank inner word
yi{           Yank inside braces
>ip           Indent inner paragraph
=i{           Auto-indent inside braces
```

## Insert Mode Entry

```
i / I         Insert before cursor / at line start
a / A         Append after cursor / at line end
o / O         Open line below / above
s / S         Delete char / line and insert
C             Delete to end of line and insert
gi            Insert at last insert position
```

## Visual Mode

```
v             Character-wise visual
V             Line-wise visual
Ctrl-v        Block (column) visual
o             Jump to other end of selection
gv            Reselect last visual selection

Ctrl-v → select → I → type → ESC    Insert in all selected lines
Ctrl-v → select → A → type → ESC    Append to all selected lines
Ctrl-v → select → c → type → ESC    Change all selected lines
Ctrl-v → select → d                  Delete column
Ctrl-v → select → r{char}            Replace with char
V3j>          Select 4 lines, indent right
vip:sort      Select paragraph, sort lines
```

## Registers and Clipboard

```
"{reg}y       Yank into register {reg}
"{reg}p       Paste from register {reg}
"+y / "+p     Yank to / paste from system clipboard
"0p           Paste last yank (ignores deletes)
"_d           Delete into black hole (don't overwrite default register)
"ayiw         Yank word into register a
"Ayy          Append line to register a (uppercase = append)
:registers    Show all register contents

Special: "  last used   0  last yank    1-9  last deletes
         .  last insert  %  filename    :  last command  /  last search
```

## Macros

```
qa            Start recording macro into register 'a'
q             Stop recording
@a            Play macro 'a'
@@            Replay last played macro
5@a           Play macro 'a' 5 times
:5,20normal @a   Run macro on lines 5-20

Recursive: qaqqa...@aq  — clears a, records actions + self-call, stops on failure
Edit macro: "ap to paste, edit text, "ayy to yank back
```

## Marks

```
ma            Set mark 'a' at cursor position
'a / `a       Jump to line / exact position of mark 'a'
:marks        List all marks

Automatic marks:
''  ``        Last jump position
'.  `.        Last edit position
'^  `^        Last insert position
'[  `[  ']  `]    Start / end of last change or yank
'<  `<  '>  `>    Start / end of last visual selection

Uppercase marks (A-Z) are global across files:
mA            Set global mark A
'A            Jump to file and line of mark A
```

## Search and Replace

```
:s/old/new/           Replace first on current line
:s/old/new/g          Replace all on current line
:%s/old/new/g         Replace all in file
:%s/old/new/gc        Replace all with confirmation (y/n/a/q/l)
:5,20s/old/new/g      Replace on lines 5-20
:'<,'>s/old/new/g     Replace in visual selection
:%s/\v(\w+)/\U\1/g    Very magic mode — uppercase all words
:%s/\s\+$//           Strip trailing whitespace

Global command — run ex command on matching lines:
:g/TODO/d             Delete all lines containing TODO
:g/^$/d               Delete all blank lines
:g/pattern/normal A;  Append semicolon to matching lines

Inverse global — run on NON-matching lines:
:v/keep/d             Delete lines NOT containing "keep"
```

## Window Management

```
:sp [file]            Horizontal split (or Ctrl-w s)
:vsp [file]           Vertical split (or Ctrl-w v)
Ctrl-w h/j/k/l       Move to left/down/up/right window
Ctrl-w H/J/K/L       Move window to far position
Ctrl-w =              Equalize window sizes
Ctrl-w _ / Ctrl-w |   Maximize height / width
Ctrl-w o              Close all except current
Ctrl-w q              Close current window
Ctrl-w T              Move window to new tab
:tabnew               New tab
gt / gT               Next / previous tab
```

## Buffer Navigation

```
:ls           List open buffers
:bn / :bp     Next / previous buffer
:b#           Toggle to alternate buffer
:b {name}     Switch by partial name
:bd           Close current buffer
:bufdo %s/old/new/g   Replace across all buffers
```

## Useful Commands

```
.             Repeat last change (most powerful command in Vim)
u / Ctrl-r    Undo / Redo
J / gJ        Join lines with / without space
~             Toggle case of character
g~~           Toggle case of entire line
Ctrl-a        Increment number under cursor
Ctrl-x        Decrement number under cursor
ga            Show ASCII value of character
gf            Open file under cursor
gx            Open URL under cursor
:!cmd         Run shell command
:r !cmd       Insert shell command output
```

## .vimrc Essentials

```vim
let mapleader = " "
set number relativenumber
set ignorecase smartcase
set incsearch hlsearch
set expandtab tabstop=2 shiftwidth=2
set scrolloff=8
set clipboard=unnamedplus

nnoremap <leader>w :w<CR>
nnoremap <leader>q :q<CR>
nnoremap <leader>/ :noh<CR>
nnoremap Y y$
vnoremap < <gv
vnoremap > >gv
nnoremap n nzzzv
nnoremap N Nzzzv
```

## Vim in VS Code

```jsonc
// settings.json — vscodevim extension
"vim.leader": "<space>",
"vim.useSystemClipboard": true,
"vim.hlsearch": true,
"vim.smartRelativeLine": true,
"vim.handleKeys": {
  "<C-d>": true, "<C-u>": true,
  "<C-w>": false, "<C-b>": false, "<C-p>": false
}
```

Let VS Code handle Ctrl-w (close tab), Ctrl-b (sidebar), Ctrl-p (quick open). Let Vim handle Ctrl-d and Ctrl-u (scrolling).

## Vim in JetBrains (IdeaVim)

```
# ~/.ideavimrc
set ideajoin surround commentary NERDTree
map <leader>r <Action>(RenameElement)
map <leader>f <Action>(GotoFile)
map <leader>b <Action>(ToggleLineBreakpoint)
map <leader>d <Action>(Debug)
```

## Neovim Differences

```lua
-- Neovim uses init.lua (Lua) instead of .vimrc (Vimscript)
vim.g.mapleader = " "
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.tabstop = 2
vim.opt.shiftwidth = 2
vim.opt.expandtab = true
vim.opt.clipboard = "unnamedplus"

vim.keymap.set("n", "<leader>w", ":w<CR>")
vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv")  -- move selection down
vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv")  -- move selection up
-- Built-in LSP, Treesitter, terminal mode (Ctrl-\ Ctrl-n to exit)
```

## Productivity Patterns

```
ci"           Change inside quotes — cursor anywhere between them
da(           Delete around parens including the parens
yiw           Yank word without needing to be at word start
dap           Delete entire paragraph
*cwfix<ESC>   Find word under cursor, change it, then n. to repeat everywhere
xp            Transpose two characters
ddp           Swap current line with next
gf            Open filename under cursor
:e %:h/       Open file in same directory as current
qaI// <ESC>jq  Record macro to comment lines, repeat with @a
```
