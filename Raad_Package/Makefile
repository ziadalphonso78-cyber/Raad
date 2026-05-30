# Makefile for Raad Language

.PHONY: help repl run test clean install uninstall build debug format

# Variables
PYTHON = python3
MAIN = main.py
VERSION = 1.0.0

# Default target
help:
	@echo "Raad Language v$(VERSION)"
	@echo ""
	@echo "Usage: make [command]"
	@echo ""
	@echo "Commands:"
	@echo "  make repl          - Start Raad REPL"
	@echo "  make run FILE=name.rd - Run a Raad file"
	@echo "  make test          - Run test.rd"
	@echo "  make clean         - Remove cache files"
	@echo "  make install       - Install globally"
	@echo "  make uninstall     - Remove global install"
	@echo "  make build         - Create executable"
	@echo "  make debug         - Run with debug output"
	@echo "  make format        - Format code"
	@echo "  make help          - Show this help"

# Start REPL
repl:
	@echo "Starting Raad REPL..."
	$(PYTHON) $(MAIN)

# Run a specific file
run:
	@if [ -z "../$(FILE)" ]; then \
		echo "Error: Please specify FILE=filename.rd"; \
		exit 1; \
	fi
	@if [ ! -f "../$(FILE)" ]; then \
		echo "Error: File '../$(FILE)' not found"; \
		exit 1; \
	fi
	@echo "Running $(FILE)..."
	$(PYTHON) $(MAIN) ../$(FILE)

# Run test file
test:
	@if [ -f "test.rd" ]; then \
		echo "Running test.rd..."; \
		$(PYTHON) $(MAIN) ../test.rd; \
	else \
		echo "Creating test.rd..."; \
		echo 'print("Hello from Raad!")' > test.rd; \
		$(PYTHON) $(MAIN) ../test.rd; \
	fi

# Clean cache files
clean:
	@echo "Cleaning cache files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".DS_Store" -delete 2>/dev/null || true
	@echo "Clean complete!"

# Install globally (Linux/Mac)
install:
	@echo "Installing Raad Language..."
	@sudo cp $(MAIN) /usr/local/bin/raad
	@sudo chmod +x /usr/local/bin/raad
	@echo "✓ Installed! Use 'raad' command anywhere"

# Uninstall global command
uninstall:
	@echo "Uninstalling Raad Language..."
	@sudo rm -f /usr/local/bin/raad
	@echo "✓ Uninstalled!"

# Build standalone executable
build:
	@echo "Building executable..."
	@echo '#!/usr/bin/env python3' > raad
	@cat $(MAIN) >> raad
	@chmod +x raad
	@echo "✓ Created './raad'"
	@echo "Run with: ./raad or ./raad file.rd"

# Debug mode
debug:
	@echo "Debug mode enabled..."
	$(PYTHON) -v $(MAIN) $(FILE)

# Format code (requires black)
format:
	@which black > /dev/null || (echo "Installing black..."; pip install black)
	@echo "Formatting code..."
	@black *.py
	@echo "Format complete!"

# Create new project
new:
	@if [ -z "$(NAME)" ]; then \
		echo "Error: Please specify NAME=projectname"; \
		exit 1; \
	fi
	@mkdir -p $(NAME)
	@echo '# $(NAME).rd' > $(NAME)/main.rd
	@echo 'print("Welcome to $(NAME)!")' >> $(NAME)/main.rd
	@echo "✓ Created new project in ./$(NAME)"
	@echo "Run with: make run FILE=$(NAME)/main.rd"

# Run examples
examples:
	@echo "Running examples..."
	@echo ""
	@echo "1. Hello World:"
	@echo 'print("Hello, World!")' | $(PYTHON) $(MAIN)
	@echo ""
	@echo "2. Variables:"
	@echo 'var x = 10; var y = 20; print(x + y)' | $(PYTHON) $(MAIN)
	@echo ""
	@echo "3. Loop:"
	@echo 'var i = 0; while i < 5 { print(i); i++ }' | $(PYTHON) $(MAIN)

# Show version
version:
	@echo "Raad Language v$(VERSION)"

# Run all tests
all-tests:
	@echo "Running all tests..."
	@for test in tests/*.rd; do \
		echo "Testing $$test..."; \
		$(PYTHON) $(MAIN) $$test; \
	done

# Watch mode (auto-run on file change)
watch:
	@which entr > /dev/null || (echo "Install entr: brew install entr (Mac) or apt install entr (Linux)"); \
	echo "Watching $(FILE) for changes..."; \
	echo "$(FILE)" | entr -c $(PYTHON) $(MAIN) $(FILE)

# Create distribution package
dist:
	@mkdir -p dist
	@cp $(MAIN) dist/
	@cp -r . dist/ 2>/dev/null || true
	@echo "Distribution created in ./dist"

# Docker support
docker-build:
	@docker build -t raad-lang .

docker-run:
	@docker run -it raad-lang

# Set up development environment
setup-dev:
	@echo "Setting up development environment..."
	@pip install black pytest
	@mkdir -p tests examples
	@echo "✓ Development environment ready!"

# Short aliases
r: repl
rd: run
t: test
c: clean
b: build
v: version