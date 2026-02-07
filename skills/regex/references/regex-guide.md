# Regular Expressions (Regex) Guide

## Basic Patterns

```
.       Matches any character
^       Start of line
$       End of line  
*       0 or more repetitions
+       1 or more repetitions
?       0 or 1 repetition
{n}     Exactly n repetitions
{n,}    n or more repetitions
{n,m}   Between n and m repetitions
```

## Character Classes

```
[abc]       Any of a, b, c
[^abc]      Not a, b, c
[a-z]       Range: a to z
[0-9]       Digits
\d          Digit (shorthand)
\D          Non-digit
\w          Word char [a-zA-Z0-9_]
\W          Non-word char
\s          Whitespace
\S          Non-whitespace
```

## Common Patterns

### Email
```
^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$
```

### Phone (US)
```
^(\+1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$
```

### URL
```
https?://(?:www\.)?[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:/[^\s]*)?
```

### IP Address
```
^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$
```

### Date (YYYY-MM-DD)
```
^\d{4}-?(?:0[1-9]|1[0-2])-?(?:0[1-9]|[12][0-9]|3[01])$
```

## Anchors & Word Boundaries

```
^word      Starts with word
word$      Ends with word
\bword\b   Whole word
^$         Empty line
\A         Start of string
\Z         End of string
```

## Groups & Capturing

```
(abc)       Capture group
(?:abc)     Non-capturing group
(abc|def)   Alternation
\1          Backreference to group 1
```

## Examples

```bash
# Extract emails
grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' file.txt

# Find URLs
grep -oE 'https?://[^\s]+' file.txt

# Replace pattern
sed 's/old.*/new/g' file.txt

# Match lines starting with #
grep '^#' file.txt
```

## Regex Flavors

- **PCRE** (Perl Compatible) - Most powerful
- **ECMA** (JavaScript) - Web standard
- **POSIX** (Basic/Extended) - Unix standard
- **Python** - `re` module
- **Java** - `Pattern` class
