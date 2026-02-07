#!/usr/bin/env bash
# Git Advanced Workflows
# Interactive rebase and history management

interactive_rebase() {
    local branch="$1"
    
    echo "=== Interactive Rebase ==="
    echo "Rebasing current branch onto $branch"
    echo ""
    echo "This will open an editor where you can:"
    echo "  pick   - use commit"
    echo "  reword - use commit, but edit message"
    echo "  squash - use commit, but meld into previous"
    echo "  fixup  - like squash, but discard log"
    echo ""
    
    git rebase -i "$branch"
}

cherry_pick_commit() {
    local commit="$1"
    
    echo "Applying commit $commit to current branch"
    git cherry-pick "$commit"
    
    if [ $? -eq 0 ]; then
        echo "✓ Commit applied successfully"
    else
        echo "✗ Conflict during cherry-pick"
        echo "Resolve conflicts and run: git cherry-pick --continue"
    fi
}

squash_commits() {
    echo "Squashing last 5 commits into one"
    git rebase -i HEAD~5
}

# Usage
interactive_rebase "main"
