# Python Virtual Environments

## venv (Built-in)

```bash
# Create virtual environment
python3 -m venv myenv

# Activate
source myenv/bin/activate      # macOS/Linux
myenv\Scripts\activate         # Windows

# Deactivate
deactivate

# Remove
rm -rf myenv
```

## Installing Packages

```bash
# Install into active venv
pip install flask django

# Specific version
pip install flask==2.0.1

# From requirements file
pip install -r requirements.txt

# Show installed packages
pip list

# Freeze dependencies
pip freeze > requirements.txt
```

## Poetry (Modern Approach)

```bash
# Create new project
poetry new myproject

# Initialize in existing project
poetry init

# Add dependency
poetry add flask
poetry add --group dev pytest

# Install dependencies
poetry install

# Lock dependencies
poetry lock

# Run command in venv
poetry run python script.py

# Export to requirements.txt
poetry export -f requirements.txt -o requirements.txt
```

### pyproject.toml Structure

```toml
[tool.poetry]
name = "myproject"
version = "0.1.0"
description = "My Python project"

[tool.poetry.dependencies]
python = "^3.9"
flask = "^2.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
black = "^23.0"
```

## Conda (Scientific Python)

```bash
# Create environment
conda create -n myenv python=3.10

# Activate
conda activate myenv

# Install packages
conda install numpy pandas scikit-learn

# List environments
conda env list

# Remove
conda env remove -n myenv
```

## Best Practices

1. **Always use virtual environments** - Keep projects isolated
2. **Use requirements.txt or Poetry** - Track dependencies
3. **Exclude venv from git** - Add to .gitignore
4. **Use specific versions** - For reproducibility
5. **Activate before developing** - So all tools work correctly
