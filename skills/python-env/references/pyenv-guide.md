# Python Version Management

## pyenv (Version Manager)

```bash
# Install pyenv
brew install pyenv

# List available versions
pyenv versions

# Install Python version
pyenv install 3.11.0

# Set global version
pyenv global 3.11.0

# Set project version
pyenv local 3.10.0

# Which Python is active
which python
python --version
```

## .python-version File

```
3.11.0
```

Automatically use this version when entering directory.

## Multiple Python Versions

```bash
# Use pyenv to manage multiple versions
pyenv versions
# * 3.9.1 (set by /Users/user/.pyenv/version)
#   3.10.2
#   3.11.0

# Switch temporarily
pyenv shell 3.10.2

# Reset
pyenv shell --unset
```

## Dependency Isolation

Combine pyenv + venv:

```bash
# Use Python 3.11
pyenv local 3.11.0

# Create venv with that version
python -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

```bash
# Check if in virtual environment
echo $VIRTUAL_ENV   # Non-empty if in venv

# Set environment for development
export PYTHONPATH=/path/to/lib:$PYTHONPATH
export PYTHONDONTWRITEBYTECODE=1  # Don't create .pyc files
```
