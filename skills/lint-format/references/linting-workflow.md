# lint-staged for Efficient Linting

Only lint changed files before commit:

```bash
npm install --save-dev lint-staged
```

`.husky/pre-commit`:
```bash
npx lint-staged
```

`package.json`:
```json
{
  "lint-staged": {
    "*.js": "eslint --fix",
    "*.json": "prettier --write",
    "*.md": "prettier --write"
  }
}
```

Benefits:
- Faster pre-commit checks
- Only checks modified files
- Auto-formats on commit

## Commit Message Linting

Enforce consistent message format:

```bash
npm install --save-dev commitlint @commitlint/config-conventional
```

`.commitlintrc.json`:
```json
{
  "extends": ["@commitlint/config-conventional"]
}
```

Valid:
- `feat: add login`
- `fix: resolve bug`
- `docs: update README`
- `refactor: simplify logic`

Invalid:
- `added feature` (lowercase, no type)
- `WIP` (too short)
