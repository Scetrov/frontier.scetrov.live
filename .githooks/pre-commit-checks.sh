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

echo "Running cspell (spellcheck) on staged markdown files..."
if command -v npx >/dev/null 2>&1; then
  staged_md=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.md$' || true)
  if [ -n "$staged_md" ]; then
    echo "$staged_md" | xargs -r npx cspell --no-progress || {
      echo "cspell found spelling issues. Add words to .cspell.json or fix the typos." >&2
      exit 1
    }
  else
    echo "No staged markdown files to spellcheck." >&2
  fi
else
  echo "npx not available; skipping cspell (spellcheck)." >&2
fi

echo "Running htmltest (full-site link checks against public/)..."
if command -v htmltest >/dev/null 2>&1; then
  if ! htmltest -c .htmltest.yml -s public; then
    echo "htmltest found link issues; please fix them or add exclusions to .htmltest.yml" >&2
    exit 1
  fi
else
  echo "htmltest not found; skipping full-site HTML/link checks. Install htmltest (go install github.com/wjdp/htmltest/cmd/htmltest@latest) to enable." >&2
fi

echo "Docs validation passed."
