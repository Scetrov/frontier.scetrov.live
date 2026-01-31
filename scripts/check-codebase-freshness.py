#!/usr/bin/env python3
"""
Check documentation freshness against GitHub codebase.

Compares the 'date' field in documentation front matter against the last
commit date of the corresponding codebase file/directory on GitHub.

Requires: gh CLI (authenticated)
"""

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class DocPage:
    """Represents a documentation page with its metadata."""
    filepath: Path
    title: str
    date: datetime
    codebase_url: str
    is_draft: bool = False
    is_index: bool = False


@dataclass
class FreshnessResult:
    """Result of a freshness check for a single page."""
    page: DocPage
    codebase_last_commit: Optional[datetime]
    is_stale: bool
    error: Optional[str] = None


def parse_toml_frontmatter(content: str) -> dict:
    """Extract TOML front matter from markdown content."""
    match = re.match(r'^\+\+\+\s*\n(.*?)\n\+\+\+', content, re.DOTALL)
    if not match:
        return {}
    
    frontmatter = {}
    for line in match.group(1).strip().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"\'')
            frontmatter[key] = value
    
    return frontmatter


def parse_iso_date(date_str: str) -> datetime:
    """Parse ISO 8601 date string to datetime."""
    # Handle various ISO formats
    date_str = date_str.replace('Z', '+00:00')
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        # Fallback for dates without timezone
        return datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)


def extract_github_path(url: str) -> tuple[str, str, str]:
    """
    Extract owner, repo, and path from GitHub URL.
    
    Returns: (owner, repo, path)
    """
    # Handle blob URLs (files)
    blob_match = re.match(
        r'https://github\.com/([^/]+)/([^/]+)/blob/[^/]+/(.+)',
        url
    )
    if blob_match:
        return blob_match.groups()
    
    # Handle tree URLs (directories)
    tree_match = re.match(
        r'https://github\.com/([^/]+)/([^/]+)/tree/[^/]+/(.+)',
        url
    )
    if tree_match:
        return tree_match.groups()
    
    raise ValueError(f"Cannot parse GitHub URL: {url}")


# Cache for cloned repositories to avoid re-cloning
_repo_cache: dict[str, Path] = {}


