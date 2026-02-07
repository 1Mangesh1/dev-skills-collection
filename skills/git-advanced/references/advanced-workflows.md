# Advanced Git Workflows

## Rebasing vs Merging

### Merging
```
main ──● (merge commit)
      │╲
      │ ●─●─● feature
      │/
     ●
```
**Pros:** Full history
**Cons:** Messy with many branches

### Rebasing
```
main ─●─●─●─●
        ↑ rebased feature commits
```
**Pros:** Clean history
**Cons:** Rewrites history (don't do on shared branches)

## Squashing Commits

Before PR:
```
● Initial commit
● Fix bug
● Refactor  
● Oops, forgot line
```

After squashing:
```
● Implement feature (with all changes)
```

```bash
git rebase -i HEAD~4  # Rewrite last 4 commits
```

## Cherry-pick

Apply specific commit from another branch:

```bash
git cherry-pick abc123def456  # Apply commit abc123def456
```

Useful for:
- Backporting fixes to older releases
- Pulling specific changes from another branch

## Stashing Work

```bash
# Save work without committing
git stash

# List stashes
git stash list

# Apply stash
git stash pop  # or git stash apply

# Stash with message
git stash save "WIP: authentication feature"
```

## Bisect (Binary Search for Bugs)

Find which commit introduced a bug:

```bash
git bisect start
git bisect bad HEAD     # Current is broken
git bisect good v1.0    # v1.0 was working
# Git checkouts commits, you test each one
git bisect reset        # Done
```
