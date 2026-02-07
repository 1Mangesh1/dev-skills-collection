# Advanced Regex Techniques

## Lookahead & Lookbehind

```
(?=abc)       Positive lookahead: followed by abc
(?!abc)       Negative lookahead: not followed by abc
(?<=abc)      Positive lookbehind: preceded by abc
(?<!abc)      Negative lookbehind: not preceded by abc
```

Example: Match number not followed by %
```
\d+(?!%)
```

## Non-greedy Matching

```
.*?   Non-greedy any character
+?    Non-greedy one or more
??    Non-greedy zero or one
{n,}? Non-greedy n or more
```

Example: Extract text between tags (minimal)
```
<tag>(.*?)</tag>    # Matches minimal content (correct)
<tag>(.*)</tag>     # Matches maximal content (wrong)
```

## Named Groups

Python:
```python
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
match = re.search(pattern, '2024-01-20')
print(match['year'])  # 2024
```

JavaScript:
```javascript
const pattern = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/;
const match = '2024-01-20'.match(pattern);
console.log(match.groups.year);  // 2024
```

## Modifiers

```
i     Case insensitive
m     Multiline (^ and $ per line)
s     Dot matches newlines
x     Verbose (ignore whitespace)
g     Global (match all)
```

## Performance Tips

1. **Use anchors** - `^pattern$` is faster than `pattern`
2. **Narrow character class** - `[0-9]` faster than `[0-9a-zA-Z_]`
3. **Avoid backtracking** - Use `+` or `*` carefully
4. **Compile once** - Store regex objects
5. **Test thoroughly** - Edge cases creep in

## Common Mistakes

```
❌ .*           Greedy, slow, matches everything
✓ .+?           Non-greedy, better

❌ [a-zA-Z0-9_] Many character classes
✓ \w            Shorthand version

❌ (a|b|c|d|...) Many alternations
✓ [abcd...]     Character class

❌ ^abc.*xyz$  No middle constraint
✓ ^abc\w{10}xyz$ More specific
```
