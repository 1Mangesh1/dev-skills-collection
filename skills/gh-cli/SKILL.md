---
name: gh-cli
description: GitHub CLI (gh) reference for authentication, repos, pull requests, issues, code review, Actions, releases, gists, API calls, search, aliases, extensions, codespaces, and configuration. Use when the user asks to create or manage PRs, issues, releases, workflows, gists, repos, or any GitHub operation from the terminal.
---

# GitHub CLI Reference

Complete reference for `gh`, the official GitHub CLI.

## Authentication

```bash
gh auth login                            # Interactive login (browser or token)
gh auth login --hostname enterprise.example.com  # GitHub Enterprise
gh auth status                           # Check current auth
gh auth token                            # Print current token
gh auth refresh --scopes workflow        # Add scopes
gh auth logout
```

## Repository Operations

```bash
gh repo clone owner/repo
gh repo clone owner/repo ./target-dir
gh repo create my-repo --public --clone
gh repo create my-repo --private --source=. --push
gh repo fork owner/repo --clone
gh repo view owner/repo                  # Terminal view
gh repo view owner/repo --web            # Open in browser
gh repo list owner --limit 50
gh repo archive owner/repo
gh repo delete owner/repo --yes
gh repo rename new-name
```

## Pull Requests

### Create

```bash
gh pr create --title "Add caching" --body "Reduces DB calls by 40%"
gh pr create --fill                      # Title/body from commits
gh pr create --draft
gh pr create --base develop --reviewer alice,bob --label enhancement
gh pr create --web                       # Open form in browser
```

### List, View, Checkout

```bash
gh pr list
gh pr list --state all --author @me
gh pr list --label "needs-review"
gh pr view 123
gh pr view 123 --web
gh pr diff 123
gh pr view 123 --json title,state,reviews,mergeable
gh pr checkout 123
```

### Review

```bash
gh pr review 123 --approve
gh pr review 123 --request-changes --body "Retry logic needs backoff"
gh pr review 123 --comment --body "Minor nits inline"
```

### Merge and Close

```bash
gh pr merge 123 --squash --delete-branch
gh pr merge 123 --merge                  # Merge commit
gh pr merge 123 --rebase --delete-branch
gh pr merge 123 --auto --squash          # Auto-merge when checks pass
gh pr close 123 --comment "Superseded by #456"
gh pr reopen 123
```

## Issues

### Create and Edit

```bash
gh issue create --title "Login timeout" --body "Details"
gh issue create --label bug,urgent --assignee @me
gh issue create --template bug_report.md
gh issue edit 456 --title "New title" --add-label priority:high
gh issue edit 456 --add-assignee alice --remove-assignee bob
gh issue transfer 456 owner/other-repo
```

### List and View

```bash
gh issue list
gh issue list --label "bug" --state open
gh issue list --assignee @me
gh issue list --search "timeout in:title"
gh issue view 456
gh issue view 456 --web
gh issue view 456 --json title,state,labels,assignees
```

### Close and Manage

```bash
gh issue close 456 --comment "Fixed in #123"
gh issue reopen 456
gh issue pin 456
gh issue unpin 456
gh issue edit 456 --add-label "wontfix" --remove-label "bug"
```

## GitHub Actions

```bash
gh run list
gh run list --workflow build.yml
gh run view 12345
gh run view 12345 --log
gh run view 12345 --log-failed
gh run watch 12345                       # Live progress
gh run rerun 12345 --failed
gh run cancel 12345
gh run download 12345                    # Download artifacts
gh workflow run deploy.yml -f environment=production -f version=1.2.3
gh workflow list
gh workflow disable build.yml
gh workflow enable build.yml
gh workflow view build.yml
```

## Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --notes "Initial release"
gh release create v1.0.0 --generate-notes
gh release create v1.0.0 --draft --generate-notes
gh release create v2.0.0-rc.1 --prerelease --generate-notes
gh release create v1.0.0 ./dist/*.tar.gz ./dist/*.zip  # With assets
gh release upload v1.0.0 ./build/artifact.zip           # Add asset later
gh release list
gh release view v1.0.0
gh release delete v1.0.0 --yes
gh release delete v1.0.0 --yes --cleanup-tag
```

## Gists

```bash
gh gist create file.txt --public
gh gist create file.txt --desc "SQL query for monthly report"
gh gist create main.py utils.py --desc "Helper scripts"
echo "hello" | gh gist create --filename greeting.txt
gh gist list --limit 20
gh gist view <gist-id>
gh gist view <gist-id> --web
gh gist edit <gist-id>
gh gist edit <gist-id> --add newfile.txt
gh gist clone <gist-id>
gh gist delete <gist-id>
```

## API Calls

Use `gh api` for any REST or GraphQL endpoint not covered by built-in commands.

```bash
# REST
gh api repos/owner/repo/issues
gh api repos/owner/repo/issues -f title="Bug" -f body="Details"
gh api repos/owner/repo/issues/42 -X PATCH -f state="closed"
gh api repos/owner/repo/issues/42/labels/bug -X DELETE
gh api repos/owner/repo/issues --paginate
gh api repos/owner/repo/contributors --jq '.[].login'
gh api repos/{owner}/{repo}/pulls/123/comments

# GraphQL
gh api graphql -f query='{ viewer { login } }'
gh api graphql -f query='
  query { viewer { repositories(first:5, orderBy:{field:UPDATED_AT, direction:DESC}) {
    nodes { name }
  }}}
'
```

## Search

```bash
gh search repos "language:rust stars:>1000"
gh search issues "label:bug language:go is:open"
gh search prs "review:approved is:merged author:alice"
gh search code "fmt.Errorf" --language go
gh search commits "fix typo" --author alice
gh search repos "topic:cli" --json fullName,description --limit 10
```

## Aliases

```bash
gh alias set pv 'pr view'
gh alias set co 'pr checkout'
gh alias set mypr 'pr list --author @me --state open'
gh alias set --shell igrep 'gh issue list --label "$1"'
gh alias list
gh alias delete pv
# Usage
gh pv 123
gh mypr
```

## Extensions

```bash
gh extension list
gh extension browse
gh extension install owner/gh-extension-name
gh extension upgrade owner/gh-extension-name
gh extension upgrade --all
gh extension remove owner/gh-extension-name
gh extension create my-extension          # Scaffold new extension
```

## Codespaces

```bash
gh codespace create --repo owner/repo
gh codespace create --repo owner/repo --machine largePremiumLinux
gh codespace list
gh codespace ssh --codespace <name>
gh codespace code --codespace <name>     # Open in VS Code
gh codespace stop --codespace <name>
gh codespace delete --codespace <name>
gh codespace ports forward 8080:8080 --codespace <name>
```

## Configuration and Environment

```bash
gh config set editor vim
gh config set git_protocol ssh
gh config list
```

| Variable              | Purpose                                          |
|-----------------------|--------------------------------------------------|
| `GH_TOKEN`            | Auth token (overrides stored credentials)        |
| `GITHUB_TOKEN`        | Fallback token (common in CI)                    |
| `GH_REPO`             | Override repository context (owner/repo)         |
| `GH_HOST`             | Default GitHub host (for Enterprise)             |
| `GH_ENTERPRISE_TOKEN` | Auth token for GitHub Enterprise                 |
| `NO_COLOR`            | Disable color output                             |

## JSON Output and Scripting

```bash
gh pr list --json number,title,author
gh pr list --json number,title --jq '.[] | "#\(.number) \(.title)"'
gh pr list --json number,title --template '{{range .}}#{{.number}} {{.title}}{{"\n"}}{{end}}'
gh issue list --json number --jq '.[].number' | xargs -I{} gh issue view {}
```

## Common Workflows

### PR from Branch

```bash
git checkout -b feature/caching
# make changes
git add -A && git commit -m "Add caching layer"
git push -u origin feature/caching
gh pr create --fill --reviewer alice
```

### Review Cycle

```bash
# Reviewer checks out and reviews
gh pr checkout 123
gh pr review 123 --request-changes --body "Needs error handling"
# Author pushes fixes, reviewer re-reviews
gh pr checkout 123 && git pull
gh pr review 123 --approve
gh pr merge 123 --squash --delete-branch
```

### Release Workflow

```bash
git tag v1.2.0 && git push origin v1.2.0
gh release create v1.2.0 --generate-notes
gh release upload v1.2.0 ./dist/*.tar.gz
```

### Triage Issues

```bash
gh issue list --label "bug" --assignee ""
gh issue edit 456 --add-assignee @me --add-label "priority:high"
gh issue close 789 --comment "Duplicate of #456"
```
