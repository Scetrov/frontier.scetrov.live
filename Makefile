.PHONY: help build serve validate-docs lint-md precommit install-tools podman-policy devcontainer-rebuild clean

SHELL := /bin/bash

HUGO ?= hugo
MDLINT ?= npx markdownlint-cli
PRECOMMIT ?= pre-commit
SCRIPTS_DIR := scripts
PODMAN_HELPER := $(SCRIPTS_DIR)/setup-podman-policy.sh

help: ## Show available make targets
	@echo "Available targets:"
	@echo "  build               Build the Hugo site (minified)"
	@echo "  serve               Serve the site locally (hugo serve)"
	@echo "  validate-docs       Build the site and run markdown linting"
	@echo "  lint-md             Run markdownlint across content and .github"
	@echo "  precommit           Run configured pre-commit hooks (all files)"
	@echo "  install-tools       Try to install common tools (apt-based systems)"
	@echo "  podman-policy       Run the Podman policy helper script (if present)"
	@echo "  devcontainer-rebuild Rebuild devcontainer using devcontainer CLI"
	@echo "  clean               Remove generated public/ directory"

build: ## Build the Hugo site (minified)
	@echo "Running: $(HUGO) --minify"
	$(HUGO) --minify

serve: ## Serve the site locally (hugo serve)
	@echo "Running: $(HUGO) serve"
	$(HUGO) serve

lint-md: ## Run markdownlint over content and .github (uses npx markdownlint-cli)
	@echo "Running: $(MDLINT) \"content/**/*.md\" \".github/**/*.md\""
	$(MDLINT) "content/**/*.md" ".github/**/*.md"

validate-docs: build lint-md ## Build site and run markdown linter
	@echo "validate-docs completed"

precommit: ## Run pre-commit hooks locally (all files)
	@echo "Running: $(PRECOMMIT) run --all-files"
	$(PRECOMMIT) run --all-files

install-tools: ## Install tools used by this Makefile (Debian/Ubuntu via apt). May require sudo.
	@echo "Attempting to install hugo, npm, python3-pip, and node packages (markdownlint-cli)."
	@if command -v apt-get >/dev/null 2>&1; then \
		sudo apt-get update && sudo apt-get install -y hugo npm python3-pip || true; \
		python3 -m pip install --user pre-commit || true; \
		npm install -g markdownlint-cli || true; \
		echo "Installed (or attempted) packages. You may need to add ~/.local/bin to your PATH for pre-commit."; \
	else \
		echo "Non-apt system detected. Please install 'hugo', 'npm' and 'python3-pip' via your package manager, then run:"; \
		echo "  python3 -m pip install --user pre-commit"; \
		echo "  npm install -g markdownlint-cli"; \
	fi

podman-policy: ## Run the Podman policy helper script to create a permissive policy.json
	@if [ -x "$(PODMAN_HELPER)" ]; then \
		"$(PODMAN_HELPER)"; \
	else \
		echo "Podman helper '$(PODMAN_HELPER)' not found or not executable. See docs/CONTRIBUTING_DOCS.md"; \
	fi

devcontainer-rebuild: ## Rebuild devcontainer image (requires 'devcontainer' CLI)
	@command -v devcontainer >/dev/null 2>&1 || { echo "devcontainer CLI not found; install '@devcontainers/cli' or use VS Code to rebuild the container."; exit 1; }
	devcontainer build --workspace-folder .

clean: ## Remove generated public/ directory
	rm -rf public || true
