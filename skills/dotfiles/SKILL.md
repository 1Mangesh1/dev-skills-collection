---
name: dotfiles
description: Dotfile management with stow, chezmoi, yadm, or git bare repo for configuration sync across machines. Use when user asks to "manage dotfiles", "sync configs", "setup dotfiles", "backup shell config", "organize config files", "bootstrap new machine", "stow packages", "chezmoi template", "git bare repo dotfiles", "XDG directories", "shell startup files", "gitconfig aliases", "tmux config", or manage any ~/. configuration files.
---

# Dotfiles

Manage and sync configuration files across machines.

## Management Strategy Comparison

| Tool | Complexity | Symlinks | Templates | Encryption | Multi-machine |
|------|-----------|----------|-----------|------------|---------------|
| Git bare repo | Low | No (actual files) | No | No | Manual |
| GNU Stow | Low | Yes | No | No | Manual |
| chezmoi | Medium | No (copies) | Yes | Yes | Built-in |
| yadm | Medium | No (actual files) | Yes (Jinja) | Yes (GPG) | Built-in |

## Git Bare Repo (Minimal)

No dependencies, no symlinks. Home directory is the work tree.

```bash
git init --bare $HOME/.dotfiles
alias dot='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
dot config --local status.showUntrackedFiles no
echo "alias dot='git --git-dir=\$HOME/.dotfiles --work-tree=\$HOME'" >> ~/.zshrc

dot add ~/.zshrc ~/.gitconfig
dot commit -m "Add shell and git config"
dot remote add origin git@github.com:user/dotfiles.git
dot push -u origin main

# Clone to new machine
git clone --bare git@github.com:user/dotfiles.git $HOME/.dotfiles
alias dot='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
dot checkout
# If conflicts: back up existing files, then checkout again
dot checkout 2>&1 | grep -E "^\s+" | xargs -I{} mv {} {}.bak
dot checkout
dot config --local status.showUntrackedFiles no
```

## GNU Stow (Symlink Manager)

```bash
brew install stow   # macOS
apt install stow    # Debian/Ubuntu
mkdir -p ~/dotfiles && cd ~/dotfiles && git init
```

Each top-level folder is a "package" mirroring home directory structure:

```
~/dotfiles/
├── zsh/
│   └── .zshrc
├── git/
│   └── .gitconfig
├── nvim/
│   └── .config/nvim/
│       └── init.lua
├── tmux/
│   └── .tmux.conf
└── scripts/
    └── .local/bin/
        └── backup.sh
```

### Usage

```bash
cd ~/dotfiles
stow zsh                # symlink: ~/.zshrc -> ~/dotfiles/zsh/.zshrc
stow */                 # stow all packages
stow -D zsh             # unstow (remove symlinks)
stow -R zsh             # restow (unstow then stow — use after restructuring)
stow -t /etc/nginx nginx  # target a different directory
stow -n -v zsh          # dry run with verbose output
```

### Conflict Resolution and Ignore

```bash
# If target exists, stow refuses. Back up first:
mv ~/.zshrc ~/.zshrc.bak && stow zsh

# Or adopt existing files into stow dir (overwrites stow version):
stow --adopt zsh    # then review with git diff
```

Create `.stow-local-ignore` in any package to exclude files: `README.md`, `LICENSE`, `\.git`.

## chezmoi (Full-Featured)

```bash
brew install chezmoi
chezmoi init                                            # new setup
chezmoi init --apply https://github.com/user/dotfiles.git  # clone + apply

chezmoi add ~/.zshrc                    # track a file
chezmoi add --autotemplate ~/.gitconfig  # auto-detect template variables
chezmoi add --encrypt ~/.ssh/id_ed25519 # add encrypted
chezmoi edit ~/.zshrc                   # edit source, not target
chezmoi diff                            # preview changes
chezmoi apply                           # apply to home directory
chezmoi update                          # pull from remote and apply
```

### Templates

```
# ~/.local/share/chezmoi/dot_gitconfig.tmpl
[user]
    name = {{ .name }}
    email = {{ .email }}
{{ if eq .chezmoi.os "darwin" }}
[credential]
    helper = osxkeychain
{{ end }}
{{ if eq .chezmoi.hostname "work-laptop" }}
[http]
    proxy = http://proxy.corp:8080
{{ end }}
```

```toml
# ~/.config/chezmoi/chezmoi.toml
[data]
    name = "Jane Doe"
    email = "jane@work.com"
```

### Encrypted Files

