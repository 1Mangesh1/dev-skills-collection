---
name: code-review
description: Code review checklists, PR review patterns, feedback techniques, and review automation. Use when user asks to "review this code", "code review checklist", "PR review template", "review best practices", "write review feedback", "review this PR", "how to give feedback on code", "PR too large", "split this PR", "review turnaround time", "automated code review", "CODEOWNERS", "pair review", "when to request changes", "code review tool", "review security", "design review", "performance review", "test coverage review", or any code review and feedback tasks.
---

# Code Review

Checklists, patterns, feedback techniques, and automation for effective code reviews.

---

## Review Checklist by Category

### Logic and Correctness
- [ ] Does the code do what the PR description says it does?
- [ ] Are edge cases handled (empty inputs, boundary values, concurrent access)?
- [ ] Are error conditions handled gracefully with appropriate error types?
- [ ] Are there off-by-one errors in loops, slices, or pagination?
- [ ] Are null/undefined/nil cases handled?
- [ ] Does the control flow match the intended behavior (early returns, fallthrough)?

### Security
- [ ] No hardcoded secrets, keys, tokens, or passwords
- [ ] Input validation on all user-supplied data (query params, body, headers)
- [ ] No SQL injection, XSS, or command injection vectors
- [ ] Authentication and authorization checks on every endpoint
- [ ] Sensitive data not logged, not in error messages, not exposed in responses
- [ ] CSRF protection on state-changing requests
- [ ] Rate limiting on sensitive endpoints (auth, password reset)

### Performance
- [ ] No N+1 database queries (queries inside loops)
- [ ] No memory leaks (event listeners, timers, subscriptions not cleaned up)
- [ ] Large datasets paginated, not loaded entirely into memory
- [ ] Expensive computations cached where appropriate
- [ ] No blocking operations on the main thread or event loop
- [ ] Database queries use indexes (check EXPLAIN plans for new queries)

### Readability and Maintainability
- [ ] Code is understandable without needing the author to explain it
- [ ] Functions have a single responsibility and a clear name
- [ ] No duplicated logic (DRY where it reduces coupling, not blindly)
- [ ] Naming conventions are consistent with the codebase
- [ ] No dead code, commented-out code, or unused imports
- [ ] Complex logic has comments explaining why, not what

### Testing
- [ ] Tests cover the primary success path
- [ ] Edge cases and error paths tested
- [ ] Tests are deterministic (no flaky tests introduced)
- [ ] Test names describe the behavior, not the implementation
- [ ] Mocks are minimal and realistic

---

## How to Give Constructive Feedback

The praise sandwich is patronizing and everyone sees through it. Be direct and kind. Critique the code, not the person.

### Principles
- Be specific. "This will throw if `user` is null on line 42" beats "handle errors better."
- Explain the why. Don't just say what to change -- explain the risk or benefit.
- Offer alternatives. If you flag a problem, suggest a solution or direction.
- Acknowledge tradeoffs. If a shortcut is reasonable given constraints, say so.
- Ask genuine questions. "What's the reasoning for X?" is valid when you don't understand.

### Prefixed Comments

```
[nit] Minor style issue, take or leave
[suggestion] Optional improvement idea
[question] Seeking understanding, not necessarily a change
[issue] Must be addressed before merge
[praise] Something done well worth calling out
[thought] Sharing context or perspective, no action needed
```

### Direct Feedback Examples

```
Instead of: "This is wrong"
Write: "This will fail when `items` is empty because `items[0]` returns undefined."

Instead of: "Why did you do it this way?"
Write: "Was there a performance reason for the manual loop? Array.filter would be more readable."

Instead of: "This is bad code"
Write: "This function handles validation, transformation, and persistence. Splitting would make each testable independently."
```

---

## PR Size Guidelines

```
Small (< 200 lines changed)   -> Review in 15-30 min. Ideal size.
Medium (200-400 lines)         -> Review in 30-60 min. Acceptable.
Large (400-800 lines)          -> Consider splitting.
Very large (> 800 lines)       -> Should almost always be split.
```

### When to Split

- Refactoring mixed with feature changes. Ship the refactor first.
- Infrastructure changes mixed with business logic.
- Database migrations with application code. Migrate first, then use.
- Multiple independent features or fixes bundled together.

### When Large PRs Are Acceptable

- Generated code (protobuf, OpenAPI, migration boilerplate).
- Bulk renames or automated reformatting.
- Initial project setup or deleting large amounts of dead code.

---

