---
name: update-world-contracts-version-comparison
description: Refresh the source-pinned World Contracts v0/main versus dev comparison with canonical upstream provenance and fail-closed review validation.
---

# Update World Contracts Version Comparison

Run this workflow from the documentation repository root. It is comparison-specific: do not replace it with date-only freshness checks. Preserve unrelated worktree changes.

## Setup and canonical candidates

```bash
set -euo pipefail
root="$(git rev-parse --show-toplevel)"
workflow="$root/tmp/update-world-contracts-version-comparison"
repo="$workflow/world-contracts"
chapter="$root/content/develop/world-contracts/version-comparison"
coverage="$root/data/world-contracts-version-comparison/coverage.toml"
plan="$workflow/plan.json"
inventory="$workflow/inventory.json"
mkdir -p "$workflow"
git clone --no-checkout https://github.com/evefrontier/world-contracts.git "$repo"
python3 "$root/scripts/update-world-contracts-version-comparison.py" plan \
  --chapter "$chapter" --repo "$repo" > "$plan"
python3 "$root/scripts/update-world-contracts-version-comparison.py" inventory \
  --chapter "$chapter" --repo "$repo" > "$inventory"
```

The helper verifies the canonical `evefrontier/world-contracts` origin, fetches `main` and `dev`, and reads only freshly fetched `origin/main` and `origin/dev`. If any command fails, stop without editing the cursor and report its output. Temporary repositories set their own noninteractive identity and signing controls only in tests; do not alter user or project signing policy.

## Review and coverage

Read `mode` from `"$plan"`. For `incremental`, review each recorded-cursor-to-candidate range and the candidate tip-to-tip range. For `full-rebaseline`, retain the prior cursor as historical context, regenerate inventories, and re-check every claim and coverage disposition; never use non-ancestor cursor SHAs as incremental bases.

Use immutable GitHub links only. Keep source modules, tests, and `contracts/archive/` separate. Update `"$coverage"` so every generated `v0_module`, `active_module`, `archived_module`, and `changed_path` has one exact `path`, an allowed `state`, and a meaningful `disposition`. Archived paths cannot satisfy active coverage.

A no-op plan has candidates identical to the cursor: do not edit documentation, but still record that the final-ref check was stable. Source proves implementation only; manifests prove only named deployment facts.

## Transactional completion

Save the old cursor before edits, then create the candidate file and run the authoritative complete validation:

```bash
cursor_backup="$workflow/_index.md.before"
cp "$chapter/_index.md" "$cursor_backup"
python3 - "$plan" "$workflow/reviewed-candidates.json" <<'PY'
import json, pathlib, sys
plan = json.loads(pathlib.Path(sys.argv[1]).read_text())
pathlib.Path(sys.argv[2]).write_text(json.dumps({"candidates": plan["candidates"]}, indent=2) + "\n")
PY
candidates="$workflow/reviewed-candidates.json"
python3 "$root/scripts/update-world-contracts-version-comparison.py" validate \
  --chapter "$chapter" --repo "$repo" --coverage "$coverage" \
  --inventory-file "$inventory" --reviewed-candidates-file "$candidates"
python3 "$root/scripts/update-world-contracts-version-comparison.py" final-refs \
  --chapter "$chapter" --repo "$repo" --reviewed-candidates-file "$candidates" \
  > "$workflow/final-refs.json"
```

Only after complete validation succeeds may the cursor be changed to the reviewed candidates. If any post-cursor check fails, restore it with `cp "$cursor_backup" "$chapter/_index.md"` and stop. If `final-refs.json` reports `pending`, preserve the reviewed candidate cursor, report the newer heads as pending work, and do not substitute them.

## Required checks and report

```bash
python3 -m unittest scripts/tests/test_update_world_contracts_version_comparison.py
hugo build -d public
npm run lint:md
./.githooks/validate-frontmatter.sh
npm run spell
htmltest -c .htmltest.yml -s public
```

Report review mode; old cursor; reviewed candidates; final heads and pending movement; changed pages; all commands/results; every changed-path disposition; contradictions; deployment/runtime uncertainty; and residual risks. Remove only `"$workflow"` after retaining requested reports: `rm -rf "$workflow"`.