```toml
# ~/.config/chezmoi/chezmoi.toml
encryption = "age"
[age]
    identity = "~/.config/chezmoi/key.txt"
    recipient = "age1ql3z7hjy54pw3hyww5ayyfg7zqgvc7w3j2elw8zmrj2kg5sfn9aqmcac8p"
```

### Run Scripts

```bash
# ~/.local/share/chezmoi/run_onchange_install-packages.sh.tmpl
#!/bin/bash
{{ if eq .chezmoi.os "darwin" -}}
brew bundle --file=/dev/stdin <<EOF
brew "ripgrep"
brew "fd"
brew "fzf"
EOF
{{ else if eq .chezmoi.os "linux" -}}
sudo apt install -y ripgrep fd-find fzf
{{ end -}}
```

## Shell Startup File Order

### Bash

```
Login shell:        /etc/profile -> ~/.bash_profile OR ~/.bash_login OR ~/.profile (first found)
Interactive shell:  ~/.bashrc
```

Best practice — put everything in `.bashrc`, source from `.bash_profile`:

```bash
# ~/.bash_profile
[[ -f ~/.bashrc ]] && source ~/.bashrc
```

### Zsh

```
Order: .zshenv (always) -> .zprofile (login) -> .zshrc (interactive) -> .zlogin (login)
Logout: .zlogout
```

Keep `.zshenv` minimal. Put most config in `.zshrc`.

### Common Shell Config

```bash
# -- History --
HISTFILE=~/.zsh_history
HISTSIZE=50000
SAVEHIST=50000
setopt SHARE_HISTORY HIST_IGNORE_DUPS HIST_IGNORE_SPACE

# -- PATH (deduplicated in zsh) --
typeset -U PATH path
path=("$HOME/.local/bin" "$HOME/go/bin" "$HOME/.cargo/bin" "/opt/homebrew/bin" $path)
export PATH

# -- Aliases --
alias ll='ls -lAh'
alias g='git'
alias dc='docker compose'
alias k='kubectl'
alias ..='cd ..'
alias ...='cd ../..'

# -- Functions --
mkcd() { mkdir -p "$1" && cd "$1"; }

# -- Environment --
export EDITOR='nvim'
export VISUAL='nvim'
eval "$(starship init zsh)"
[ -f ~/.fzf.zsh ] && source ~/.fzf.zsh
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
```

## Git Configuration

```ini
# ~/.gitconfig
[user]
    name = Your Name
    email = you@example.com
    signingkey = ~/.ssh/id_ed25519.pub
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    sw = switch
    lg = log --oneline --graph --all --decorate
    unstage = reset HEAD --
    amend = commit --amend --no-edit
    wip = !git add -A && git commit -m 'WIP'
[core]
    editor = nvim
    pager = delta
    autocrlf = input
    excludesFile = ~/.gitignore_global
[init]
    defaultBranch = main
[pull]
    rebase = true
[push]
    autoSetupRemote = true
[merge]
    conflictstyle = zdiff3
[diff]
    algorithm = histogram
    colorMoved = default
[delta]
    navigate = true
    side-by-side = true
    line-numbers = true
[gpg]
    format = ssh
[commit]
    gpgsign = true
[rerere]
    enabled = true
```

```
# ~/.gitignore_global
.DS_Store
Thumbs.db
*.swp
*~
.idea/
.vscode/
```

## Terminal Configs

### tmux

```bash
# ~/.tmux.conf
set -g default-terminal "tmux-256color"
set -ag terminal-overrides ",xterm-256color:RGB"
set -g mouse on
set -g base-index 1
setw -g pane-base-index 1
set -g renumber-windows on
set -g history-limit 50000
set -g escape-time 0

unbind C-b
set -g prefix C-a
bind C-a send-prefix
bind | split-window -h -c "#{pane_current_path}"
bind - split-window -v -c "#{pane_current_path}"
bind h select-pane -L
bind j select-pane -D
bind k select-pane -U
bind l select-pane -R
bind r source-file ~/.tmux.conf \; display "Reloaded"
```

### WezTerm

```lua
-- ~/.config/wezterm/wezterm.lua
local wezterm = require("wezterm")
local config = wezterm.config_builder()
config.font = wezterm.font("JetBrains Mono")
config.font_size = 14.0
config.color_scheme = "Catppuccin Mocha"
config.hide_tab_bar_if_only_one_tab = true
return config
```

## macOS-Specific

### Brewfile