## Review Speed and Turnaround

Slow reviews kill velocity. Fast reviews compound into fast teams.

- **Target**: First-pass review within 4 business hours.
- **Unblocking**: If a PR blocks other work, prioritize it. Say so in the review request.
- **Async norms**: "I'll review by end of day" is better than silence.
- **Re-reviews**: After feedback is addressed, re-review within 2 hours. Focus on the diff, don't restart.
- **Don't batch**: Review PRs as they come in. End-of-day batching creates bottlenecks.
- **Stale PRs**: Unreviewed for 24+ hours? Escalate or reassign.

---

## Automated Review Tools

Automate what machines do better than humans. Save reviewers for logic and design.

### GitHub Actions

```yaml
name: PR Checks
on: [pull_request]
jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test -- --coverage
```

### Danger.js

```javascript
import { danger, warn, fail } from 'danger';

if (danger.github.pr.additions + danger.github.pr.deletions > 500) {
  warn('This PR is large. Consider splitting.');
}
if (!danger.github.pr.body || danger.github.pr.body.length < 20) {
  fail('Please add a meaningful PR description.');
}
const sensitive = danger.git.modified_files.filter(f =>
  f.includes('migration') || f.includes('.env') || f.includes('auth')
);
if (sensitive.length > 0) {
  warn(`Sensitive files changed: ${sensitive.join(', ')}`);
}
```

### Other Tools
- **CodeRabbit** -- AI-powered review summaries and inline suggestions
- **SonarQube / SonarCloud** -- static analysis for bugs, smells, security hotspots
- **Codacy / CodeClimate** -- automated code quality scoring
- **Reviewbot / Prow** -- bot-driven labeling, assignment, merge gating
- **Codecov / Coveralls** -- test coverage tracking and PR comments

---

## Security-Focused Review

Check against OWASP Top 10 patterns most likely to appear in application code.

- **Injection**: User input reaching queries, commands, or templates without parameterization.
- **Broken auth**: Missing auth checks on new endpoints. Tokens that don't expire.
- **Data exposure**: PII in logs, error messages, or API responses. Secrets in client code.
- **Access control**: Can user A access user B's resources? Admin routes unprotected?
- **Misconfiguration**: Debug mode in production. Default credentials. Verbose errors.
- **XSS**: User input rendered without encoding in HTML or JavaScript contexts.
- **SSRF**: Server requests using user-controlled URLs without allowlist validation.

### Auth Review Specifics
- Session tokens regenerated after login.
- Password reset tokens are single-use and time-limited.
- JWT validation checks signature, expiration, issuer, and audience.
- API keys scoped to minimum necessary permissions.

---

## Performance Review Patterns

### N+1 Queries

```javascript
// BAD: one query per iteration
for (const post of posts) {
  post.author = await db.query('SELECT * FROM users WHERE id = $1', [post.author_id]);
}
// GOOD: batch
const authorIds = [...new Set(posts.map(p => p.author_id))];
const authors = await db.query('SELECT * FROM users WHERE id = ANY($1)', [authorIds]);
```

### Memory Leaks
- Event listeners without cleanup on unmount/destroy.
- Intervals/timeouts not cleared. Subscriptions not unsubscribed.
- Growing caches without eviction. Closures holding references to large objects.

### Unnecessary Renders (React)
- Objects or arrays created inline in JSX props (new reference every render).
- Missing `useMemo`/`useCallback` for expensive computations or callback props.
- Context providers with unmemoized object values.

---

## Reviewing Database Migrations

Migrations deserve extra scrutiny because they're hard to reverse in production.

- [ ] Is the migration reversible? Does the rollback function work?
- [ ] Will it lock tables? Adding a column with default on large tables locks in some databases.
- [ ] Are new columns nullable or have defaults? Non-nullable without default fails on existing rows.
- [ ] Indexes added concurrently where possible (`CREATE INDEX CONCURRENTLY`)?
- [ ] Data migration separated from schema migration?
- [ ] Is the migration idempotent (safe to run twice)?
- [ ] Estimated run time tested against production-sized data?
- [ ] Dropping columns has a deprecation path (stop reading first, then drop)?

---

## Common Antipatterns in Reviews

**Nitpicking** -- Commenting on formatting and cosmetics a linter should catch. If you're debating semicolons, add a linter rule.

**Rubber-Stamping** -- "LGTM" on a 500-line PR after 2 minutes. If you can't review properly, let someone else.

**Bike-Shedding** -- Long debates on trivial matters while ignoring real issues. Keep comments proportional to impact.

