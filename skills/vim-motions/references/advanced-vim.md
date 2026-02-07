# Advanced Vim Techniques

## Macros

Recording:
```
qa               Start recording in register 'a'
(editing)        Perform actions
q                Stop recording
@a               Play back macro 'a'
@@               Repeat last macro
3@a              Play macro 3 times
```

Example - Add semicolon to line end:
```
qa
$
a;
Esc
q
@a              Play on current line
```

## Marks & Jumps

```
ma               Mark current position as 'a'
mA               Global mark 'a' (cross-file)
'a               Jump to mark 'a'
`a               Jump to exact char position
''               Jump to previous position
`.               Jump to last edit location
m.               Last modified position
```

## Ranges

```
:1,5p            Print lines 1-5
:5,$d            Delete from line 5 to end
:45 .            Line 45 (same as :45)
:.,+5y           Copy current line and 5 below
:'a,'bd          Delete from mark a to b
:%s/old/new/     Replace in entire file
```

## Visual Selection

```
v                Start visual (character)
V                Start visual (line)
Ctrl-v           Start visual (block)
o                Toggle to other end
aw               Select a word
ap               Select a paragraph
i{               Select inside braces
```

Block editing:
```
Ctrl-v           Select block
I                Insert at start of all lines
Type text
Esc              Apply to all lines
```

## Advanced Search & Replace

```
/\<word\>        Search whole word
/[0-9]\+         Search regex (one or more digits)
:%s/foo/bar/gc   Replace with confirmation
:%s/\(.\)\(.\)/\2\1/   Swap every 2 characters
:%s/^/  /        Add indent to all lines
```

## Folding

```
zf               Create fold
zo               Open fold
zc               Close fold
zR               Open all folds
zM               Close all folds
zj               Next fold
zk               Previous fold
```

Method-based:
```
:set foldmethod=indent
:set foldmethod=marker
:set foldmethod=expr
```

## Plugins & Productivity

Essential plugins:
- **vim-surround** - Change surrounding chars
- **vim-commentary** - Toggle comments
- **vim-easymotion** - Fast navigation
- **fzf.vim** - Fuzzy file finding
- **vim-fugitive** - Git integration
- **NERDTree** - File browser
- **vim-airline** - Status line

## Efficiency Tips

1. Use `hjkl` instead of arrow keys
2. Combine operators: `diw` = delete inner word
3. Use marks for frequently accessed spots
4. Record macros for repetitive tasks
5. Learn regex for search/replace
6. Use visual block for column edits
7. Exploit keyword length in search
