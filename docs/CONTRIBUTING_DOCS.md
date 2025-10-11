Pre-commit hooks for docs validation
====================================

This project includes a pre-commit hook that validates documentation before commits:

- Runs `hugo --minify` to ensure the site builds with minification.
- Runs `markdownlint-cli` to lint Markdown files under `content/` and `.github/`.

Install and enable the hooks locally:

```sh
# Install pre-commit (Python)
python3 -m pip install --user pre-commit

# From the repository root, install the git hooks
pre-commit install

# Run hooks once against all files (optional)
pre-commit run --all-files
```

If you don't have `npx` available, install Node.js and the markdownlint-cli package:

```sh
# using npm
npm install --save-dev markdownlint-cli
```

Troubleshooting:

- If `hugo --minify` fails locally, run `hugo --minify` directly to see build errors.
- If `npx markdownlint-cli` reports warnings/errors, fix the reported markdown issues or update `.markdownlint.json` if a rule needs to be tuned.# Docs validation helpers

This repository includes local and CI checks to validate documentation. The checks run:

- `hugo --minify` to ensure the site builds
- `markdownlint-cli` to lint Markdown files under `content/` and `.github/`

Local pre-commit
----------------

Install pre-commit and enable the hooks:

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

CI
--

A GitHub Actions workflow runs on push/PR to `main` and executes the same checks.

Podman / buildah note
---------------------

If you use Podman (or the distributions buildah shim) instead of Docker, VS Code's devcontainer build may fail with an error about a missing `policy.json`. Example from the logs:

```
Error: creating build container: no policy.json file found at any of the following: "/home/<user>/.config/containers/policy.json", "/etc/containers/policy.json"
```

Workarounds:

- Create a simple `/etc/containers/policy.json` with permissive defaults, or see your distributions Podman/buildah documentation for the recommended configuration.
- Use the prebuilt devcontainer image instead of building locally (the repository's `.devcontainer/devcontainer.json` defaults to a prebuilt image to avoid this issue).

Podman helper script
--------------------

We've added a helper script that writes a permissive `policy.json` for Podman to `$HOME/.config/containers/policy.json` and (optionally) to `/etc/containers/policy.json` if run as root.

Run it locally with:

```sh
./scripts/setup-podman-policy.sh
```

This will create a user-level `policy.json`. To write the system file (requires sudo) re-run the command as root or follow the printed instructions.

Makefile (convenience targets)
------------------------------

This repository includes a top-level `Makefile` with convenient targets to build, serve, and validate the docs. Common targets include:

- `build` — run `hugo --minify` to build the site.
- `serve` — run `hugo serve` for local preview.
- `validate-docs` — run the site build then `markdownlint` over the content.
- `lint-md` — run `markdownlint` only.
- `precommit` — run the configured pre-commit hooks against all files.
- `install-tools` — attempt to install common tools on Debian/Ubuntu (may require sudo).
- `podman-policy` — run the Podman helper script (`scripts/setup-podman-policy.sh`).
- `devcontainer-rebuild` — rebuild the devcontainer (requires the `devcontainer` CLI).

Examples:

```sh
# Build the site (minified)
make build

# Serve the site locally
make serve

# Run docs validation (build + markdown lint)
make validate-docs

# Run pre-commit hooks locally (all files)
make precommit

# Try installing tools (Debian/Ubuntu)
make install-tools

# Run the Podman policy helper
make podman-policy
```

Notes:

- `install-tools` uses `apt-get` and is intended for Debian/Ubuntu systems; on other OSes install the listed tools with your package manager and then run the commands shown.
- If `pre-commit` was installed with `python3 -m pip --user`, add `~/.local/bin` to your `PATH` so `make precommit` can find it.
- `devcontainer-rebuild` requires the `devcontainer` CLI from `@devcontainers/cli` or use VS Code's "Rebuild Container" action.
