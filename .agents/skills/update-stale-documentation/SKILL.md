---
name: update-stale-documentation
description: Checks this repository's documentation against upstream code, updates only verified stale pages and metadata, and validates Markdown, Mermaid, links, and the Hugo site. Use when asked to run the documentation freshness workflow or refresh stale world-contracts docs.
---

# Update Stale Documentation

Run every command from the repository root. Keep clones, reports, and other temporary data under a workflow-specific directory inside `./tmp`; never use shared `/tmp`.

## Prerequisites

Before editing anything:

```bash
command -v gh
command -v python3
command -v hugo
gh auth status
python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'
test -f scripts/check-codebase-freshness.py
mkdir -p "./tmp/update-stale-documentation/cache"
```

If a command is missing, GitHub authentication fails, Python is older than 3.10, or the script is absent, stop and report the failed check plus a safe installation, login, or path-remediation step. Do not make partial documentation edits.

## Run the Freshness Check

The script's fallback uses Python's temporary directory. Scope that directory explicitly to this repository:

```bash
repo_root="$(git rev-parse --show-toplevel)"
work_dir="$repo_root/tmp/update-stale-documentation"
mkdir -p "$work_dir/cache"
set -o pipefail
set +e
TMPDIR="$work_dir/cache" python3 "$repo_root/scripts/check-codebase-freshness.py" \
  | tee "$work_dir/freshness-report.md"
check_status="${PIPESTATUS[0]}"
set -e
```

Review the report summary, **Pages Requiring Review** table, errors, and JSON automation block. The script intentionally exits `1` when it finds stale pages, so accept status `1` only when a complete report identifies stale pages and no execution errors. Status `0` means the report found no stale pages. For any other status, or status `1` without a valid stale-page report, stop and diagnose the failure. Do not treat errored pages as fresh.

If all pages are fresh and there are no errors, make no documentation edits, report that no update is required, and proceed only to scoped cleanup.

## Review and Update Stale Pages

For each stale page:

1. Read its documentation file, `doc_date`, and `codebase` URL from the report.
2. Fetch the current upstream file with authenticated `gh api`, or clone/update its repository beneath `"$work_dir/cache"`. Quote all derived URLs and paths. For example:

   ```bash
   gh api "/repos/evefrontier/world-contracts/contents/contracts/world/sources/primitives/energy.move" \
     --jq '.content' | base64 --decode
   gh repo clone "evefrontier/world-contracts" \
     "$work_dir/cache/world-contracts" -- --depth 1
   ```

3. Compare source history and current source with the documented behavior since `doc_date`. Update only content proven stale: functions and types, signatures, semantics, examples, use cases, and affected cross-references.
4. Set the page's frontmatter `date` to today's date only when substantive source-backed updates were made.
5. Verify each code example is syntactically correct, every Mermaid diagram still matches the implementation, cross-references resolve, and existing links remain stable.
6. Keep changes scoped to the pages identified by the report unless a directly affected shared reference also requires correction. Explain every extra file.

If an upstream file moved or was deleted, confirm its location manually (for example, `gh browse "owner/repository"`) and report uncertainty rather than inventing replacement behavior.

## Validate

Run the repository checks after edits:

```bash
make build
make lint-md
make lint-mermaid
```

If available and appropriate, run `hugo serve` for manual review, then stop the server cleanly. Report the exact failing check and relevant output for any failure. Do not claim completion or commit changes while validation fails.

Review `git diff -- content/` and confirm that only verified documentation updates and metadata are present. Commit only if the user explicitly asks; use a conventional `docs:` commit message.

## Cleanup

After preserving any report the user requested, remove only this workflow's directory:

```bash
rm -rf "$(git rev-parse --show-toplevel)/tmp/update-stale-documentation"
```

Never remove all of `./tmp`, another workflow's cache, or a shared system temporary directory.
