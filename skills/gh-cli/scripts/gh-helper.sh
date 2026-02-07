#!/usr/bin/env bash
# GitHub CLI Helper
# Common gh commands for repository management

create_issue() {
    local title="$1"
    local body="$2"
    
    echo "=== Creating Issue ==="
    gh issue create \
        --title "$title" \
        --body "$body" \
        --assignee "me"
}

list_prs() {
    echo "=== Pull Requests ==="
    gh pr list \
        --state open \
        --limit 20 \
        --json title,number,author,updatedAt \
        --template '{{range .}}{{.number}}: {{.title}} ({{.author.login}}){{"\n"}}{{end}}'
}

merge_pr() {
    local pr_number="$1"
    
    echo "Merging PR #$pr_number"
    gh pr merge "$pr_number" \
        --squash \
        --delete-branch
}

# Usage
create_issue "Bug: Login broken" "Users cannot log in after password reset"
list_prs