**Gatekeeper Mentality** -- Blocking PRs over personal style preferences not in the team's style guide. Enforce shared standards, not individual taste.

**Drive-By Reviews** -- One vague comment ("this seems off") then disappearing. Either review thoroughly or don't start.

---

## Review Templates by PR Type

### Feature PR
```markdown
- [ ] Requirements from the issue/spec are met
- [ ] Edge cases identified and handled
- [ ] Tests cover happy path and failure cases
- [ ] No security regressions (auth, input validation)
- [ ] Performance acceptable (no new N+1, no blocking calls)
- [ ] Documentation updated if public API changed
```

### Bugfix PR
```markdown
- [ ] Root cause identified (not just symptoms patched)
- [ ] Regression test added that fails without the fix
- [ ] Fix doesn't introduce new edge cases
- [ ] Related code checked for same class of bug
```

### Refactor PR
```markdown
- [ ] Behavior unchanged (no functional changes mixed in)
- [ ] Existing tests pass without modification
- [ ] Code is measurably better (simpler, fewer dependencies, more testable)
- [ ] Performance characteristics unchanged or improved
```

### Dependency Update PR
```markdown
- [ ] Changelog reviewed for breaking changes
- [ ] Major version bumps justified and tested
- [ ] Lock file changes are consistent (no unexpected additions)
- [ ] No new vulnerabilities introduced
- [ ] Bundle size impact acceptable
```

---

## Code Ownership and CODEOWNERS

```
# .github/CODEOWNERS
*                       @org/platform-team
/src/components/        @org/frontend-team
/src/api/               @org/backend-team
/src/auth/              @org/security-team
/db/migrations/         @org/dba-team
/terraform/             @org/devops-team
/.github/workflows/     @org/devops-team
```

- Keep ownership granular. One team owning everything defeats the purpose.
- Review CODEOWNERS quarterly. Remove departed members. Update assignments.
- Use for mandatory review, not as a notification mechanism.
- Combine with branch protection rules requiring CODEOWNERS approval.

---

## Pair Review vs Async Review

### Pair Review (Synchronous)
**Best for**: Complex architecture, unfamiliar codebases, onboarding, contentious designs.
- Faster resolution. No async back-and-forth.
- Higher bandwidth catches design issues written comments miss.
- Time-expensive. Reserve for PRs where async would take 3+ rounds.

### Async Review (Standard)
**Best for**: Routine changes, well-understood domains, distributed teams.
- Reviewer reads at their own pace. More thoughtful.
- Written feedback creates searchable record.
- Risk of miscommunication. Tone is hard in text.

### When to Switch from Async to Pair
- More than 2 rounds of back-and-forth on the same issue.
- Reviewer and author disagree and comments aren't resolving it.
- The PR touches unfamiliar territory needing a walkthrough.

---

## When to Request Changes vs Approve with Comments

### Request Changes
- Bug that will break production.
- Security vulnerability (injection, auth bypass, data leak).
- PR doesn't do what the description says.
- Tests missing for critical paths.
- Change will cause data loss or corruption.

### Approve with Comments
- Suggestions are improvements but code works correctly as-is.
- Style preferences not in the team's style guide.
- Minor refactoring opportunities that aren't urgent.
- Questions driven by curiosity, not blockers.

**The rule**: If the PR shipped right now, would it cause harm? Request changes. If it works but could be better? Approve with comments. Trust the author to address optional feedback.

---

## Review Workflow

```
1. Read the PR description and linked issue
2. Understand context: what problem, why now?
3. Check PR size. If too large, ask to split before reviewing
4. Review test files first to understand expected behavior
5. Review main changes with the checklist for the PR type
6. Check correctness, security, performance, readability
7. Run locally if the change is complex or risky
8. Leave feedback using prefixed comments
9. Summarize with overall assessment and clear status
```

---

## Tools

- **Danger.js** -- programmable PR review rules and warnings
- **CodeRabbit** -- AI-powered review summaries and inline suggestions
- **SonarQube / SonarCloud** -- static analysis for bugs, smells, security hotspots
- **GitHub Actions** -- CI checks, linting, test coverage gates
- **Codecov / Coveralls** -- test coverage tracking and PR comments

## References

- Google Engineering Practices -- Code Review Guide: https://google.github.io/eng-practices/review/
- Conventional Comments: https://conventionalcomments.org/
- OWASP Code Review Guide: https://owasp.org/www-project-code-review-guide/
