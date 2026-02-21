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
```text
If you don't have `npx` available, install Node.js and the markdownlint-cli package:

```sh
# using npm
npm install --save-dev markdownlint-cli
```text
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
```text
CI
--

A GitHub Actions workflow runs on push/PR to `main` and executes the same checks.

Podman / buildah note
---------------------

If you use Podman (or the distributions buildah shim) instead of Docker, VS Code's devcontainer build may fail with an error about a missing `policy.json`. Example from the logs:

```text
Error: creating build container: no policy.json file found at any of the following: "/home/<user>/.config/containers/policy.json", "/etc/containers/policy.json"
```text
Workarounds:

- Create a simple `/etc/containers/policy.json` with permissive defaults, or see your distributions Podman/buildah documentation for the recommended configuration.
- Use the prebuilt devcontainer image instead of building locally (the repository's `.devcontainer/devcontainer.json` defaults to a prebuilt image to avoid this issue).

Podman helper script
--------------------

We've added a helper script that writes a permissive `policy.json` for Podman to `$HOME/.config/containers/policy.json` and (optionally) to `/etc/containers/policy.json` if run as root.

Run it locally with:

```sh
./scripts/setup-podman-policy.sh
```text
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
```text
Notes:

- `install-tools` uses `apt-get` and is intended for Debian/Ubuntu systems; on other OSes install the listed tools with your package manager and then run the commands shown.
- If `pre-commit` was installed with `python3 -m pip --user`, add `~/.local/bin` to your `PATH` so `make precommit` can find it.
- `devcontainer-rebuild` requires the `devcontainer` CLI from `@devcontainers/cli` or use VS Code's "Rebuild Container" action.

Devcontainer image vs build note
-------------------------------

The devcontainer configuration was intentionally set to use a prebuilt image (`mcr.microsoft.com/devcontainers/javascript-node:20`) instead of building the local `Dockerfile`. This avoids local image builds that can fail under rootless Podman when subordinate UID/GID mappings are insufficient.

If VS Code still fails to pull the base image, follow the NixOS remedy earlier in this document (add `extraSubuids` / `extraSubgids` for your user and run `podman system migrate`), or use the `podman-policy` helper as documented above for a temporary workaround.

Upstream PR Monitoring Process
------------------------------

This documentation site tracks two upstream repositories for changes that affect content accuracy:

| Repository | URL |
| --- | --- |
| **world-contracts** | https://github.com/evefrontier/world-contracts |
| **builder-documentation** | https://github.com/evefrontier/builder-documentation |

**Review Cadence**

Perform a weekly review of open and recently merged pull requests in both repositories.

**Process**

- **Check for open/merged PRs** on both repos (GitHub → Pull requests → filter by recently updated).
- **Assess impact** — determine which documentation pages are affected by the change.
- **For merged PRs**: Update the affected pages immediately. If the PR introduced a renamed struct, new module, or changed behavior, update the corresponding `.move.md` page, diagrams, and security tables.
- **For open/draft PRs**: If the change is significant enough to document early, create or update the affected page and add the `pre-release` shortcode at the top of the content:

  ```markdown
  {{%/* pre-release pr_number="84" repo="world-contracts" description="Item teleportation vulnerability fix" */%}}
  ```

  The shortcode renders a warning banner linking to the PR, clearly marking the content as based on unreleased code.

- **When the PR merges**: Remove the `pre-release` shortcode from the page.

Shortcode parameters:

| Parameter | Required | Default | Description |
| --- | --- | --- | --- |
| `pr_number` | Yes | — | The pull request number |
| `repo` | No | `world-contracts` | Repository name (e.g., `builder-documentation`) |
| `description` | No | — | Brief description shown in the banner |

Currently tracked PRs:

| PR | Repo | Status | Summary |
| --- | --- | --- | --- |
| [#84](https://github.com/evefrontier/world-contracts/pull/84) | world-contracts | Draft | Item teleportation vulnerability |
| [#83](https://github.com/evefrontier/world-contracts/pull/83) | world-contracts | Draft | Deposit Receipts extension |
| [#44](https://github.com/evefrontier/builder-documentation/pull/44) | builder-documentation | Open | Fix outdated Move link in intro |
