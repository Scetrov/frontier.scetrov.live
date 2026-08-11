#!/usr/bin/env python3
"""Plan and fail-closed validate World Contracts comparison reviews."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse

CURSOR_FIELDS = frozenset({"comparison_schema", "upstream_repository", "comparison_mode", "v0_ref", "v0_reviewed_commit", "v1_ref", "v1_reviewed_commit", "merge_base_commit", "reviewed_at", "review_status"})
SHA = re.compile(r"^[0-9a-f]{40}$")
URL = re.compile(r"https://github\.com/evefrontier/world-contracts/(?:blob|tree)/[0-9a-f]{40}(?:/[^\s)>]*)?")
CANONICAL_REPOSITORY = "evefrontier/world-contracts"
STATES = frozenset({"active-v1", "redesigned", "partial", "archived-only", "not-yet-ported", "main-only", "deployment-unknown"})


class ValidationError(ValueError):
    """Raised for input that cannot safely represent a completed review."""


@dataclass(frozen=True)
class Baseline:
    path: str
    upstream_repository: str
    v0_ref: str
    v0_reviewed_commit: str
    v1_ref: str
    v1_reviewed_commit: str
    merge_base_commit: str
    reviewed_at: str
    review_status: str


def frontmatter(path: Path) -> tuple[dict, str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValidationError(f"cannot read {path}: {exc}") from exc
    if not text.startswith("+++\n"):
        raise ValidationError(f"{path}: missing TOML frontmatter")
    end = text.find("\n+++", 4)
    if end == -1:
        raise ValidationError(f"{path}: unterminated TOML frontmatter")
    try:
        data = tomllib.loads(text[4:end])
    except tomllib.TOMLDecodeError as exc:
        raise ValidationError(f"{path}: malformed TOML frontmatter: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: frontmatter must be a TOML table")
    return data, text[end + 4:]


def parse_utc(value: object) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValidationError("reviewed_at must be an ISO-8601 UTC timestamp ending in Z")
    try:
        dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError("reviewed_at must be a valid ISO-8601 UTC timestamp") from exc
    return value


def validate_metadata(chapter: Path) -> Baseline:
    pages = sorted(chapter.rglob("*.md"))
    if not pages:
        raise ValidationError(f"{chapter}: no Markdown comparison pages")
    cursors: list[tuple[Path, dict]] = []
    for page in pages:
        data, _ = frontmatter(page)
        present = CURSOR_FIELDS.intersection(data)
        if present:
            if present != CURSOR_FIELDS:
                raise ValidationError(f"{page}: incomplete comparison cursor")
            cursors.append((page, data))
    if len(cursors) != 1:
        raise ValidationError(f"expected exactly one comparison cursor, found {len(cursors)}")
    path, data = cursors[0]
    if path.name != "_index.md":
        raise ValidationError("the canonical comparison cursor must be in _index.md")
    required = {"comparison_schema": 1, "upstream_repository": CANONICAL_REPOSITORY, "comparison_mode": "tip-to-tip", "v0_ref": "main", "v1_ref": "dev", "review_status": "complete"}
    for key, expected in required.items():
        if data.get(key) != expected:
            raise ValidationError(f"{path}: {key} must be {expected!r}")
    for key in ("v0_reviewed_commit", "v1_reviewed_commit", "merge_base_commit"):
        if not isinstance(data.get(key), str) or not SHA.fullmatch(data[key]):
            raise ValidationError(f"{path}: {key} must be a lowercase 40-hex commit")
    reviewed_at = parse_utc(data.get("reviewed_at"))
    return Baseline(str(path), *(data[key] for key in ("upstream_repository", "v0_ref", "v0_reviewed_commit", "v1_ref", "v1_reviewed_commit", "merge_base_commit")), reviewed_at, data["review_status"])


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repo), *args], check=False, capture_output=True, text=True)
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or f"exit status {result.returncode}"
        raise ValidationError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def normalize_remote(value: str) -> str:
    value = value.strip()
    forms = (r"https://github\.com/evefrontier/world-contracts(?:\.git)?/?$", r"ssh://git@github\.com/evefrontier/world-contracts(?:\.git)?/?$", r"git@github\.com:evefrontier/world-contracts(?:\.git)?$")
    if any(re.fullmatch(form, value, flags=re.IGNORECASE) for form in forms):
        return CANONICAL_REPOSITORY
    raise ValidationError(f"origin remote must identify {CANONICAL_REPOSITORY}, got {value!r}")


def verify_repository(repo: Path, baseline: Baseline) -> None:
    if baseline.upstream_repository != CANONICAL_REPOSITORY:
        raise ValidationError("comparison metadata names a non-canonical repository")
    normalize_remote(run_git(repo, "config", "--get", "remote.origin.url"))


def fetch_declared_refs(repo: Path, baseline: Baseline) -> None:
    verify_repository(repo, baseline)
    run_git(repo, "fetch", "--no-tags", "origin", f"+refs/heads/{baseline.v0_ref}:refs/remotes/origin/{baseline.v0_ref}", f"+refs/heads/{baseline.v1_ref}:refs/remotes/origin/{baseline.v1_ref}")


def resolve(repo: Path, ref: str) -> str:
    """Resolve only a freshly fetched canonical remote-tracking ref."""
    sha = run_git(repo, "rev-parse", "--verify", f"refs/remotes/origin/{ref}^{{commit}}")
    if not SHA.fullmatch(sha):
        raise ValidationError(f"origin/{ref}: non-SHA commit result")
    return sha


def require_commit(repo: Path, sha: str, label: str) -> None:
    if not isinstance(sha, str) or not SHA.fullmatch(sha):
        raise ValidationError(f"{label} must be a lowercase 40-hex commit")
    run_git(repo, "cat-file", "-e", f"{sha}^{{commit}}")


def is_ancestor(repo: Path, older: str, newer: str) -> bool:
    result = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", older, newer], check=False, capture_output=True, text=True)
    if result.returncode not in (0, 1):
        raise ValidationError(f"cannot check ancestry: {result.stderr.strip()}")
    return result.returncode == 0


def plan_review(repo: Path, baseline: Baseline) -> dict:
    fetch_declared_refs(repo, baseline)
    for sha, label in ((baseline.v0_reviewed_commit, "v0_reviewed_commit"), (baseline.v1_reviewed_commit, "v1_reviewed_commit"), (baseline.merge_base_commit, "merge_base_commit")):
        require_commit(repo, sha, label)
    v0, v1 = resolve(repo, baseline.v0_ref), resolve(repo, baseline.v1_ref)
    base = run_git(repo, "merge-base", v0, v1)
    v0_ok, v1_ok = is_ancestor(repo, baseline.v0_reviewed_commit, v0), is_ancestor(repo, baseline.v1_reviewed_commit, v1)
    return {"mode": "incremental" if v0_ok and v1_ok else "full-rebaseline", "candidates": {"v0": v0, "v1": v1, "merge_base": base}, "previous": asdict(baseline), "ranges": {"v0": f"{baseline.v0_reviewed_commit}..{v0}", "v1": f"{baseline.v1_reviewed_commit}..{v1}", "tip_to_tip": f"{v0}...{v1}"} if v0_ok and v1_ok else {}}


def is_test_path(path: str) -> bool:
    return any(part in {"test", "tests"} for part in Path(path).parts)


def inventory(repo: Path, v0: str, v1: str) -> dict:
    def files(ref: str) -> list[str]:
        return sorted(run_git(repo, "ls-tree", "-r", "--name-only", ref).splitlines())
    def modules(ref: str) -> tuple[list[str], list[str], list[str]]:
        paths = [path for path in files(ref) if path.endswith(".move")]
        archived = [path for path in paths if path.startswith("contracts/archive/")]
        tests = [path for path in paths if is_test_path(path)]
        sources = [path for path in paths if path not in archived and path not in tests]
        return sources, tests, archived
    v0_sources, v0_tests, _ = modules(v0)
    v1_sources, v1_tests, v1_archived = modules(v1)
    return {"v0_move_modules": v0_sources, "v0_move_tests": v0_tests, "v1_active_move_modules": v1_sources, "v1_move_tests": v1_tests, "v1_archive_move_modules": v1_archived, "tip_to_tip_changed_files": sorted(run_git(repo, "diff", "--name-only", v0, v1).splitlines())}


def load_json(path: Path, label: str) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"{label} {path}: malformed JSON: {exc}") from exc


def load_toml(path: Path) -> dict:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ValidationError(f"coverage {path}: malformed TOML: {exc}") from exc
    if not isinstance(data, dict):
        raise ValidationError(f"coverage {path}: root must be a table")
    return data


def require_records(data: dict, key: str, required_paths: list[str], kind: str) -> None:
    rows = data.get(key)
    if not isinstance(rows, list):
        raise ValidationError(f"coverage: {key} must be an array")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("path"), str) or not isinstance(row.get("state"), str) or not isinstance(row.get("disposition"), str) or not row["disposition"].strip():
            raise ValidationError(f"coverage: every {key} record needs string path, state, and disposition")
        if row["state"] not in STATES:
            raise ValidationError(f"coverage: invalid state {row['state']!r}")
        path = row["path"]
        if path in seen:
            raise ValidationError(f"coverage: duplicate {key} mapping for {path}")
        seen.add(path)
        if key == "active_module" and path.startswith("contracts/archive/"):
            raise ValidationError(f"coverage: archived module cannot be active: {path}")
    expected = set(required_paths)
    if seen != expected:
        missing, extra = sorted(expected - seen), sorted(seen - expected)
        raise ValidationError(f"coverage: {key} mappings do not exactly match inventory (missing: {', '.join(missing) or 'none'}; extra: {', '.join(extra) or 'none'})")


def validate_cursor_candidates(repo: Path, baseline: Baseline, candidates_file: Path) -> dict:
    data = load_json(candidates_file, "reviewed candidates")
    if not isinstance(data, dict) or not isinstance(data.get("candidates", data), dict):
        raise ValidationError("reviewed candidates must contain a candidates object")
    actual = data.get("candidates", data)
    expected = {"v0": baseline.v0_reviewed_commit, "v1": baseline.v1_reviewed_commit, "merge_base": baseline.merge_base_commit}
    if actual != expected or any(not isinstance(value, str) for value in actual.values()):
        raise ValidationError("canonical cursor does not match the reviewed candidates")
    for key, sha in actual.items():
        require_commit(repo, sha, f"candidate {key}")
    merge_base = run_git(repo, "merge-base", actual["v0"], actual["v1"])
    if merge_base != actual["merge_base"]:
        raise ValidationError("canonical cursor merge base differs from reviewed candidates")
    return actual


def validate_inventory_coverage(inventory_file: Path, coverage: Path) -> None:
    data = load_json(inventory_file, "inventory")
    if not isinstance(data, dict):
        raise ValidationError("inventory must be a JSON object")
    required_lists = ("v0_move_modules", "v1_active_move_modules", "v1_archive_move_modules", "tip_to_tip_changed_files")
    for key in required_lists:
        if not isinstance(data.get(key), list) or any(not isinstance(value, str) for value in data[key]):
            raise ValidationError(f"inventory: {key} must be a list of paths")
    coverage_data = load_toml(coverage)
    require_records(coverage_data, "v0_module", data["v0_move_modules"], "v0")
    require_records(coverage_data, "active_module", data["v1_active_move_modules"], "active-v1")
    require_records(coverage_data, "archived_module", data["v1_archive_move_modules"], "archived-v1")
    require_records(coverage_data, "changed_path", data["tip_to_tip_changed_files"], "changed")


def validate_evidence(repo: Path, baseline: Baseline, chapter: Path) -> None:
    permitted = {baseline.v0_reviewed_commit, baseline.v1_reviewed_commit, baseline.merge_base_commit}
    for page in sorted(chapter.rglob("*.md")):
        _, body = frontmatter(page)
        for url in URL.findall(body):
            parsed = urlparse(url)
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 4 or parts[0:2] != ["evefrontier", "world-contracts"] or parts[2] not in {"blob", "tree"}:
                raise ValidationError(f"{page}: invalid evidence URL: {url}")
            sha, path = parts[3], "/".join(parts[4:])
            if sha not in permitted:
                raise ValidationError(f"{page}: evidence URL uses a commit outside the cursor: {url}")
            if not path:
                raise ValidationError(f"{page}: evidence URL has no repository path: {url}")
            run_git(repo, "cat-file", "-e", f"{sha}:{path}")


def final_refs(repo: Path, baseline: Baseline, candidates_file: Path) -> dict:
    candidates = validate_cursor_candidates(repo, baseline, candidates_file)
    fetch_declared_refs(repo, baseline)
    heads = {"v0": resolve(repo, baseline.v0_ref), "v1": resolve(repo, baseline.v1_ref)}
    pending = {key: value for key, value in heads.items() if value != candidates[key]}
    return {"candidates": candidates, "heads": heads, "pending": pending, "stable": not pending}


def validate_complete(chapter: Path, repo: Path | None, coverage: Path | None, inventory_file: Path | None, candidates_file: Path | None) -> None:
    if repo is None or coverage is None or inventory_file is None or candidates_file is None:
        raise ValidationError("completed validation requires --repo, --coverage, --inventory-file, and --reviewed-candidates-file")
    baseline = validate_metadata(chapter)
    verify_repository(repo, baseline)
    validate_cursor_candidates(repo, baseline, candidates_file)
    validate_inventory_coverage(inventory_file, coverage)
    validate_evidence(repo, baseline, chapter)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("validate", "plan", "inventory", "final-refs"))
    parser.add_argument("--chapter", type=Path, required=True)
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--coverage", type=Path)
    parser.add_argument("--inventory-file", type=Path)
    parser.add_argument("--reviewed-candidates-file", type=Path)
    args = parser.parse_args()
    try:
        baseline = validate_metadata(args.chapter)
        if args.command == "validate":
            validate_complete(args.chapter, args.repo, args.coverage, args.inventory_file, args.reviewed_candidates_file)
            output = {"baseline": asdict(baseline), "valid": True}
        elif args.command == "plan":
            if args.repo is None: raise ValidationError("--repo is required for plan")
            output = plan_review(args.repo, baseline)
        elif args.command == "inventory":
            if args.repo is None: raise ValidationError("--repo is required for inventory")
            plan = plan_review(args.repo, baseline)
            output = inventory(args.repo, plan["candidates"]["v0"], plan["candidates"]["v1"])
        else:
            if args.repo is None or args.reviewed_candidates_file is None: raise ValidationError("final-refs requires --repo and --reviewed-candidates-file")
            output = final_refs(args.repo, baseline, args.reviewed_candidates_file)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 0
    except KeyboardInterrupt:
        print("error: validation interrupted; no cursor was changed", file=sys.stderr)
        return 130
    except (OSError, ValidationError, tomllib.TOMLDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
