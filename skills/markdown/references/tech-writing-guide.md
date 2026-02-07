# Writing Technical Documentation

## Structure

1. **Overview** - What is this?
2. **Prerequisites** - What do I need?
3. **Installation** - How do I get it?
4. **Quick Start** - Get going ASAP
5. **Detailed Guide** - Deep dive
6. **Examples** - Real-world usage
7. **Troubleshooting** - Common issues
8. **References** - Links and resources

## Writing Tips

### Bad Example
```markdown
# Stuff

The thing does things. You need to configure it.
Configure with config file.
It has options: a, b, c.
```

### Good Example
```markdown
# Application Configuration

## Overview
This application requires configuration before first run.

## Quick Start
1. Copy `config.example.yml` to `config.yml`
2. Edit the values
3. Start the application

## Configuration Options

### Database (Required)
Connection string to database

Example:
\`\`\`yaml
database:
  host: localhost
  port: 5432
\`\`\`
```

## Formatting Tips

- **Use code blocks** for commands and code
- **Use tables** for comparisons
- **Use lists** for procedures
- **Use headings** for navigation
- **Use emphasis** sparingly (bold important terms)
- **Link liberally** to related docs
- **Update consistently** with code changes

## README Essentials

```markdown
# Project Name
Brief description

## Features
- Feature 1
- Feature 2

## Quick Start
Steps to get running

## Documentation
[Link to full docs]

## Contributing
How to contribute

## License
MIT
```