def get_last_commit_date(codebase_url: str) -> datetime:
    """
    Get the last commit date for a file/directory.
    
    First tries the GitHub API via gh CLI. If that fails (e.g., 404 errors),
    falls back to cloning the repository and using local git.
    
    Raises an exception if both methods fail.
    """
    owner, repo, path = extract_github_path(codebase_url)
    
    # Try gh API first
    result = subprocess.run(
        [
            'gh', 'api',
            f'/repos/{owner}/{repo}/commits',
            '-q', '.[0].commit.committer.date',
            '-f', f'path={path}',
            '-f', 'per_page=1'
        ],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0 and result.stdout.strip():
        return parse_iso_date(result.stdout.strip())
    
    # Fallback: clone repo and use local git
    return get_last_commit_date_via_git(owner, repo, path)


def get_last_commit_date_via_git(owner: str, repo: str, path: str) -> datetime:
    """
    Get the last commit date by cloning the repo and using local git log.
    
    Caches cloned repos to avoid redundant clones.
    """
    import tempfile
    
    cache_key = f"{owner}/{repo}"
    
    if cache_key not in _repo_cache:
        # Clone to temp directory
        clone_dir = Path(tempfile.gettempdir()) / f"freshness-check-{owner}-{repo}"
        
        if clone_dir.exists():
            # Update existing clone
            subprocess.run(
                ['git', '-C', str(clone_dir), 'fetch', '--depth=50', 'origin', 'main'],
                capture_output=True,
                text=True
            )
            subprocess.run(
                ['git', '-C', str(clone_dir), 'reset', '--hard', 'origin/main'],
                capture_output=True,
                text=True
            )
        else:
            # Fresh clone
            clone_result = subprocess.run(
                ['gh', 'repo', 'clone', cache_key, str(clone_dir), '--', '--depth=50'],
                capture_output=True,
                text=True
            )
            if clone_result.returncode != 0:
                raise RuntimeError(f"Failed to clone {cache_key}: {clone_result.stderr}")
        
        _repo_cache[cache_key] = clone_dir
    
    clone_dir = _repo_cache[cache_key]
    
    # Get last commit date for the path
    log_result = subprocess.run(
        ['git', '-C', str(clone_dir), 'log', '-1', '--format=%cI', '--', path],
        capture_output=True,
        text=True
    )
    
    if log_result.returncode != 0:
        raise RuntimeError(f"git log failed for {path}: {log_result.stderr}")
    
    date_str = log_result.stdout.strip()
    if not date_str:
        raise RuntimeError(f"No commits found for path: {path}")
    
    return parse_iso_date(date_str)


def scan_documentation(base_path: Path) -> list[DocPage]:
    """Scan documentation directory for pages with codebase URLs."""
    pages = []
    
    for md_file in base_path.rglob('*.md'):
        content = md_file.read_text()
        frontmatter = parse_toml_frontmatter(content)
        
        if 'codebase' not in frontmatter or 'date' not in frontmatter:
            continue
        
        pages.append(DocPage(
            filepath=md_file,
            title=frontmatter.get('title', md_file.stem),
            date=parse_iso_date(frontmatter['date']),
            codebase_url=frontmatter['codebase'],
            is_draft=frontmatter.get('draft', '').lower() == 'true',
            is_index=md_file.name == '_index.md'
        ))
    
    return pages


def check_freshness(pages: list[DocPage], skip_indexes: bool = False) -> list[FreshnessResult]:
    """Check freshness of all pages against their codebase."""
    results = []
    
    for page in pages:
        if skip_indexes and page.is_index:
            continue
        
        try:
            last_commit = get_last_commit_date(page.codebase_url)
            is_stale = last_commit > page.date
            results.append(FreshnessResult(
                page=page,
                codebase_last_commit=last_commit,
                is_stale=is_stale
            ))
        except Exception as e:
            results.append(FreshnessResult(
                page=page,
                codebase_last_commit=None,
                is_stale=False,
                error=str(e)
            ))
    
    return results


def format_report(results: list[FreshnessResult]) -> str:
    """Format freshness results as a readable report."""
    lines = [
        "# Documentation Freshness Report",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
    ]
    
    stale = [r for r in results if r.is_stale]
    fresh = [r for r in results if not r.is_stale and r.error is None]
    errors = [r for r in results if r.error is not None]
    
    # Summary
    lines.extend([
        "## Summary",
        "",
        f"- **Total pages checked**: {len(results)}",
        f"- **Stale (needs review)**: {len(stale)}",
        f"- **Fresh**: {len(fresh)}",
        f"- **Errors**: {len(errors)}",
        "",
    ])
    
    # Stale pages
    if stale:
        lines.extend([
            "## 🔴 Pages Requiring Review",
            "",
            "| Page | Doc Date | Codebase Updated | Status |",
            "| ---- | -------- | ---------------- | ------ |",
        ])
        for r in sorted(stale, key=lambda x: x.codebase_last_commit or datetime.min, reverse=True):
            draft_flag = " [DRAFT]" if r.page.is_draft else ""
            lines.append(
                f"| {r.page.title}{draft_flag} | "
                f"{r.page.date.strftime('%Y-%m-%d')} | "
                f"{r.codebase_last_commit.strftime('%Y-%m-%d')} | "
                f"**STALE** |"
            )
        lines.append("")
    
    # Fresh pages
    if fresh:
        lines.extend([
            "## 🟢 Fresh Pages",
            "",
            "| Page | Doc Date | Codebase Updated | Status |",
            "| ---- | -------- | ---------------- | ------ |",
        ])
        for r in sorted(fresh, key=lambda x: x.page.title):
            draft_flag = " [DRAFT]" if r.page.is_draft else ""
            lines.append(
                f"| {r.page.title}{draft_flag} | "
                f"{r.page.date.strftime('%Y-%m-%d')} | "
                f"{r.codebase_last_commit.strftime('%Y-%m-%d')} | "
                f"OK |"
            )
    
    # Errors
    if errors:
        lines.extend([
            "## ⚠️ Errors",
            "",
        ])
        for r in errors:
            lines.append(f"- **{r.page.title}**: {r.error}")
        lines.append("")
    
    # Detailed stale page info for automation
    if stale:
        lines.extend([
            "## Stale Page Details (for automation)",
            "",
            "```json",
            json.dumps([
                {
                    "filepath": str(r.page.filepath),
                    "title": r.page.title,
                    "codebase_url": r.page.codebase_url,
                    "doc_date": r.page.date.isoformat(),
                    "codebase_date": r.codebase_last_commit.isoformat(),
                    "is_draft": r.page.is_draft
                }
                for r in stale
            ], indent=2),
            "```",
        ])
    
    return '\n'.join(lines)


def main():
    # Find the content directory relative to script location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    content_dir = repo_root / 'content' / 'develop' / 'world-contracts'
    
    if not content_dir.exists():
        print(f"Error: Content directory not found: {content_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning: {content_dir}", file=sys.stderr)
    
    pages = scan_documentation(content_dir)
    print(f"Found {len(pages)} pages with codebase URLs", file=sys.stderr)
    
    results = check_freshness(pages, skip_indexes=False)
    
    report = format_report(results)
    print(report)
    
    # Exit with error code if there are stale pages
    stale_count = sum(1 for r in results if r.is_stale)
    sys.exit(1 if stale_count > 0 else 0)


if __name__ == '__main__':
    main()
