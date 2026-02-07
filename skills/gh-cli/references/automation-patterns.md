# GitHub CLI Scripting

## Automation Examples

### Auto-label Issues

```bash
#!/bin/bash
# Label all open issues with 10+ days without activity

DAYS=10
LABELS="stale"

for issue in $(gh issue list --state open --json number -q '.[].number'); do
    updated=$(gh issue view $issue --json updatedAt -q '.updatedAt')
    days_old=$(($(date +%s) - $(date -d "$updated" +%s))) / 86400)
    
    if [ "$days_old" -gt "$DAYS" ]; then
        gh issue edit $issue --add-label "$LABELS"
        echo "Labeled issue #$issue as $LABELS"
    fi
done
```

### Auto-close Duplicate Issues

```bash
gh issue list --state open --label "duplicate" \
  --json number,body | \
  jq -r '.[] | select(.body | contains("Duplicate of")) | .number' | \
  while read issue; do
    gh issue close $issue
  done
```

### Bulk Update PRs

```bash
# Add reviewers to all open PRs
gh pr list --state open --json number -q '.[].number' | \
  while read pr; do
    gh pr edit $pr --add-reviewer @user1,@user2
  done
```

### Auto-merge Stale PRs

```bash
# Merge PRs older than 30 days with approvals
for pr in $(gh pr list --state open --json number -q '.[].number'); do
    reviews=$(gh pr view $pr --json reviews -q '.reviews | length')
    if [ "$reviews" -gt 0 ]; then
        gh pr merge $pr --squash
    fi
done
```
