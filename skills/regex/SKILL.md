---
name: regex
description: Regular expression mastery with syntax, common patterns, and language-specific usage. Use when user asks to "write a regex", "match pattern", "validate email", "extract data with regex", "parse string", "regex for phone number", "lookahead", "backreference", "capture group", "regex replace", "grep pattern", "sed substitute", "catastrophic backtracking", or any regular expression tasks.
---

# Regular Expressions

Regex syntax, patterns, recipes, and cross-language reference.

## Core Syntax

### Character Classes

```
.           Any character (except newline, unless s/dotall flag)
\d  \D      Digit [0-9] / Non-digit
\w  \W      Word char [a-zA-Z0-9_] / Non-word
\s  \S      Whitespace [ \t\n\r\f\v] / Non-whitespace
[abc]       Character set (a, b, or c)
[^abc]      Negated set (not a, b, or c)
[a-z]       Range (a through z)
[a-zA-Z]    Multiple ranges
\p{L}       Unicode letter (PCRE/Java/JS with u flag/Rust)
\p{N}       Unicode number
```

### Quantifiers

```
*    +    ?       0+, 1+, 0-1 (greedy)
{3}  {3,} {3,5}  Exact, min, range
*?   +?   ??      Lazy (non-greedy) versions
*+   ++           Possessive (PCRE/Java) - no backtracking
```

Greedy: match max, then backtrack. Lazy: match min, then expand. Possessive: match max, never backtrack.

### Anchors & Boundaries

```
^  $        Start/end of string (or line with m flag)
\b  \B      Word boundary / Non-word boundary
\A  \Z      Start/end of string (ignores m flag)
```

### Groups & References

```
(abc)           Capture group
(?:abc)         Non-capturing group
(?<name>abc)    Named capture group (JS/PCRE/.NET)
(?P<name>abc)   Named capture group (Python)
\1              Backreference to group 1
\k<name>        Backreference to named group (JS/PCRE)
(?P=name)       Backreference to named group (Python)
(?>abc)         Atomic group (PCRE/Java) - no backtracking into group
```

### Lookahead & Lookbehind

Zero-width assertions: match a position without consuming characters.

```
(?=abc)     Positive lookahead: followed by abc
(?!abc)     Negative lookahead: NOT followed by abc
(?<=abc)    Positive lookbehind: preceded by abc
(?<!abc)    Negative lookbehind: NOT preceded by abc
```

```
^(?=.*\d)(?=.*[A-Z]).{8,}$   # Password: 8+ chars, digit + uppercase
\d+(?!%)                      # Number NOT followed by %
(?<=\$)\w+                    # Word preceded by $
(?<!bar)foo                   # foo not preceded by bar
```

Lookbehind limits: JS requires fixed-length. Python allows fixed-length alternation branches. PCRE allows variable-length with `\K`.

### Flags / Modifiers

```
g   Global (all matches)       i   Case-insensitive
m   Multiline (^/$ per line)   s   Dotall (. matches \n)
u   Unicode                    x   Extended (whitespace ignored, # comments)
```

Inline: `(?i)pattern` or scoped `(?i:abc)`.

## Non-Greedy (Lazy) Matching

```
<.*>      Greedy:  <b>bold</b>  → "<b>bold</b>" (first < to LAST >)
<.*?>     Lazy:    <b>bold</b>  → "<b>" then "</b>" (first < to NEXT >)
<[^>]*>   Negated class: same as lazy, faster (no backtracking)
```

## Common Patterns

### Validation

```
# Email (simplified)
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$

# URL
^https?://[^\s/$.?#].[^\s]*$

# Phone (US)
^\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}$

# IPv4 (strict 0-255)
^(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)$

# Date (YYYY-MM-DD)
^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$

# UUID v4
^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$

# Semver
^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-([\da-zA-Z-]+(?:\.[\da-zA-Z-]+)*))?(?:\+([\da-zA-Z-]+(?:\.[\da-zA-Z-]+)*))?$

# Hex color
^#?([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$

# Strong password (8+ chars, upper, lower, digit, special)
^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$

# Slug
^[a-z0-9]+(?:-[a-z0-9]+)*$

# JWT structure
^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$
```

### Extraction

