---
name: git-worktree
description: Git worktrees for working on multiple branches simultaneously without stashing or cloning. Use when user mentions "git worktree", "multiple branches", "work on two branches", "parallel branches", "switch branches without stashing", "worktree", "isolated branch work", needing to work on a hotfix while a feature is in progress, "bare repo worktree", "dotfiles bare repo", "worktree vs stash", "worktree vs clone", "orphaned worktree", or "worktree prune".
---

# Git Worktree

## Core Concepts

A git worktree is an additional working directory linked to the same repository. Every repo starts with one worktree (the main worktree). You can add linked worktrees that share the same `.git` object store, refs, and config.

**Shared across all worktrees:** object database, refs (branches, tags), config, hooks, remote tracking info, rerere cache.

**Isolated per worktree:** working tree files, index (staging area), HEAD, `MERGE_HEAD`, `REBASE_HEAD`, `CHERRY_PICK_HEAD`, `.env` files, `node_modules`, build artifacts.

The main worktree is the one created by `git init` or `git clone`. Linked worktrees are created with `git worktree add`. The main worktree cannot be removed with `git worktree remove` -- it is permanent. Linked worktrees can be added and removed freely.

Internally, each linked worktree gets a directory under `.git/worktrees/<name>/` containing its own `HEAD`, `index`, and tracking files. The linked worktree's working directory contains a `.git` file (not a directory) pointing back to this location.

## Worktree vs Stash vs Branch Switching vs Clone

| Approach | Good When | Downsides |
|---|---|---|
| `git stash` | Quick one-off interruptions under 5 minutes | Linear workflow, stashes pile up, merge conflicts on pop |
| `git switch` | Clean working tree, fast branch change | Must commit or stash first, loses uncommitted context |
| `git worktree` | Parallel work, keeping multiple contexts alive | Extra disk space, must manage multiple directories |
| `git clone` | Fully isolated environments, different configs | Doubles disk usage for objects, no shared refs |

Stashing forces linear context switching. Worktrees let you keep multiple branches checked out simultaneously in separate directories -- no serialization, no forgotten stashes, no pop conflicts.

## Performance Benefits Over Clone

Worktrees share the object database. A clone duplicates it. On a repo with 2 GB of history, a second worktree costs only the working tree size (source files). A second clone costs 2 GB + working tree.

Branches and tags update instantly across worktrees because refs are shared. With clones, you must fetch separately in each.

Worktrees also share hooks and config, so tooling stays consistent without duplication.

## Creating Worktrees

From an existing branch:

```bash
git worktree add ../hotfix-login hotfix/login
```

This checks out `hotfix/login` into `../hotfix-login`.

From a new branch:

```bash
git worktree add -b feature/search ../feature-search main
```

Creates `feature/search` based on `main` and checks it out in `../feature-search`.

From a specific commit (detached HEAD):

```bash
git worktree add --detach ../investigate-crash abc1234
```

Useful for inspecting a specific commit without creating a branch.

From a remote branch you want to track locally:

```bash
git fetch origin
git worktree add ../review-pr42 origin/pr-42
```

## Worktree Management

### Listing Worktrees

```bash
git worktree list
```

Output shows each worktree path, its HEAD commit, and the branch name. Add `--porcelain` for machine-parseable output.

### Removing Worktrees

The correct way -- handles both the directory and internal tracking:

```bash
git worktree remove ../hotfix-login
```

Use `--force` if the worktree has uncommitted changes you want to discard.

### Moving Worktrees

```bash
git worktree move ../hotfix-login ../hotfix-auth
```

Moves the worktree directory and updates internal tracking. Cannot move the main worktree.

### Lock and Unlock

Lock a worktree to prevent `git worktree prune` from removing it (useful for worktrees on removable drives or network mounts):

```bash
git worktree lock ../usb-worktree --reason "on external drive"
git worktree unlock ../usb-worktree
```

### Pruning Stale Entries

```bash
git worktree prune
```

Removes internal tracking for worktrees whose directories no longer exist. Run with `--dry-run` first to see what would be pruned. See "Cleaning Up Orphaned Worktrees" below for more detail.

## Directory Layout Strategies

**Sibling directories (recommended)**

```
~/projects/
  myapp/              # main worktree
  myapp-hotfix/       # hotfix worktree
  myapp-review/       # PR review worktree
```

Keeps things flat. Easy to spot in file managers and terminal tabs. Each directory is self-contained.

**Subdirectory layout**

```
~/projects/myapp/
  main/               # main worktree (bare repo is parent)
  hotfix/
  review/
```

Works well with the bare repo pattern (see below). All worktrees grouped under one parent.

Pick one convention per project and stick with it.

## Common Workflows

### Hotfix while mid-feature

You are deep in a feature branch with uncommitted changes. Production breaks.

```bash
# From your feature worktree, create a hotfix worktree
git worktree add -b hotfix/crash ../myapp-hotfix main

# Move to the hotfix directory
cd ../myapp-hotfix

# Fix the bug, commit, push
git commit -am "fix null pointer in auth handler"
git push origin hotfix/crash

# Go back to your feature work -- it is exactly as you left it
cd ../myapp
```

### Review a PR while your branch is dirty

```bash
git fetch origin
git worktree add ../myapp-review origin/feature/new-api

cd ../myapp-review
# Read the code, run tests, leave comments
# Your in-progress work in the main worktree is untouched
```

When done:

```bash
git worktree remove ../myapp-review
```

### Run tests on one branch while coding on another

Terminal 1: write code in your feature worktree. Terminal 2: run tests in a separate worktree:

```bash
git worktree add ../myapp-test main
cd ../myapp-test && npm test -- --watch
```

### Compare behavior across branches side-by-side

Run the app from two worktrees on different ports:

