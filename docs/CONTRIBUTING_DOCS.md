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

If you use Podman (or the distro's buildah shim) instead of Docker, VS Code's devcontainer build may fail with an error about a missing `policy.json`. Example from the logs:

```
Error: creating build container: no policy.json file found at any of the following: "/home/<user>/.config/containers/policy.json", "/etc/containers/policy.json"
```

Workarounds:

- Create a simple `/etc/containers/policy.json` with permissive defaults, or see your distro's Podman/buildah documentation for the recommended configuration.
- Use the prebuilt devcontainer image instead of building locally (the repository's `.devcontainer/devcontainer.json` defaults to a prebuilt image to avoid this issue).
