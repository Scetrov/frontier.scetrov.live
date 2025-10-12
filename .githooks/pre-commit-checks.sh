#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

echo "Running hugo --minify..."
if ! hugo --minify >/dev/null 2>&1; then
  echo "Hugo build failed (run 'hugo --minify' locally to see errors)" >&2
  exit 1
fi

echo "Running markdownlint-cli..."
# prefer installed npx/markdownlint-cli; use local node_modules if available
if ! command -v npx >/dev/null 2>&1; then
  echo "npx not found; please install Node.js and markdownlint-cli (npm i -D markdownlint-cli)" >&2
  exit 1
fi

# run markdownlint; ignore exit code for printing then exit non-zero if issues
npx markdownlint-cli "content/**/*.md" ".github/**/*.md"

echo "Validating TOML frontmatter in content/*.md files..."
if ! ./.githooks/validate-frontmatter.sh; then
  echo "Frontmatter validation failed. Please add TOML frontmatter (+++ ... +++) to the listed files." >&2
  exit 1
fi

echo "Docs validation passed."