```bash
# Terminal 1                          # Terminal 2
cd ~/projects/myapp                   cd ~/projects/myapp-main
PORT=3000 npm start                   PORT=3001 npm start
```

## Shared vs Separate Dependencies and Artifacts

Each worktree gets its own working tree -- separate `node_modules`, `dist`, `build`, `.env`, and generated files. You must run `npm install` (or your package manager) in each worktree independently. Build caches are not shared. If disk matters, use `pnpm` with a shared store. Symlink `.env` files across worktrees if they share the same config.

## Bare Repo + Worktree Setup

Cloning with `--bare` gives you a repo with no default worktree. You then create all working directories as worktrees. This avoids the "main is already checked out" problem for the default branch.

```bash
git clone --bare git@github.com:user/myapp.git myapp/.bare
cd myapp

# Tell git where the bare repo lives
echo "gitdir: ./.bare" > .git

# Create worktrees for the branches you need
git worktree add main main
git worktree add develop develop
git worktree add feature/auth feature/auth
```

### Dotfiles with bare repo

```bash
# Initial setup
git init --bare $HOME/.dotfiles
alias dotfiles='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
dotfiles config status.showUntrackedFiles no
dotfiles add ~/.zshrc ~/.gitconfig
dotfiles commit -m "add shell and git config"

# On a new machine
git clone --bare git@github.com:user/dotfiles.git $HOME/.dotfiles
alias dotfiles='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
dotfiles checkout
```

## Handling Submodules with Worktrees

Worktrees do not automatically initialize submodules. Run `git submodule update --init --recursive` in each new worktree. Each worktree has its own index tracking submodule commits, so different branches can have different submodule states without conflict.

```bash
git worktree add ../myapp-hotfix hotfix/crash
cd ../myapp-hotfix
git submodule update --init --recursive
```

## CI/CD Patterns with Worktrees

Test multiple branches in a single CI job without multiple clones:

```bash
git fetch origin main feature/new-api
git worktree add /tmp/test-main main
git worktree add /tmp/test-feature origin/feature/new-api

# Run tests in parallel
(cd /tmp/test-main && npm ci && npm test) &
(cd /tmp/test-feature && npm ci && npm test) &
wait

# Clean up
git worktree remove /tmp/test-main
git worktree remove /tmp/test-feature
```

Saves CI time and disk compared to multiple full clones.

## IDE Integration

**VS Code:** `code ../myapp-hotfix` opens a new window with independent file state, terminal, and git status. Multi-root workspaces can combine multiple worktrees in one window.

**JetBrains:** File > Open the worktree directory. Opens as a separate project with shared git history detected automatically.

**Vim/Neovim:** `cd` into the worktree and open your editor. Fugitive and other git plugins pick up worktree context automatically.

Every worktree is a normal directory on disk -- any editor that can open a folder works without special configuration.

## Worktree-Aware Scripts and Aliases

```bash
# List worktrees with short names
alias gwl='git worktree list'

# Quick-create a worktree for a branch
gwa() {
  local branch="$1"
  local dir="../$(basename "$(pwd)")-$(echo "$branch" | tr '/' '-')"
  git worktree add "$dir" "$branch" && cd "$dir"
}

# Quick-create a worktree with a new branch from main
gwn() {
  local branch="$1"
  local dir="../$(basename "$(pwd)")-$(echo "$branch" | tr '/' '-')"
  git worktree add -b "$branch" "$dir" main && cd "$dir"
}

# Remove current worktree and go back to main
gwr() {
  local current="$(pwd)"
  local main="$(git worktree list | head -1 | awk '{print $1}')"
  cd "$main" && git worktree remove "$current"
}

# Check if inside a linked worktree
is_linked_worktree() {
  [ -f "$(pwd)/.git" ] && echo "linked worktree" || echo "main worktree or not a worktree"
}
```

## Common Mistakes

**Deleting the directory without `git worktree remove`.** Leaves orphaned entries in `.git/worktrees/`. Fix with `git worktree prune --dry-run` then `git worktree prune`. Always prefer `git worktree remove` -- it handles both the directory and tracking in one step.

**Trying to check out the same branch in two worktrees.** Git prevents this to avoid conflicting work on the same ref.

```bash
# This will fail if 'main' is already checked out somewhere
git worktree add ../myapp-second main
# fatal: 'main' is already checked out at '/path/to/myapp'
```

Workaround: use `--detach` to check out the commit without the branch, or commit changes and use a temporary branch.

**Forgetting to install dependencies in new worktrees.** Each worktree has its own `node_modules` / `venv` / etc. Always run your install step after creating a worktree.

**Running `git gc` aggressively.** Objects are shared, so `git gc` in any worktree affects all of them. Aggressive pruning can remove objects still referenced by another worktree's index. Generally safe with default settings.

**Expecting worktree-specific config.** `git config` writes to the shared config by default. Use `git config --worktree` (Git 2.20+) after enabling `extensions.worktreeConfig` for per-worktree settings.

## Quick Reference

| Action | Command |
|---|---|
| Create from existing branch | `git worktree add <path> <branch>` |
| Create with new branch | `git worktree add -b <new-branch> <path> <start-point>` |
| Create detached HEAD | `git worktree add --detach <path> <commit>` |
| List all worktrees | `git worktree list` |
| List (machine-readable) | `git worktree list --porcelain` |
| Remove a worktree | `git worktree remove <path>` |
| Move a worktree | `git worktree move <old-path> <new-path>` |
| Clean stale entries | `git worktree prune` |
| Preview prune | `git worktree prune --dry-run` |
| Lock a worktree | `git worktree lock <path>` |
| Lock with reason | `git worktree lock <path> --reason "why"` |
| Unlock | `git worktree unlock <path>` |
