# Contributing to Dev Skills Collection

Thank you for your interest in contributing! This guide will help you get started.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/dev-skills-collection.git
   cd dev-skills-collection
   ```
3. **Create a feature branch**:
   ```bash
   git checkout -b feat/your-skill-name
   ```

## Adding a New Skill

### Directory Structure

Each skill should follow this structure:

```
skills/your-skill/
├── SKILL.md                    # Main skill documentation
├── references/
│   ├── guide-1.md             # Supporting documentation
│   └── guide-2.md
└── scripts/                     # Optional: automation scripts
    └── example.sh
```

### SKILL.md Template

```markdown
# Your Skill Name

Brief description of what this skill does.

## Quick Start

Show the most common use cases with examples.

## Advanced Usage

Cover advanced patterns and best practices.

## References

- [Example Reference](references/guide-1.md)

## Tools & Dependencies

List any required tools or dependencies.

## Tips & Tricks

Share expert techniques and gotchas.
```

### Metadata

Update `package.json` to include your skill:

```json
{
  "skillCategories": {
    "category-name": ["your-skill", ...]
  }
}
```

## Skill Categories

- **testing**: jest-vitest, pytest
- **ci-cd**: github-actions
- **infrastructure**: aws-cli, kubernetes, terraform, etc.
- **developer-tools**: git, linting, formatting, API design
- **utilities**: one-liners, regex, tmux, vim
- **security**: authentication, secrets scanning

## Code Style

- Use clear, concise language
- Include practical examples
- Link to official documentation
- Keep files organized in `references/` directory

## Agent Compatibility

Ensure your skill works with:
- ✅ Claude Code
- ✅ Cursor
- ✅ Windsurf
- ✅ Aider
- ✅ Continue
- ✅ Cline

Add your skill to the `agents` array in `package.json`:

```json
"agents": ["claude", "cursor", "windsurf", "aider", "continue", "cline"]
```

## Testing Your Skill

1. **Validate SKILL.md**: Check for broken links and formatting
   ```bash
   npm run validate:skills
   ```

2. **Test in agents**: Load the skill in Claude/Cursor and verify it works

3. **Check references**: Ensure all referenced files exist

## Pull Request Process

1. **Write descriptive commit messages**:
   ```
   feat: add kubernetes deployment skill
   docs: add terraform best practices
   chore: update skill category
   ```

2. **Update package.json** with your new skill entry

3. **Submit PR** with:
   - Clear description of skill
   - Use case/examples
   - Any dependencies required
   - Links to official docs

4. **Address feedback** from maintainers

## Skill Quality Checklist

Before submitting your PR, verify:

- [ ] SKILL.md is well-formatted and readable
- [ ] All code examples are tested and working
- [ ] References are comprehensive and linked
- [ ] Skill is added to package.json with correct category
- [ ] Agent compatibility is accurate
- [ ] No broken links or missing files
- [ ] Grammar and spelling are correct

## Naming Conventions

- Skill folders: `kebab-case` (e.g., `git-advanced`)
- Files: `kebab-case.md` (e.g., `best-practices.md`)
- Skills in package.json: `kebab-case`

## Questions?

- Open an issue for feature requests
- Discuss ideas in GitHub Discussions
- Check existing skills for examples

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Happy contributing! 🚀
