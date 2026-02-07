# GitHub CLI Complete Guide

## Installation

```bash
# macOS
brew install gh

# Ubuntu/Debian
curl https://cli.github.com/packages.key | sudo apt-key add -
sudo apt update && sudo apt install gh

# Auth
gh auth login
```

## Common Commands

### Issues

```bash
# List issues
gh issue list --state open
gh issue list --assignee me
gh issue list --label bug

# Create issue
gh issue create --title "Bug: Login broken"

# View issue
gh issue view 123

# Comment on issue
gh issue comment 123 -b "Fixed in #456"
```

### Pull Requests

```bash
# List PRs
gh pr list --state open
gh pr list --reviewer me

# Create PR
gh pr create --title "feat: dark mode" --body "Implements dark theme"

# View PR
gh pr view 123

# Check PR
gh pr checks 123

# Review PR
gh pr review 123 --approve
gh pr review 123 --request-changes

# Merge PR
gh pr merge 123 --squash --delete-branch
```

### Repositories

```bash
# List repos
gh repo list username

# Clone repo
gh repo clone owner/repo

# View repo
gh repo view owner/repo

# Create repo
gh repo create repo-name --public
```

### Releases

```bash
# List releases
gh release list

# Create release
gh release create v1.0.0 --title "Version 1.0.0"

# Upload asset
gh release upload v1.0.0 file.tar.gz

# View release
gh release view v1.0.0
```

### Gists

```bash
# Create gist
gh gist create file.txt

# List gists
gh gist list

# View gist
gh gist view gist_id
```

## Advanced

### Using Templates

```bash
# Custom output
gh pr list --json number,title,author \
  --template '{{range .}}#{{.number}} - {{.title}}{{"\n"}}{{end}}'

# With conditions
gh pr list --state merged \
  --json mergedAt,title \
  --template '{{range .}}{{.mergedAt}} - {{.title}}{{"\n"}}{{end}}'
```

### Workflows

```bash
# List workflows
gh workflow list

# Run workflow
gh workflow run workflow.yml --ref main

# View runs
gh run list
gh run view run_id
```
