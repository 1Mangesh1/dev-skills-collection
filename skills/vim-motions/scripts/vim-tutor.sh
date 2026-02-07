#!/usr/bin/env bash
# Vim Motion Tutor
# Practice and reference vim motions

show_basic_motions() {
    cat << 'EOF'
=== Basic Vim Motions ===

MOVEMENT
h         Move left
j         Move down
k         Move up
l         Move right
w         Next word
b         Previous word
e         End of word
0         Start of line
$         End of line
gg        Start of file
G         End of file
nG        Go to line n

EDITING
i         Insert before cursor
a         Insert after cursor
I         Insert at line start
A         Insert at line end
o         New line below
O         New line above
x         Delete character
d         Delete (dd = delete line)
y         Copy (yy = copy line)
p         Paste
u         Undo
Ctrl-r    Redo

SEARCHING
/pattern  Search forward
?pattern  Search backward
n         Next match
N         Previous match
*         Search word under cursor
g*        Search partial word
EOF
}

show_advanced_motions() {
    cat << 'EOF'
=== Advanced Vim Motions ===

RANGES
d2w       Delete 2 words
y5j       Copy 5 lines down
d$        Delete to end of line
c0        Change to start of line

MARKS
ma        Set mark 'a'
'a        Go to mark 'a'
`a        Go to exact position of mark

MACROS
qa        Start recording macro 'a'
q         Stop recording
@a        Play macro 'a'
@@        Repeat last macro

TEXT OBJECTS
iw        Inner word
aw        A word
is        Inner sentence
as        A sentence
ip        Inner paragraph
ap        A paragraph
i"        Inside quotes
a}        Around braces

COMBINING
cw        Change word
d)        Delete to next )
y2w       Yank 2 words
v3j       Select 3 lines down
EOF
}

show_vim_cheatsheet() {
    show_basic_motions
    echo ""
    show_advanced_motions
}

# Usage
show_vim_cheatsheet
