# Define variables
PYTHON = python3
VENV_DIR = venv
ACTIVATE = . $(VENV_DIR)/bin/activate

# Default rule
.PHONY: all
all: install run

# Create a virtual environment and install dependencies
.PHONY: install
install:
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Activating virtual environment and installing dependencies..."
	bash -c "$(ACTIVATE) && pip install --upgrade pip && pip install -r requirements.txt"

# Run the application
.PHONY: run
run:
	@echo "Running the application..."
	bash -c "$(ACTIVATE) && $(PYTHON) app.py"

# Clean up virtual environment
.PHONY: clean
clean:
	@echo "Removing virtual environment..."
	rm -rf $(VENV_DIR)

