# Dev Skills Collection

Comprehensive AI skills collection for developer productivity - **40+ powerful tools** for testing, CI/CD, DevOps, infrastructure, databases, version control, and utilities.

> Perfect for building, deploying, and managing applications with AI-powered assistance across Claude, Cursor, Windsurf, Aider, Continue, and Cline.

## Quick Start

### Install a Specific Skill

```bash
# Copy a specific skill to your project
cp -r node_modules/@1mangesh1/dev-skills-collection/skills/jest-vitest ./my-project/.agents/skills/

# Or use npx to access skills
npx @1mangesh1/dev-skills-collection
```

### Install via NPM

```bash
npm install @1mangesh1/dev-skills-collection
# or
yarn add @1mangesh1/dev-skills-collection
# or
pnpm add @1mangesh1/dev-skills-collection
```

## Available Skills (41 Total)

### Testing (2 skills)
- **jest-vitest** - Jest and Vitest testing frameworks
- **pytest** - Python pytest testing framework

### CI/CD (1 skill)
- **github-actions** - GitHub Actions workflows and CI/CD

### Infrastructure (8 skills)
- **aws-cli** - AWS CLI commands and infrastructure management
- **kubernetes** - Kubernetes and container orchestration
- **nginx** - Nginx web server configuration
- **redis** - Redis database and caching
- **sql-migrations** - Database migrations and SQL best practices
- **ssh-config** - SSH configuration and key management
- **terraform** - Terraform infrastructure as code

### Developer Tools (13 skills)
- **api-design** - Design RESTful and GraphQL APIs
- **curl-http** - cURL and HTTP client commands
- **gh-cli** - GitHub CLI commands and workflows
- **git-advanced** - Advanced Git workflows and commands
- **git-emoji** - Emoji conventions for Git commits
- **git-hooks** - Git hooks and automation
- **graphql** - GraphQL query language and APIs
- **lint-format** - Code linting and formatting tools
- **npm-scripts** - NPM scripts and task automation
- **python-env** - Python virtual environments and package management
- **code-review** - Code review checklists and best practices
- **env-debug** - Debug environment variables and configurations
- **mcp-setup** - Model Context Protocol setup and configuration

### Utilities (15 skills)
- **ascii-art** - Create and manipulate ASCII art
- **changelog** - Generate and manage changelog files
- **color** - Color manipulation and palette tools
- **cron** - Cron job scheduling and syntax
- **dotfiles** - Manage and configure dotfiles
- **http-status** - HTTP status codes reference
- **jq-yq** - JSON and YAML processing
- **makefile** - Makefile syntax and build automation
- **markdown** - Markdown syntax and documentation
- **one-liners** - Useful command-line one-liners
- **placeholder-data** - Generate placeholder and mock data
- **regex** - Regular expressions and pattern matching
- **shortcuts** - Keyboard shortcuts and productivity tips
- **tmux** - Tmux terminal multiplexer
- **vim-motions** - Vim motions and keyboard shortcuts

### Security (2 skills)
- **dependency-audit** - Audit and manage project dependencies
- **secret-scanner** - Detect and scan for secrets in code

### Meta (1 skill)
- **skill-creator** - Framework for creating new skills

## Skills by Category

| Category | Count | Skills |
|----------|-------|--------|
| Testing | 2 | jest-vitest, pytest |
| CI/CD | 1 | github-actions |
| Infrastructure | 8 | aws-cli, kubernetes, nginx, redis, sql-migrations, ssh-config, terraform |
| Developer Tools | 13 | api-design, curl-http, gh-cli, git-advanced, git-emoji, git-hooks, graphql, lint-format, npm-scripts, python-env, code-review, env-debug, mcp-setup |
| Utilities | 15 | ascii-art, changelog, color, cron, dotfiles, http-status, jq-yq, makefile, markdown, one-liners, placeholder-data, regex, shortcuts, tmux, vim-motions |
| Security | 2 | dependency-audit, secret-scanner |
| Meta | 1 | skill-creator |

## Agent Compatibility

All skills are designed for compatibility with modern AI coding agents:

| Agent | Status | Notes |
|-------|--------|-------|
| Claude Code | ✅ Supported | Full MCP integration |
| Cursor | ✅ Supported | Works with all skills |
| Windsurf | ✅ Supported | Full compatibility |
| Aider | ✅ Supported | Works with core skills |
| Continue | ✅ Supported | Extended capabilities |
| Cline | ✅ Supported | Full feature support |

## Use Cases

### Local Development
- **Testing & Quality**: Use jest-vitest or pytest for testing strategies
- **Git Workflows**: Leverage git-advanced and git-emoji for professional commits
- **Debugging**: Use env-debug and one-liners for environment troubleshooting

### DevOps & Infrastructure
- **Cloud Deployment**: Use aws-cli, terraform, kubernetes for IaC
- **Configuration**: Use nginx, ssh-config, redis for infrastructure setup
- **Migrations**: Use sql-migrations for database changes

### Quick References
- **HTTP Status**: Quick lookup for status codes
- **Regex Patterns**: Common regex patterns and syntax
- **Color Theory**: Color manipulation and palette generation
- **Command Cheatsheets**: curl-http, jq-yq, tmux, vim-motions

## Installation Methods

### NPM / Yarn / PNPM
```bash
npm install @1mangesh1/dev-skills-collection
yarn add @1mangesh1/dev-skills-collection
pnpm add @1mangesh1/dev-skills-collection
```

### Direct Git Clone
```bash
git clone https://github.com/1Mangesh1/dev-skills-collection.git
cd dev-skills-collection
npm install
```

### Via CDN (for browser-based tools)
Skills can be accessed through GitHub's raw content:
```
https://raw.githubusercontent.com/1Mangesh1/dev-skills-collection/main/skills/{skill-name}/SKILL.md
```

## Contributing

We welcome contributions! Each skill should:
- Include a comprehensive `SKILL.md` with examples and use cases
- Have organized `references/` directory with supplementary docs
- Include relevant metadata in package.json

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Support

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/1Mangesh1/dev-skills-collection/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/1Mangesh1/dev-skills-collection/discussions)
- **Documentation**: Full docs available in each skill's SKILL.md

## License

MIT - see [LICENSE](LICENSE) file for details

---

**Built for modern developers with AI-powered coding assistants** 🚀
