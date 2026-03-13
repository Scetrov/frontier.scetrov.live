#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)" || exit 1

echo "Running hugo --minify..."
if command -v hugo >/dev/null 2>&1; then
  if ! hugo --minify >/dev/null 2>&1; then
    echo "Hugo build failed (run 'hugo --minify' locally to see errors)" >&2
    exit 1
  fi
else
  echo "hugo not found; install hugo from https://github.com/gohugoio/hugo/releases" >&2
  exit 1
fi

echo "Validating TOML frontmatter in content/*.md files..."
if ! ./.githooks/validate-frontmatter.sh; then
  echo "Frontmatter validation failed. Please add TOML frontmatter (+++ ... +++) to the listed files." >&2
  exit 1
fi

echo "Running htmltest (full-site link checks against public/)..."
if command -v htmltest >/dev/null 2>&1; then
  if ! htmltest -c .htmltest.yml -s public; then
    echo "htmltest found link issues; please fix them or add exclusions to .htmltest.yml" >&2
    exit 1
  fi
else
  echo "htmltest not found; install htmltest (go install github.com/wjdp/htmltest/cmd/htmltest@latest) to enable full-site HTML/link checks." >&2
  exit 1
fi

echo "Docs validation passed."
