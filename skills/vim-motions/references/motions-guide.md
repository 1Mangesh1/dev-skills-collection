# Vim Motions Complete Guide

## Navigation

### Character Level
```
h        Move left
j        Move down
k        Move up
l        Move right
```

### Word Level
```
w        Next word (start)
W        Next WORD (whitespace separated)
e        End of word
E        End of WORD
b        Previous word
B        Previous WORD
```

### Line Level
```
0        Start of line
^        First non-space
$        End of line
g_       Last non-space
```

### Document Level
```
gg       Start of file
G        End of file
:n       Go to line n
Ctrl-g   Show current position
```

### Screen Level
```
H        Top of screen
M        Middle of screen
L        Bottom of screen
Ctrl-u   Page up
Ctrl-d   Page down
Ctrl-f   Page forward
Ctrl-b   Page back
```

## Editing

### Insert
```
i        Insert before cursor
a        Insert after cursor
I        Insert at line start
A        Insert at line end
o        New line below
O        New line above
s        Substitute character
S        Substitute line
```

### Delete/Cut
```
x        Delete char at cursor
X        Delete char before cursor
d<move>  Delete range
dd       Delete entire line
D        Delete to end of line
```

### Copy/Paste
```
y<move>  Yank (copy)
yy       Yank entire line
Y        Yank to end of line
p        Paste after cursor
P        Paste before cursor
```

### Change
```
c<move>  Change range
cc       Change entire line
C        Change to end of line
r<char>  Replace character
~        Toggle case
```

## Text Objects

### Quotes
```
i"       Inside double quotes
a"       Around double quotes
i'       Inside single quotes
a'       Around single quotes
```

### Brackets
```
i(       Inside parentheses
a(       Around parentheses
i[       Inside brackets
a[       Around brackets
i{       Inside braces
a{       Around braces
```

### Words & Sentences
```
iw       Inner word
aw       A word (with space)
is       Inner sentence
as       A sentence
ip       Inner paragraph
ap       A paragraph
```

### Tag (HTML/XML)
```
it       Inner tag
at       Around tag
```

## Combining Motions

```
d2w      Delete 2 words
y5j      Copy 5 lines down
3dd      Delete 3 lines
c10l     Change 10 characters
v3w      Select 3 words
d$       Delete to end of line
y)       Copy to next )
c}       Change to }
```

## Searching

```
/pattern     Search forward
?pattern     Search backward
n            Next match
N            Previous match
*            Search word under cursor
#            Search backward for word
%            Find matching bracket
```

## Marks & Registers

```
ma           Set mark 'a'
'a           Jump to mark 'a'
`a           Jump to exact char position
'"           Last closed buffer
'"           Unnamed register (last delete/yank)
"a           Named register 'a'
":           Last command
"/           Last search
```