```
https?://([^/\s]+)                     # Domain from URL
[^/\\]+$                               # Filename from path
-?\d+\.?\d*                            # Numbers (int or decimal)
(\w+)=([^\s&]+)                        # Key=value pairs
\[([^\]]+)\]\(([^)]+)\)                # Markdown links
^\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] \[(\w+)\] (.+)$  # Log line
```

## Substitution Patterns

```
$0 or \0    Entire match         ${name}     Named group (JS)
$1 or \1    First capture group  \g<name>    Named group (Python)

# Swap first/last name
Find:    (\w+) (\w+)         Replace: $2, $1

# camelCase to snake_case
Find:    ([a-z])([A-Z])      Replace: $1_\l$2

# Remove console.log lines
Find:    ^\s*console\.log\([^)]*\);?\s*\n    Replace: (empty)
```

## Language-Specific Usage

### JavaScript

```javascript
const re = /\d+/g;                              // Literal
const re2 = new RegExp('\\d+', 'g');            // Constructor
/^\d+$/.test('123');                             // true
'abc 123 def 456'.match(/\d+/g);                // ['123', '456']

for (const m of 'a1 b2'.matchAll(/([a-z])(\d)/g)) {
  console.log(m[1], m[2]);                      // a 1, b 2
}

'hello'.replace(/[aeiou]/g, c => c.toUpperCase());  // "hEllO"

// Named groups
const m = '2024-01-15'.match(/(?<y>\d{4})-(?<m>\d{2})-(?<d>\d{2})/);
m.groups.y;                                      // '2024'

'$100 €200'.match(/(?<=\$)\d+/);                 // ['100'] (ES2018+)
```

### Python

```python
import re

re.match(r'^\d+', '123abc')              # Match from start
re.search(r'\d+', 'abc123')              # Search anywhere
re.findall(r'\d+', 'a1 b2 c3')           # ['1', '2', '3']
re.sub(r'\d+', 'X', 'a1b2')              # 'aXbX'

pat = re.compile(r'\b\w{4}\b')            # Compiled for reuse
pat.findall('the quick brown fox')        # ['quick', 'brown']

# Named groups (Python syntax)
m = re.search(r'(?P<year>\d{4})-(?P<month>\d{2})', '2024-01')
m.group('year')                           # '2024'
m.groupdict()                             # {'year': '2024', 'month': '01'}

# Verbose mode
pat = re.compile(r'''
    (?P<year>\d{4})   # year
    -(?P<month>\d{2}) # month
    -(?P<day>\d{2})   # day
''', re.VERBOSE)
```

### Go

```go
import "regexp"

re := regexp.MustCompile(`\d+`)             // Panics on bad pattern
re.MatchString("abc123")                     // true
re.FindString("abc 123 def")                 // "123"
re.FindAllString("a1 b2", -1)               // ["1", "2"]
re.ReplaceAllString("a1b2", "X")             // "aXbX"

// Named groups
re := regexp.MustCompile(`(?P<year>\d{4})-(?P<month>\d{2})`)
match := re.FindStringSubmatch("2024-01")
// match[re.SubexpIndex("year")] == "2024"
```

Go uses RE2: no backreferences, no lookahead/lookbehind. Guarantees linear-time matching.

### Rust

```rust
use regex::Regex;

let re = Regex::new(r"\d+").unwrap();
re.is_match("abc123");                       // true
re.find("abc 123").unwrap().as_str();         // "123"

// Named captures
let re = Regex::new(r"(?P<y>\d{4})-(?P<m>\d{2})").unwrap();
let caps = re.captures("2024-01").unwrap();
&caps["y"];                                   // "2024"
```

Rust `regex` crate uses RE2-like semantics. Use `fancy-regex` for PCRE features.

## Regex Flavor Differences

