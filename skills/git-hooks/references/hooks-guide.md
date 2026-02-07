# Git Hooks Best Practices

## Common Hooks

### pre-commit
Run before commit (lint, format, test):
```bash
.git/hooks/pre-commit
```

### commit-msg
Validate commit message format:
```bash
.git/hooks/commit-msg
```

### pre-push
Run before pushing (build, full test):
```bash
.git/hooks/pre-push
```

### post-checkout
Run after switching branches:
```bash
.git/hooks/post-checkout
```

## Using husky (Recommended)

Instead of manual hook scripts, use husky:

```bash
npm install husky --save-dev
npx husky install

# Create hook
npx husky add .husky/pre-commit "npm run lint"
npx husky add .husky/pre-push "npm test"
```

## Conventional Commits with commitlint

Enforce commit message format:

```bash
npm install commitlint @commitlint/config-conventional --save-dev
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js

# Add hook
npx husky add .husky/commit-msg 'npx --no -- commitlint --edit "$1"'
```

Valid commits:
- `feat: add login page`
- `fix: resolve memory leak`
- `docs: update README`
- `refactor: simplify logic`
- `test: add unit tests`

## Preventing Disaster

```bash
# Prevent committing secrets
npm install detect-secrets --save-dev

# Or use git-secrets
git secrets --install
git secrets --register-aws
```

## Tips

1. Keep hooks fast (< 5 seconds)
2. Make them optional with `--no-verify` if needed
3. Document what each hook does
4. Share hooks with team via repo
