# Dotfiles Management

## Common Dotfiles

```
~/.bashrc       - Bash shell configuration
~/.zshrc        - Zsh shell configuration
~/.vimrc        - Vim editor configuration
~/.gitconfig    - Git configuration
~/.ssh/config   - SSH client configuration
~/.tmux.conf    - Tmux configuration
~/.npmrc        - NPM configuration
~/.nvmrc        - Node.js version
```

## Setup Dotfiles Repository

```bash
# Create dotfiles repo
mkdir ~/.dotfiles
cd ~/.dotfiles
git init

# Create directory structure
mkdir -p bash zsh vim git

# Move files
mv ~/.bashrc bash/
mv ~/.zshrc zsh/
mv ~/.vimrc vim/
```

## Symlinking (Old Way)

```bash
ln -s ~/.dotfiles/bash/.bashrc ~/.bashrc
ln -s ~/.dotfiles/zsh/.zshrc ~/.zshrc
ln -s ~/.dotfiles/vim/.vimrc ~/.vimrc
```

## Better: Use GNU Stow

```bash
# Install stow
brew install stow      # macOS
sudo apt install stow  # Ubuntu

# Organize
mkdir -p .dotfiles/{bash,zsh,vim,git}
mv ~/.bashrc .dotfiles/bash/.bashrc
# ... repeat for other files

# Create symlinks
cd ~/.dotfiles
stow bash    # Creates ~/.bashrc -> zsh/bash/.bashrc
stow zsh
stow vim
```

## Installation Script

```bash
#!/bin/bash

# Clone dotfiles repo
cd ~
git clone https://github.com/username/dotfiles .dotfiles

# Install stow
sudo apt install stow

# Apply all stow configs
cd ~/.dotfiles
stow */
```

## Protecting Secrets

Never commit:
- `.ssh/private_key`
- `.aws/credentials`
- API keys
- Passwords

```bash
# .gitignore
/.ssh/id_*
!/.ssh/id_*.pub
/.aws/credentials
.env.local
```

## Platform-Specific Configs

```bash
# macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS-specific config
  export PATH="/usr/local/opt/gnu-sed/libexec/gnubin:$PATH"
fi

# Linux
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
  # Linux-specific config
fi

# WSL
if grep -qi microsoft /proc/version; then
  # WSL-specific config
fi
```
