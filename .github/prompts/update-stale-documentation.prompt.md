# Update Stale Documentation Prompt

This prompt guides the process of checking and updating documentation that has fallen behind the upstream codebase.

## Prerequisites

- Authenticated `gh` CLI (`gh auth status` should show logged in)
- Python 3.10+

## Step 1: Set Up Environment and Run Freshness Check

Run the following commands in the terminal:

```bash
cd /home/scetrov/source/frontier.scetrov.live

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# No external dependencies needed - script uses gh CLI

# Run the freshness check
python scripts/check-codebase-freshness.py | tee freshness-report.md
```

## Step 2: Review the Report

The script outputs a Markdown report with:

1. **Summary** - Count of stale, fresh, and errored pages
2. **Pages Requiring Review** - Table of stale documentation with dates
3. **Stale Page Details** - JSON block for automation

If all pages are fresh, the script exits with code 0 and no further action is needed.

## Step 3: Update Stale Pages

For each page listed in "Pages Requiring Review":

### 3.1 Fetch the Current Codebase

Use the `codebase` URL from the report to view the current source:

```bash
# Example for a specific file
gh api /repos/evefrontier/world-contracts/contents/contracts/world/sources/primitives/energy.move \
  -q '.content' | base64 -d
```

Or clone/update the repository locally:

```bash
gh repo clone evefrontier/world-contracts /tmp/world-contracts -- --depth 1
```

### 3.2 Compare and Update Documentation

For each stale page:

1. Open the documentation file in the editor
2. Review the corresponding source file for changes since the `doc_date`
3. Update the documentation to reflect:
   - New functions or types
   - Changed function signatures
   - Updated behavior or semantics
   - New examples or use cases
4. Update the `date` field in front matter to today's date
5. Verify Mermaid diagrams still accurately represent the code

### 3.3 Validation Checklist

For each updated page, ensure:

- [ ] All code examples compile/are syntactically correct
- [ ] Mermaid diagrams render correctly
- [ ] Cross-references to other docs are still valid
- [ ] The `date` field is updated to today
- [ ] No breaking changes to existing links

## Step 4: Build and Verify

```bash
# Build the site to check for errors
hugo build

# Serve locally and review changes
hugo serve
```

## Step 5: Commit Changes

```bash
git add content/develop/world-contracts/
git commit -m "docs: update world-contracts documentation for codebase changes"
```

## Automation Tips

The JSON block in the report can be used to iterate programmatically:

```bash
# Extract stale files from report
cat freshness-report.md | sed -n '/```json/,/```/p' | sed '1d;$d' | jq -r '.[].filepath'
```

## Troubleshooting

### "gh CLI error: ..." or API 404s

The GitHub commits API sometimes returns 404 for valid paths. The script automatically falls back to cloning the repository locally and using `git log` when the API fails. Ensure you're authenticated:

```bash
gh auth status
gh auth login  # if needed
```

The fallback clone is cached in `/tmp/freshness-check-{owner}-{repo}` to avoid redundant downloads.

### "No commits found for path"

The file may have been moved or deleted. Check the repository manually:

```bash
gh browse evefrontier/world-contracts
```

### Rate limiting

The script makes one API call per page. If rate-limited, the script will fall back to local git clones which are not rate-limited.
