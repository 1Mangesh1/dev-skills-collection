# GNU Make Advanced

## String Functions

```makefile
TEXT = "Hello World"

# Substitute
RESULT = $(subst Hello,Hi,$(TEXT))  # Hi World

# Uppercase
UPPER = $(shell echo $(TEXT) | tr a-z A-Z)
```

## Conditional Execution

```makefile
ifeq ($(BUILD_ENV),production)
    FLAGS = -O3
else
    FLAGS = -g
endif

build:
	gcc $(FLAGS) main.c
```

## .SECONDEXPANSION

Two-pass variable expansion:

```makefile
.SECONDEXPANSION:

TARGETS = file1 file2 file3
$(TARGETS): %: %.tmp
	process $< > $@

%.tmp:
	generate_temp_file > $@
```

## Multi-line Recipes

```makefile
build:
	@echo "Building..."
	npm run build
	@echo "Build complete"
	@test -f dist/index.js || (echo "Build failed!"; false)
```

## Parallel Execution

```bash
make -j4  # Run 4 jobs in parallel
```
