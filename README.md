# Dev Skills Collection

78 skills for AI coding agents — testing, CI/CD, DevOps, infrastructure, databases, version control, and general utilities. Works with Claude, Cursor, Windsurf, Aider, Continue, and Cline.

## What's in here

- Testing and QA (Jest, Vitest, Pytest)
- DevOps and infrastructure (AWS, Kubernetes, Terraform, Docker, Nginx, PostgreSQL)
- Developer tools (Git, GitHub Actions, API design, sed/awk, xargs)
- Security and networking (secret scanning, OpenSSL/TLS, DNS debugging)
- Media and files (ffmpeg, ImageMagick, tar/compression)
- Daily utilities (port/process management, encoding, date/time, package managers)
- AI and modern tooling (agents, Ollama, vector databases, Bun, Turborepo)
- Frontend (Tailwind CSS) and backend (Prisma, gRPC, Cloudflare Workers)
- Observability (OpenTelemetry)
- 100+ reference guides
- Compatible with most AI coding agents

## How it works

You ask your AI agent a question. It matches your request to a skill, loads the SKILL.md and reference docs, and uses that context to help.

## Installation

### With the skills CLI

```bash
npx skills add 1Mangesh1/dev-skills-collection
```

This downloads all 68 skills and configures them for your AI agent.

After installing, just ask your agent what you need:

```
"How do I use Jest?"             → jest-vitest skill activates
"Setup AWS infrastructure"       → aws-cli + terraform skills activate
"Improve git workflow"           → git-hooks + git-emoji skills activate
"Scan for secrets"               → secret-scanner skill activates
```

To check what you have installed:

```bash
npx skills list
npx skills view jest-vitest
```

### With git clone

```bash
git clone https://github.com/1Mangesh1/dev-skills-collection.git
cd dev-skills-collection
cp -r skills/ ~/.claude/skills/
```

## Quick start examples

Ask "Help me setup Jest and Vitest testing." The jest-vitest skill loads and walks you through config and writing your first tests.

Ask "Setup AWS infrastructure with Terraform." The aws-cli and terraform skills load together.

Ask "Setup git hooks and commit conventions." Loads git-hooks, git-emoji, and git-advanced. You get pre-commit hooks, semantic commits, and Actions integration.

Ask "Help me manage database migrations." The sql-migrations skill loads with rollback procedures and version control patterns.

## All 78 skills

### Testing (2)
- jest-vitest — Jest and Vitest testing frameworks
- pytest — Python pytest framework

### CI/CD (1)
- github-actions — GitHub Actions workflows

### Infrastructure (11)
- aws-cli — AWS CLI commands and infrastructure
- cloudflare-workers — edge computing, KV, D1, R2, Workers AI
- docker-compose — multi-container local dev and production stacks
- kubernetes — container orchestration
- nginx — web server configuration
- postgres — PostgreSQL queries, admin, and performance tuning
- redis — caching and data store
- sql-migrations — database migrations and SQL
- sqlite — embedded database and CLI
- ssh-config — SSH configuration and keys
- terraform — infrastructure as code

### Developer tools (19)
- api-design — RESTful and GraphQL API design
- bun-runtime — fast JS/TS runtime, bundler, test runner
- code-review — code review checklists
- curl-http — cURL and HTTP clients
- env-debug — environment variable debugging
- gh-cli — GitHub CLI
- git-advanced — advanced Git workflows
- git-emoji — emoji commit conventions
- git-hooks — Git hooks and automation
- git-worktree — parallel branch work without stashing
- graphql — GraphQL queries and APIs
- grpc-protobuf — gRPC and Protocol Buffers
- lint-format — linting and formatting
- mcp-setup — Model Context Protocol setup
- npm-scripts — NPM task automation
- prisma-orm — type-safe database ORM for TypeScript
- python-env — Python virtual environments
- sed-awk — text processing with sed and awk
- xargs-parallel — parallel execution and batch processing

### AI and ML (3)
- ai-agents — building autonomous AI agents, tool use, multi-agent patterns
- ollama — local LLM inference, model management, API integration
- vector-db — embeddings, semantic search, RAG pipelines

### Frontend (1)
- tailwind-css — utility-first CSS patterns and configuration

### Monorepo and build (1)
- turborepo — monorepo management, task orchestration, caching

### Observability (1)
- opentelemetry — distributed tracing, metrics, logging

### Utilities (22)
- ascii-art — ASCII art generation
- base64-encoding — base64, URL encoding, hex, hashing, JWT decode
- brew-apt — package managers (Homebrew, apt, dnf)
- changelog — changelog management
- color — color manipulation and palettes
- cron — cron job scheduling
- date-time-cli — timestamps, epoch, timezone conversion, date math
- dotfiles — dotfile management
- ffmpeg — video/audio conversion and processing
- http-status — HTTP status code reference
- imagemagick — image conversion, resize, crop, batch processing
- jq-yq — JSON and YAML processing
- makefile — Makefile syntax and builds
- markdown — Markdown syntax
- one-liners — command-line one-liners
- placeholder-data — mock data generation
- port-process — find port users, kill processes, resource management
- regex — regular expressions
- shortcuts — keyboard shortcuts
- tar-compression — archives and compression (tar, gzip, zip, zstd)
- tmux — terminal multiplexer
- vim-motions — Vim keyboard shortcuts

### Security and networking (4)
- dependency-audit — dependency auditing
- dns-network — DNS lookups, connectivity testing, latency diagnosis
- openssl-tls — certificates, TLS debugging, encryption
- secret-scanner — secret detection in code

### Meta (1)
- skill-creator — framework for creating new skills

## Agent compatibility

Tested with Claude Code, Cursor, Windsurf, Aider, Continue, and Cline. Each skill is a Markdown file, so anything that reads `.md` skills should work.

## Example workflows

**Shipping an app from scratch** — Combine jest-vitest (testing), github-actions (CI/CD), aws-cli + terraform (infrastructure), nginx (web server), and sql-migrations (database). Ask for each piece as you need it.

**Code quality audit** — Use dependency-audit to find vulnerable packages, secret-scanner to catch hardcoded credentials, lint-format for code standards, and git-hooks to automate the checks on every commit.

**Infrastructure at scale** — kubernetes, terraform, aws-cli, redis, and nginx work together. Ask about each one as you build out your stack.

## FAQ

**How do I find the right skill?** Just describe what you're trying to do. Your agent picks the matching skill automatically.

**Can I customize these?** Fork the repo and edit the SKILL.md files.

**Do skills need extra setup?** Most work immediately. A few (aws-cli, terraform, kubernetes) need the underlying CLI tools installed first — the skill docs explain what's needed.

**How do I add a new skill?** Create a directory under `skills/` with a SKILL.md, a references/ folder, and optionally examples/ or scripts/. See the skill-creator skill for the template.

## Troubleshooting

If a skill isn't loading, check that the SKILL.md is in the right directory and has activation phrases your agent can match.

If commands fail, make sure the underlying tools are installed (`aws`, `kubectl`, `terraform`, etc.) and versions match what the skill expects. Each skill's references/ folder has setup details.

Some examples need environment setup (AWS credentials, a running cluster, etc.). Check prerequisites in the skill's SKILL.md.

Missing something? [Open an issue](https://github.com/1Mangesh1/dev-skills-collection/issues).

## Links

- [Issues](https://github.com/1Mangesh1/dev-skills-collection/issues)
- [Discussions](https://github.com/1Mangesh1/dev-skills-collection/discussions)
- Pull requests welcome

## License

MIT — see [LICENSE](LICENSE).
