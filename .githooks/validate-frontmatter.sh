#!/usr/bin/env bash
set -euo pipefail

# validate-frontmatter.sh
# Ensure every Markdown file under content/ has TOML front-matter
# wrapped with +++ markers (opening and closing).

root_dir=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$root_dir"

failures=()

# Use a glob to find markdown files; handle nested dirs
shopt -s globstar nullglob
for file in content/**/*.md; do
  [ -f "$file" ] || continue

  # read first line
  first_line=$(sed -n '1p' "$file" || true)

  if [ "$first_line" != "+++" ]; then
    failures+=("$file: missing opening +++ frontmatter marker")
    continue
  fi

  # find the line number of the closing +++ after the first line
  close_line=$(awk 'NR>1 && $0=="+++" {print NR; exit}' "$file" || true)

  if [ -z "$close_line" ]; then
    failures+=("$file: missing closing +++ frontmatter marker")
    continue
  fi

  # Ensure there is at least one line of content inside the frontmatter
  if [ "$close_line" -le 2 ]; then
    failures+=("$file: empty TOML frontmatter (no lines between +++ markers)")
    continue
  fi

  # extract frontmatter lines (lines 2..close_line-1)
  fm_content=$(sed -n "2,$((close_line-1))p" "$file" || true)

  # Check for a title key in TOML frontmatter (title = "..." or title = '...')
  if ! printf "%s" "$fm_content" | grep -qE "^[[:space:]]*title[[:space:]]*=[[:space:]]*(\"[^\"]+\"|'[^']+')[[:space:]]*$"; then
    failures+=("$file: missing required 'title' field in TOML frontmatter")
    continue
  fi
done

if [ ${#failures[@]} -ne 0 ]; then
  echo "Frontmatter validation failed for the following files:" >&2
  for f in "${failures[@]}"; do
    echo " - $f" >&2
  done
  echo >&2
  echo "Each Markdown file under 'content/' must include TOML frontmatter wrapped with +++ markers." >&2
  echo "Example:" >&2
  echo "+++" >&2
  echo 'title = "Page Title"' >&2
  echo "+++" >&2
  exit 1
fi

echo "All checked Markdown files have TOML frontmatter wrapped with +++." >&2
exit 0
