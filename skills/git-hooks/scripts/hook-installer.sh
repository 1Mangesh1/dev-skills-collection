#!/usr/bin/env bash
# Git Hooks Manager
# Set up and manage git hooks

install_pre_commit_hook() {
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to run linting and tests

echo "Running pre-commit checks..."

# Lint
npm run lint
if [ $? -ne 0 ]; then
    echo "❌ Linting failed"
    exit 1
fi

# Tests
npm test
if [ $? -ne 0 ]; then
    echo "❌ Tests failed"
    exit 1
fi

echo "✓ Pre-commit checks passed"
EOF

    chmod +x .git/hooks/pre-commit
    echo "Pre-commit hook installed"
}

install_commit_msg_hook() {
    cat > .git/hooks/commit-msg << 'EOF'
#!/bin/bash
# Enforce conventional commits
# Format: type(scope): subject

msg=$(cat "$1")

if ! echo "$msg" | grep -E "^(feat|fix|docs|style|refactor|test|chore)(\(.+\))?:"; then
    echo "❌ Commit message must follow conventional commits"
    echo "Format: type(scope): subject"
    echo "Example: feat(auth): add JWT support"
    exit 1
fi
EOF

    chmod +x .git/hooks/commit-msg
    echo "Commit message hook installed"
}

# Install hooks
install_pre_commit_hook
install_commit_msg_hook
