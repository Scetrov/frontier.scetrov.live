#!/usr/bin/env python3
"""Lint all mermaid diagrams in content/ markdown files using mermaid-cli (mmdc).

Exit code 0 if all diagrams are valid, 1 if any fail to parse.
Requires: @mermaid-js/mermaid-cli (installed via npm install)
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

CONTENT_DIR = os.environ.get("CONTENT_DIR", "content")
PATTERN = re.compile(r"```mermaid\s*\n(.*?)\n```", re.DOTALL)
MAX_WORKERS = int(os.environ.get("MERMAID_WORKERS", "4"))

# Resolve the mmdc binary: prefer the local node_modules install to avoid
# the heavy per-invocation overhead of `npx -y`.
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_SCRIPT_DIR)
_LOCAL_MMDC = os.path.join(_REPO_ROOT, "node_modules", ".bin", "mmdc")
MMDC_CMD = _LOCAL_MMDC if os.path.isfile(_LOCAL_MMDC) else shutil.which("mmdc") or "mmdc"


def find_diagrams(content_dir):
    """Extract all mermaid code blocks from .md files."""
    results = []
    for root, _dirs, files in os.walk(content_dir):
        for fname in sorted(files):
            if not fname.endswith(".md"):
                continue
            path = os.path.join(root, fname)
            with open(path) as fh:
                text = fh.read()
            for match in PATTERN.finditer(text):
                diagram = match.group(1).strip()
                lineno = text[: match.start()].count("\n") + 2
                results.append((path, lineno, diagram))
    return results


def validate_diagram(diagram, tmpdir, idx):
    """Run mmdc on a single diagram. Returns error string or None."""
    infile = os.path.join(tmpdir, f"{idx}.mmd")
    outfile = os.path.join(tmpdir, f"{idx}.svg")
    with open(infile, "w") as fh:
        fh.write(diagram)
    try:
        result = subprocess.run(
            [MMDC_CMD, "-i", infile, "-o", outfile],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            lines = [
                l
                for l in result.stderr.strip().split("\n")
                if any(
                    kw in l.lower()
                    for kw in ("error", "parse", "expect", "syntax", "token")
                )
            ]
            return "\n".join(lines[:5]) if lines else result.stderr.strip()[:300]
        return None
    except FileNotFoundError:
        print(
            f"ERROR: mermaid-cli not found at '{MMDC_CMD}'.\n"
            "Run 'npm install' in the repo root to install it.",
            file=sys.stderr,
        )
        sys.exit(2)
    except subprocess.TimeoutExpired:
        return "Timed out after 60s"
    finally:
        for f in (infile, outfile):
            if os.path.exists(f):
                os.unlink(f)


def main():
    diagrams = find_diagrams(CONTENT_DIR)
    print(f"Found {len(diagrams)} mermaid diagram(s)")

    if not diagrams:
        return 0

    tmpdir = tempfile.mkdtemp()
    errors = []

    print(f"Validating with {MAX_WORKERS} parallel worker(s) using: {MMDC_CMD}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(validate_diagram, diagram, tmpdir, idx): (path, lineno)
            for idx, (path, lineno, diagram) in enumerate(diagrams)
        }
        for future in as_completed(futures):
            path, lineno = futures[future]
            err = future.result()
            if err:
                errors.append((path, lineno, err))

    try:
        os.rmdir(tmpdir)
    except OSError:
        pass

    if errors:
        print(f"\n{len(errors)} diagram(s) failed:\n")
        for path, lineno, err in errors:
            print(f"  {path}:{lineno}")
            print(f"    {err}\n")
        return 1

    print("All diagrams valid!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
