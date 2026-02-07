# Markdown Style Guide

## Headings

```markdown
# Main Title (H1) - One per file
## Section (H2)
### Subsection (H3)
#### Details (H4)
```

Best practices:
- One H1 per file
- Use ATX-style (#) not Setext (===)
- Space after #

## Lists

### Unordered
```markdown
- Item 1
- Item 2
  - Nested item
  - Another
- Item 3
```

### Ordered
```markdown
1. First
2. Second
3. Third
```

### Checklist
```markdown
- [x] Completed
- [ ] Not done
```

## Code Blocks

Inline: \`code\`

Block with language:
```python
def hello():
    print("Hello")
```

Always specify language for syntax highlighting.

## Links & Images

```markdown
# Text link
[Google](https://google.com)

# Image
![Alt text](path/to/image.jpg)

# Reference style
[Link text][ref]
[ref]: https://example.com
```

## Emphasis

```markdown
*Italic* or _Italic_
**Bold** or __Bold__
***Bold Italic*** or ___Bold Italic___
~~Strikethrough~~
```

## Tables

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
| Cell 3   | Cell 4   |
```

## Blockquotes

```markdown
> This is a quote
> Can span multiple lines
> 
> > Nested quote
```

## Horizontal Rule

```markdown
---
or
***
or
___
```

## Escaping

```markdown
\*not italic\*
\# not heading
```
