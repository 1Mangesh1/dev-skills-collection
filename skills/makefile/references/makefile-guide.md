# Makefile Guide

## Basic Structure

```makefile
.PHONY: install build test

install:
	npm install

build:
	npm run build

test:
	npm test
```

## Variables

```makefile
OUTPUT_DIR = dist
SOURCE_FILES = src/**/*.ts

build:
	# Using variables
	tsc $(SOURCE_FILES) --outDir $(OUTPUT_DIR)
```

## Rules

```makefile
# Pattern rule
%.o: %.c
	gcc -c $< -o $@

# Implies: file.o created from file.c
```

## Dependencies

```makefile
.PHONY: deploy

build:
	npm run build

test:
	npm test

deploy: build test   # Run build then test first
	npm run deploy
```

## Common Variables

```makefile
$@    # Target name
$<    # First prerequisite
$^    # All prerequisites
$*    # Target name without extension
```

Example:
```makefile
%.txt: %.md
	markdown $< > $@  # Convert .md to .txt
```

## Functions

```makefile
# Wildcard: find files
SRC = $(wildcard src/*.js)

# Patsubst: substitute pattern
OBJ = $(patsubst src/%.js,obj/%.o,$(SRC))

# Filter: select matching
JS_FILES = $(filter %.js, src/*)

# Foreach: loop
DIRS = src test dist
clean:
	$(foreach dir, $(DIRS), rm -rf $(dir);)
```

## Tips

1. **Use .PHONY** - Mark non-file targets
2. **Indentation** - Use TABS not spaces
3. **Comments** - Use `##` for help text
4. **Default recipe** - `.DEFAULT_GOAL := help`
5. **Silent commands** - Use `@` prefix
