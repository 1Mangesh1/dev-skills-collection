# Dev Skills Collection

Comprehensive AI skills collection for developer productivity - **41 powerful tools** for testing, CI/CD, DevOps, infrastructure, databases, version control, and utilities.

> Perfect for building, deploying, and managing applications with AI-powered assistance across Claude, Cursor, Windsurf, Aider, Continue, and Cline.

## ✨ Key Features

- 🧪 **Testing & QA** - Jest, Vitest, Pytest with best practices
- 🚀 **DevOps & Infrastructure** - AWS, Kubernetes, Terraform, Docker, Nginx
- 🔧 **Developer Tools** - Git workflows, GitHub Actions, API design, GraphQL
- 🔐 **Security** - Secret scanning, dependency audits, vulnerability detection
- 📚 **References** - 100+ comprehensive guides and patterns
- 🤖 **AI-Native** - Works with Claude, Cursor, Windsurf, Cline, and more
- 📦 **NPM Install** - Easy installation and integration
- 🎯 **Production-Ready** - Used across real-world projects

## How It Works

```
┌──────────────────────────────────────────────────┐
│  AI Agent (Claude, Cursor, Windsurf, Cline)    │
└──────────────────────┬───────────────────────────┘
                       │ Ask for development help
                       ▼
        ┌─────────────────────────────────┐
        │  Skill Activation Triggers      │
        │  e.g. "help with testing",      │
        │  "setup git hooks", "check AWS" │
        └─────────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │  Skill Selection & Loading      │
        │  - Parse context                │
        │  - Load relevant SKILL.md       │
        │  - Load supporting scripts      │
        └─────────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │  Provide Developer Guidance     │
        │  - Best practices               │
        │  - Code examples                │
        │  - Execution patterns           │
        └─────────────────────────────────┘
                       │
                       ▼
        ┌─────────────────────────────────┐
        │  AI-Assisted Implementation     │
        │  - Generate code                │
        │  - Review patterns              │
        │  - Troubleshoot issues          │
        └─────────────────────────────────┘
```

## Installation

### Option 1: NPM Install (Recommended)

```bash
npm install @1mangesh1/dev-skills-collection
yarn add @1mangesh1/dev-skills-collection
pnpm add @1mangesh1/dev-skills-collection
```

### Option 2: Copy Individual Skills

```bash
# Copy a specific skill to your project
cp -r node_modules/@1mangesh1/dev-skills-collection/skills/jest-vitest ./.agents/skills/
```

### Option 3: Git Clone

```bash
git clone https://github.com/1Mangesh1/dev-skills-collection.git
cd dev-skills-collection
npm install
```

## Quick Start Examples

### Example 1: Setup Testing in Your Project

**Activation Phrase**: "Help me set up testing with Jest and Vitest"

```bash
# AI will suggest:
# 1. Copy jest-vitest skill to .agents/skills/
# 2. Review testing patterns in SKILL.md
# 3. Generate test files with examples
# 4. Setup testing scripts in package.json
```

**Result**: Your project now has:
- Testing framework configuration
- Example test cases
- CI/CD integration ready
- Best practices documented

### Example 2: Manage AWS Infrastructure

**Activation Phrase**: "Help me manage AWS resources with Terraform and AWS CLI"

```bash
# AI will provide:
# 1. AWS CLI command reference
# 2. Terraform infrastructure patterns
# 3. Security best practices
# 4. Example configurations
```

**Create infrastructure safely**:
```bash
# Load aws-cli skill for AWS commands
aws s3 ls
aws ec2 describe-instances

# Load terraform skill for IaC
terraform init
terraform plan
terraform apply
```

### Example 3: Git Workflow Setup

**Activation Phrase**: "Setup professional git hooks and commit conventions"

```bash
# AI will configure:
# 1. Pre-commit hooks from git-hooks skill
# 2. Commit emoji conventions from git-emoji skill
# 3. Advanced workflows from git-advanced skill
# 4. GitHub Actions from github-actions skill
```

**Professional commits**:
```bash
# With git-emoji skill
git commit -m "🎨 refactor: improve code structure"
git commit -m "✨ feat: add new authentication flow"
git commit -m "🐛 fix: resolve memory leak in cache"
```

### Example 4: Database Migration Management

**Activation Phrase**: "Help me manage database migrations safely"

```bash
# AI will provide:
# 1. sql-migrations best practices
# 2. Migration patterns and strategies
# 3. Rollback procedures
# 4. Version control integration
```

**Result**: Safe, traceable database changes with automated rollback capability

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

## Real-World Use Cases

### Scenario 1: Launch a Production-Ready Application

**Challenge**: Need new app with testing, CI/CD, and deployment

**Skills Used**: jest-vitest, github-actions, aws-cli, terraform, nginx, sql-migrations

**Workflow**:
1. "Setup testing framework" → jest-vitest skill provides configuration
2. "Create GitHub Actions workflows" → github-actions skill enables CI/CD
3. "Deploy to AWS" → aws-cli + terraform skills handle infrastructure
4. "Configure web server" → nginx skill sets up reverse proxy
5. "Manage databases" → sql-migrations skill tracks schema changes

**Result**: Complete, production-ready application with automated testing and deployment

### Scenario 2: Improve Code Quality & Security

**Challenge**: Audit dependencies, detect secrets, improve code standards

**Skills Used**: dependency-audit, secret-scanner, lint-format, code-review, git-hooks