```ruby
# ~/dotfiles/Brewfile
brew "git"
brew "neovim"
brew "ripgrep"
brew "fd"
brew "fzf"
brew "stow"
brew "starship"
brew "git-delta"
brew "jq"
brew "bat"
brew "eza"
brew "tmux"
cask "wezterm"
cask "raycast"
cask "1password"
cask "docker"
```

```bash
brew bundle --file=~/dotfiles/Brewfile              # install
brew bundle dump --force --file=~/dotfiles/Brewfile  # export current
```

### macOS Defaults

```bash
#!/bin/bash
# ~/.macos — run once on fresh install, then reboot
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write com.apple.finder ShowPathbar -bool true
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write NSGlobalDomain KeyRepeat -int 2
defaults write NSGlobalDomain InitialKeyRepeat -int 15
mkdir -p ~/Screenshots
defaults write com.apple.screencapture location ~/Screenshots
killall Finder Dock SystemUIServer 2>/dev/null
```

## Linux-Specific

```bash
# ~/.Xresources — apply with: xrdb -merge ~/.Xresources
Xft.dpi: 144
*.foreground: #c0caf5
*.background: #1a1b26
```

### systemd User Services

```ini
# ~/.config/systemd/user/ssh-agent.service
[Unit]
Description=SSH Agent
[Service]
Type=simple
ExecStart=/usr/bin/ssh-agent -D -a %t/ssh-agent.socket
[Install]
WantedBy=default.target
```

```bash
systemctl --user enable --now ssh-agent
```

## XDG Base Directory Specification

```bash
export XDG_CONFIG_HOME="$HOME/.config"     # config files
export XDG_DATA_HOME="$HOME/.local/share"  # persistent data
export XDG_CACHE_HOME="$HOME/.cache"       # disposable cache
export XDG_STATE_HOME="$HOME/.local/state" # logs, history
```

Tools that respect XDG: nvim, tmux (3.1+), git, starship, wezterm, alacritty, kitty, bat, ripgrep.

## Secrets Management

Never commit secrets in plaintext.

```bash
# git-crypt — encrypt specific files in a git repo
brew install git-crypt
cd ~/dotfiles && git-crypt init
# .gitattributes:  secrets/** filter=git-crypt diff=git-crypt
git-crypt export-key ~/dotfiles-key     # back up this key
git-crypt unlock ~/dotfiles-key         # on new machine

# 1Password CLI — in chezmoi templates or shell
# {{ onepasswordRead "op://Personal/SSH Key/private key" }}
export GITHUB_TOKEN=$(op read "op://Dev/GitHub/token")

# age encryption — used natively by chezmoi
age-keygen -o ~/.config/chezmoi/key.txt
# Then set encryption = "age" in chezmoi.toml (see chezmoi section)
```

## Bootstrap Script

```bash
#!/usr/bin/env bash
set -euo pipefail
DOTFILES_REPO="git@github.com:user/dotfiles.git"
DOTFILES_DIR="$HOME/dotfiles"

if [[ "$OSTYPE" == darwin* ]]; then
    command -v brew >/dev/null || /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    eval "$(/opt/homebrew/bin/brew shellenv)"
    brew install git stow
elif [[ -f /etc/debian_version ]]; then
    sudo apt update && sudo apt install -y git stow
elif [[ -f /etc/arch-release ]]; then
    sudo pacman -Sy --noconfirm git stow
fi

[[ ! -d "$DOTFILES_DIR" ]] && git clone "$DOTFILES_REPO" "$DOTFILES_DIR"
cd "$DOTFILES_DIR"
for dir in */; do stow -v "$dir"; done

if [[ "$OSTYPE" == darwin* ]]; then
    brew bundle --file="$DOTFILES_DIR/Brewfile" || true
    [[ -f "$DOTFILES_DIR/.macos" ]] && bash "$DOTFILES_DIR/.macos"
fi
echo "Bootstrap complete. Restart your shell."
```

## Best Practices

1. **Version control everything** — git repo, push to private GitHub/GitLab
2. **Modular structure** — one stow package or chezmoi directory per application
3. **No secrets in plaintext** — use chezmoi encryption, git-crypt, or 1Password CLI
4. **Bootstrap script** — automate fresh machine setup end to end
5. **Test before applying** — use `chezmoi diff` or `stow -n -v` before committing
6. **Separate public and private** — secrets in private repo, everything else public
7. **XDG compliance** — prefer `~/.config/` over `~/` when tools support it
8. **Idempotent scripts** — bootstrap should be safe to run multiple times