| Feature               | PCRE        | ECMAScript (JS) | POSIX ERE  | RE2 (Go/Rust) | Python re  |
|-----------------------|-------------|-----------------|------------|----------------|------------|
| Lookahead             | Yes         | Yes             | No         | No             | Yes        |
| Lookbehind            | Variable-len| Fixed-len       | No         | No             | Fixed-len  |
| Named groups          | `(?<n>)`    | `(?<n>)`        | No         | `(?P<n>)`      | `(?P<n>)`  |
| Backreferences        | `\1`        | `\1`            | `\1` (BRE) | No             | `\1`       |
| Atomic groups         | `(?>)`      | No              | No         | Automatic      | No         |
| Possessive quantifiers| `++` `*+`   | No              | No         | No             | No         |
| Unicode properties    | `\p{L}`     | `\p{L}` (u flag)| No         | `\p{L}`        | Limited    |
| Recursive patterns    | `(?R)`      | No              | No         | No             | No         |

## CLI Tools

### grep / sed / awk

```bash
# grep
grep 'pattern' file.txt              # Basic regex (BRE)
grep -E 'extended|regex' file.txt    # Extended regex (ERE)
grep -P '\d{3}' file.txt             # Perl regex (GNU grep only)
grep -oirn 'pattern' src/            # -o only match, -i case, -r recursive, -n line nums

# sed
sed 's/old/new/g' file.txt           # Replace all
sed -E 's/([0-9]+)/[\1]/g' file.txt  # Extended regex with groups
sed '/pattern/d' file.txt            # Delete matching lines

# awk
awk '/pattern/ {print $0}' file.txt            # Print matching lines
awk '$3 ~ /^[0-9]+$/ {print $1}' file.txt      # Field regex match
```

### ripgrep (rg)

```bash
rg '\d{3}-\d{4}' src/               # Recursive, fast, .gitignore-aware
rg -t py 'import' .                 # Filter by file type
rg -U 'struct.*\n.*field' .         # Multiline match
rg --pcre2 '(?<=\$)\d+' .           # PCRE2 features
rg -r '$1' '(\w+)@\w+' emails.txt   # Replace (output only)
```

## VS Code Find & Replace

```
# Enable regex: click .* button or Alt+R
# Capture groups in replace: $1, $2, etc.

Find:    (\w+):\s*(\w+)        Replace: $2: $1
Find:    console\.log\(.*?\)   Replace: (empty)

# Case modifiers in replacement
\u  Next char uppercase    \U  Uppercase until \E
\l  Next char lowercase    \L  Lowercase until \E

Find:    const (\w+)           Replace: const \l$1
```

## Performance & Security

### Catastrophic Backtracking

Nested quantifiers cause exponential time on non-matching input:

```
# DANGEROUS                    # SAFE alternative
(a+)+b                         a+b
(a|a)+b                        [a]+b
(\w+)*@                        \w+@
```

### ReDoS (Regular Expression Denial of Service)

Mitigations:
- Use RE2-based engines (Go, Rust) which guarantee linear time
- Set timeouts on regex execution
- Validate/limit input length before matching
- Never build regex from untrusted user input

## Unicode & International Text

```
\p{L}+              # Any Unicode letter (PCRE, Java, Rust, JS with u flag)
[\u4e00-\u9fff]+     # CJK Unified Ideographs
\p{Emoji}            # Emoji (modern engines)

# JS: always use u flag for Unicode
/\p{L}+/u            # Correct - \w is still ASCII-only even with u

# Python 3: re handles Unicode by default
re.findall(r'\w+', 'cafe\u0301 nai\u0308ve')  # ['cafe\u0301', 'nai\u0308ve']
```

## Multiline & Dotall Modes

```
/^start/m             # Multiline: ^ matches start of any line
/start.*end/s         # Dotall: . matches \n
/start[\s\S]*?end/    # Cross-line match without s flag
```

## Testing & Debugging

- **regex101.com** - Test PCRE, JS, Python, Go with live explanation and debugger
- **regexr.com** - Visual tester with community patterns
- Python: `re.compile(pattern, re.DEBUG)` prints parse tree
- Build incrementally: start simple, add complexity, test each step

## When NOT to Use Regex

- **HTML/XML** - Use a parser (BeautifulSoup, cheerio, DOMParser)
- **JSON** - Use `JSON.parse()` or equivalent
- **Balanced nesting** - Brackets, recursive grammars need parser generators
- **Strict email/URL validation** - Full RFC specs are too complex; use a library
- **200+ char patterns** - If you can't read it, use code instead

## Reference

For more recipes and testing tips: `references/recipes.md`
