---
name: git-worktree
description: Git worktrees for working on multiple branches simultaneously without stashing. Use when user mentions "git worktree", "multiple branches", "work on two branches", "parallel branches", "switch branches without stashing", "worktree", "isolated branch work", or needing to work on a hotfix while a feature is in progress.
---

# Git Worktree

## What Worktrees Are

A git worktree is an additional working directory linked to the same repository. Each worktree has its own checked-out branch and working state, but they all share a single `.git` history and object store.

## Why Worktrees Beat Stashing

Stashing forces you to context-switch linearly: save work, switch branch, do something, switch back, pop stash. Worktrees let you keep multiple branches checked out at the same time in separate directories. No serialization, no forgotten stashes, no conflicts when popping. You just open another terminal or editor window.

## Creating a Worktree

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

From a remote branch you want to track locally:

```bash
git fetch origin
git worktree add ../review-pr42 origin/pr-42
```

## Listing Worktrees

```bash
git worktree list
```

Output shows each worktree path, its HEAD commit, and the branch name.

## Removing Worktrees

First, delete the directory (or just finish your work there):

```bash
rm -rf ../hotfix-login
```

Then clean up the internal worktree tracking:

```bash
git worktree prune
```

Or do both in one step (Git 2.17+):

```bash
git worktree remove ../hotfix-login
```

Use `--force` if the worktree has uncommitted changes you want to discard.

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

Works well with the bare repo pattern (see Gotchas below). All worktrees grouped under one parent.

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

Open two terminals. Terminal 1 has your feature worktree where you write code. Terminal 2 runs the test suite in a separate worktree on the same branch or on `main`:

```bash
git worktree add ../myapp-test main
cd ../myapp-test
npm test -- --watch
```

You keep coding in your feature worktree without waiting for tests to finish.

### Compare behavior across branches side-by-side

Run the app from two worktrees on different ports:

```bash
# Terminal 1 - current feature
cd ~/projects/myapp
PORT=3000 npm start

# Terminal 2 - main branch
cd ~/projects/myapp-main
PORT=3001 npm start
```

Open both in a browser to compare behavior visually.

## Shared vs Separate node_modules and Build Artifacts

Worktrees share the `.git` directory but nothing else. Each worktree gets its own working tree, which means separate `node_modules`, `dist`, `build`, and any generated files.

Implications:

- You must run `npm install` (or your package manager) in each worktree independently.
- Build caches are not shared. A build in one worktree does not affect another.
- Disk usage increases with each worktree. If this matters, consider using `pnpm` with a shared store, or symlink common large dependencies manually.
- `.env` files are per-worktree. Copy or symlink them as needed.

## Gotchas

**Cannot check out the same branch in two worktrees.** Git prevents this to avoid conflicting work on the same ref. If you need this, commit your changes in one worktree first, or work on a temporary branch.

```bash
# This will fail if 'main' is already checked out somewhere
git worktree add ../myapp-second main
# fatal: 'main' is already checked out at '/path/to/myapp'
```

**The bare repo pattern.** Cloning with `--bare` gives you a repo with no default worktree. You then create all working directories as worktrees. This avoids the "main is already checked out" problem for the default branch:

```bash
git clone --bare git@github.com:user/myapp.git myapp/.bare
cd myapp/.bare
git worktree add ../main main
git worktree add ../develop develop
```

**Worktrees and garbage collection.** Objects are shared, so `git gc` in any worktree affects all of them. This is usually fine but be aware of it.

**Submodules.** Worktrees do not automatically initialize submodules. Run `git submodule update --init` in each new worktree if your project uses them.

## Integration with IDEs

**VS Code:** Open a worktree directory as a new window with `code ../myapp-hotfix`. Each window gets its own workspace with independent file state, terminal, and git status.

**JetBrains IDEs:** Use File > Open and select the worktree directory. Each worktree opens as a separate project. The IDE detects the shared git history automatically.

**Vim/Neovim:** Just `cd` into the worktree directory and open your editor. Fugitive and other git plugins pick up the worktree context automatically.

Each worktree is a normal directory on disk, so any editor that can open a folder works without special configuration.

## Quick Reference

| Action | Command |
|---|---|
| Create from existing branch | `git worktree add <path> <branch>` |
| Create with new branch | `git worktree add -b <new-branch> <path> <start-point>` |
| List all worktrees | `git worktree list` |
| Remove a worktree | `git worktree remove <path>` |
| Clean stale entries | `git worktree prune` |
| Lock a worktree (prevent prune) | `git worktree lock <path>` |
| Unlock | `git worktree unlock <path>` |