**Workflow**:
1. "Audit project dependencies" → dependency-audit finds vulnerabilities
2. "Scan for secrets" → secret-scanner detects hardcoded credentials
3. "Setup code linting" → lint-format enforces standards
4. "Create code review workflow" → code-review provides checklists
5. "Automate checks" → git-hooks prevents bad commits

**Result**: Secure, maintainable codebase with automated quality gates

### Scenario 3: Master Developer Workflows

**Challenge**: Team efficiency - need professional git, terminals, editors

**Skills Used**: git-advanced, git-hooks, tmux, vim-motions, shortcuts

**Workflow**:
1. "Advanced git workflows" → git-advanced teaches collaboration patterns
2. "Optimize terminal usage" → tmux skill boosts productivity
3. "Master Vim" → vim-motions unlock editor power
4. "Quick shortcuts" → shortcuts discover platform-specific tips

**Result**: Team working at peak efficiency with professional workflows

### Scenario 4: Infrastructure Management at Scale

**Challenge**: Multi-cloud infrastructure with Kubernetes, monitoring, logging

**Skills Used**: kubernetes, terraform, aws-cli, nginx, redis, python-env

**Workflow**:
1. "Setup Kubernetes cluster" → kubernetes skill provides patterns
2. "Infrastructure as Code" → terraform skill manages resources
3. "AWS cloud" → aws-cli skill handles cloud operations
4. "Caching layer" → redis skill optimizes performance
5. "Web server" → nginx skill handles routing

**Result**: Scalable, resilient infrastructure managed through code

## Skill Activation Phrases (Quick Reference)

### Testing & Quality Assurance
- "How do I use Jest?" → **jest-vitest** skill
- "Setup pytest for Python testing" → **pytest** skill
- "Code review best practices" → **code-review** skill

### Infrastructure & DevOps
- "Help with AWS CLI" → **aws-cli** skill
- "Setup Kubernetes" → **kubernetes** skill
- "Terraform infrastructure" → **terraform** skill
- "Configure Nginx" → **nginx** skill
- "Redis caching patterns" → **redis** skill

### Git & Version Control
- "Advanced git workflows" → **git-advanced** skill
- "Setup git hooks" → **git-hooks** skill
- "Professional commit messages" → **git-emoji** skill
- "GitHub CLI commands" → **gh-cli** skill

### API & Integration
- "Design RESTful API" → **api-design** skill
- "GraphQL best practices" → **graphql** skill
- "cURL and HTTP commands" → **curl-http** skill

### Environment & Debugging
- "Debug environment variables" → **env-debug** skill
- "Python virtual environments" → **python-env** skill
- "Setup MCP server" → **mcp-setup** skill

### General Utilities
- "Regular expression patterns" → **regex** skill
- "Generate test data" → **placeholder-data** skill
- "JSON/YAML processing" → **jq-yq** skill
- "Tmux terminal multiplexer" → **tmux** skill
- "Vim keyboard shortcuts" → **vim-motions** skill

## FAQ

**Q: Can I use these skills with my AI agent?**
A: Yes! Skills work with Claude, Cursor, Windsurf, Aider, Continue, and Cline. Each skill is MCP-compatible and agent-agnostic.

**Q: How do I find the right skill for my task?**
A: Describe what you want to do (e.g., "setup testing", "manage databases", "improve git workflow"). Your AI agent will identify and load the appropriate skill automatically.

**Q: Can I customize skills for my team?**
A: Yes! Each skill includes SKILL.md for customization. Fork the repository and modify skills to match your team's standards.

**Q: Are there quality guarantees?**
A: All skills follow production standards with:
- Comprehensive documentation (SKILL.md)
- Reference guides (references/ directory)
- Practical examples and patterns
- Best practices and security considerations

**Q: How do I contribute new skills?**
A: Create a new directory under `skills/` with:
- SKILL.md (main skill documentation)
- references/ (supporting guides)
- examples/ or scripts/ (practical code)
See the skill-creator skill for the framework.

**Q: Do skills require configuration?**
A: Most skills work out of the box. Some (aws-cli, terraform, kubernetes) require tools installed on your system, which the skill documentation will guide you through.

## Troubleshooting

**Issue: Skill not showing up in agent**
- Ensure the skill's SKILL.md has clear activation phrases
- Check agent system prompts for skill integration
- Verify the skill is in the `/skills/` directory

**Issue: Command failures in skill execution**
- Verify required tools are installed (`aws`, `kubectl`, `terraform`, etc.)
- Check tool versions match skill requirements
- Review skill-specific setup in references/ directory

**Issue: Examples not working**
- Some examples require environment setup (AWS credentials, Kubernetes cluster, etc.)
- Read the "Prerequisites" section in each skill's SKILL.md
- Check references/ directory for detailed setup guides

**Issue: Need skill for specific use case**
- Search the Available Skills section
- Try different activation phrases with your AI agent
- Check Combined scenarios in Real-World Use Cases
- Request new skill on [GitHub Issues](https://github.com/1Mangesh1/dev-skills-collection/issues)

## Support & Community

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/1Mangesh1/dev-skills-collection/issues)
- **Discussions**: Join [GitHub Discussions](https://github.com/1Mangesh1/dev-skills-collection/discussions) for questions
- **Documentation**: Full documentation in each skill's SKILL.md
- **Contributing**: Pull requests welcomed! See contribution guidelines
- **Feedback**: Share your experience and suggest improvements

## License

MIT - see [LICENSE](LICENSE) file for details

---

**Built for modern developers with AI-powered coding assistants** 🚀
