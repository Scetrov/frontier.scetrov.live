#!/usr/bin/env python3
"""
Generate an Insomnia 5.0 collection YAML from a Swagger 2.0 JSON spec.

Reads: data/world-api-stillness.json
Writes to stdout (pipe to file or use Makefile target)

Usage:
    python3 scripts/generate-insomnia-collection.py > data/insomnia-collection.yaml
"""

import hashlib
import json
import sys
import textwrap
from pathlib import Path
from typing import Any


def md5_id(prefix: str, seed: str) -> str:
    """Generate a deterministic Insomnia-style ID from a seed string."""
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"{prefix}_{h}"


def resolve_ref(spec: dict, ref: str) -> dict | None:
    """Resolve a $ref string like '#/definitions/v1.ERC2771' to its definition."""
    if not ref.startswith("#/definitions/"):
        return None
    name = ref[len("#/definitions/"):]
    return spec.get("definitions", {}).get(name)


def generate_sample_json(spec: dict, schema: dict, depth: int = 0) -> Any:
    """Generate a sample JSON value from a Swagger schema definition."""
    if depth > 4:
        return {}

    if "$ref" in schema:
        resolved = resolve_ref(spec, schema["$ref"])
        if resolved:
            return generate_sample_json(spec, resolved, depth + 1)
        return {}

    schema_type = schema.get("type", "object")

    if schema_type == "string":
        if "enum" in schema:
            return schema["enum"][0]
        return "string"
    elif schema_type == "integer":
        return 0
    elif schema_type == "number":
        return 0
    elif schema_type == "boolean":
        return False
    elif schema_type == "array":
        items = schema.get("items", {})
        return [generate_sample_json(spec, items, depth + 1)]
    elif schema_type == "object" or "properties" in schema:
        props = schema.get("properties", {})
        if not props and "additionalProperties" in schema:
            return {}
        obj = {}
        for field, field_schema in props.items():
            obj[field] = generate_sample_json(spec, field_schema, depth + 1)
        return obj

    return {}


def yaml_escape(s: str) -> str:
    """Escape a string for YAML output, quoting if necessary."""
    if not s:
        return '""'
    # Check if the string needs quoting
    needs_quote = any(c in s for c in ':{}[]&*?|>!%@`#,\n') or s.startswith("- ")
    if needs_quote:
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def format_url_path(path: str, params: list[dict]) -> str:
    """Format the URL path, replacing {param} with example values or Insomnia vars."""
    url_path = path
    for param in params:
        if param.get("in") == "path":
            example = param.get("example", "")
            if example:
                url_path = url_path.replace(
                    "{" + param["name"] + "}", str(example)
                )
            else:
                url_path = url_path.replace(
                    "{" + param["name"] + "}",
                    "{{ _." + param["name"] + " }}",
                )
    return url_path


def indent(text: str, level: int) -> str:
    """Indent a multi-line string by a given number of spaces."""
    prefix = " " * level
    return "\n".join(prefix + line for line in text.split("\n"))


def generate_request_yaml(
    spec: dict,
    path: str,
    method: str,
    op: dict,
    sort_key: int,
) -> str:
    """Generate YAML for a single Insomnia request entry."""
    params = op.get("parameters", [])
    url_path = format_url_path(path, params)
    req_id = md5_id("req", f"{method}:{path}")
    summary = op.get("summary", f"{method.upper()} {path}")
    description = op.get("description", "")
    has_security = bool(op.get("security"))

    lines = []
    lines.append(f"      - url: >-")
    lines.append(f"            {{{{ _.base_url }}}}{url_path}")
    lines.append(f"        name: {summary}")
    lines.append(f"        meta:")
    lines.append(f"          id: {req_id}")
    lines.append(f"          created: 1749660554120")
    lines.append(f"          modified: 1749660554120")
    lines.append(f"          isPrivate: false")
    if description:
        # Handle multi-line descriptions
        desc_lines = description.strip().split("\n")
        if len(desc_lines) == 1:
            lines.append(f"          description: {yaml_escape(desc_lines[0])}")
        else:
            lines.append(f"          description: |-")
            for dl in desc_lines:
                lines.append(f"            {dl}")
    lines.append(f"          sortKey: {sort_key}")
    lines.append(f"        method: {method.upper()}")

    # Body for POST/PUT/PATCH
    if method.upper() in ("POST", "PUT", "PATCH"):
        body_param = next(
            (p for p in params if p.get("in") == "body"), None
        )
        if body_param and "schema" in body_param:
            sample = generate_sample_json(spec, body_param["schema"])
            body_json = json.dumps(sample, indent=2)
            consumes = op.get("consumes", ["application/json"])
            mime = consumes[0] if consumes else "application/json"
            lines.append(f"        body:")
            lines.append(f"          mimeType: {mime}")
            lines.append(f"          text: |-")
            for bl in body_json.split("\n"):
                lines.append(f"            {bl}")
            lines.append(f"        headers:")
            lines.append(f"          - name: Content-Type")
            lines.append(f"            disabled: false")
            lines.append(f"            value: {mime}")

    # Query parameters
    query_params = [p for p in params if p.get("in") == "query"]
    if query_params:
        lines.append(f"        parameters:")
        for qp in query_params:
            example = qp.get("example", "")
            lines.append(f"          - name: {qp['name']}")
            lines.append(f"            disabled: true")
            lines.append(f'            value: "{example}"')

    # Auth headers for secured endpoints
    if has_security:
        # Only add headers section if we didn't already add it for body
        if method.upper() not in ("POST", "PUT", "PATCH") or not next(
            (p for p in params if p.get("in") == "body"), None
        ):
            lines.append(f"        headers:")
        lines.append(f"          - name: Authorization")
        lines.append(f"            disabled: false")
        lines.append(f"            value: >-")
        lines.append(f"              {{{{ _.api_key }}}}")

    # Settings (always the same)
    lines.append(f"        settings:")
    lines.append(f"          renderRequestBody: true")
    lines.append(f"          encodeUrl: true")
    lines.append(f"          followRedirects: global")
    lines.append(f"          cookies:")
    lines.append(f"            send: true")
    lines.append(f"            store: true")
    lines.append(f"          rebuildPath: true")

    return "\n".join(lines)


def generate_collection(spec: dict) -> str:
    """Generate the full Insomnia 5.0 collection YAML from a Swagger spec."""
    version = spec.get("info", {}).get("version", "unknown")
    tag_order = ["meta", "chain", "game"]

    # Group endpoints by tag
    tags: dict[str, list[tuple[str, str, dict]]] = {}
    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict) or "responses" not in op:
                continue
            op_tags = op.get("tags", ["other"])
            for tag in op_tags:
                tags.setdefault(tag, []).append((path, method, op))

    # Sort endpoints within each tag by path then method
    for tag in tags:
        tags[tag].sort(key=lambda x: (x[0], x[1]))

    # Determine if any tag has secured endpoints (for folder-level auth)
    secured_tags = set()
    for tag, endpoints in tags.items():
        for _path, _method, op in endpoints:
            if op.get("security"):
                secured_tags.add(tag)

    lines = []
    lines.append("type: collection.insomnia.rest/5.0")
    lines.append(f"name: EVE Frontier World API ({version})")
    lines.append("meta:")
    lines.append(f"  id: {md5_id('wrk', 'world-api-collection')}")
    lines.append("  created: 1749660438111")
    lines.append("  modified: 1749660438111")
    lines.append("collection:")

    sort_counter = -1749660554120

    # Render known tags first, then any extras
    all_tags = list(tag_order)
    for t in tags:
        if t not in all_tags:
            all_tags.append(t)

    for tag in all_tags:
        if tag not in tags:
            continue
        endpoints = tags[tag]
        fld_id = md5_id("fld", f"folder:{tag}")

        lines.append(f"  - name: {tag}")
        lines.append(f"    meta:")
        lines.append(f"      id: {fld_id}")
        lines.append(f"      created: 1749660554120")
        lines.append(f"      modified: 1749660554120")
        lines.append(f"      sortKey: {sort_counter}")
        sort_counter -= 1
        lines.append(f"    children:")

        for i, (path, method, op) in enumerate(endpoints):
            req_sort = sort_counter - i
            req_yaml = generate_request_yaml(spec, path, method, op, req_sort)
            lines.append(req_yaml)

        # Folder-level authentication for tags with secured endpoints
        if tag in secured_tags:
            lines.append(f"    authentication:")
            lines.append(f"      type: bearer")
            lines.append(f"      token: >-")
            lines.append(f"        {{{{ _.api_key }}}}")

    # Cookie jar
    lines.append("cookieJar:")
    lines.append("  name: Default Jar")
    lines.append("  meta:")
    lines.append(f"    id: {md5_id('jar', 'default-cookie-jar')}")
    lines.append("    created: 1749660438113")
    lines.append("    modified: 1749660438113")

    # Environments
    lines.append("environments:")
    lines.append("  name: Base Environment")
    lines.append("  meta:")
    lines.append(f"    id: {md5_id('env', 'base-environment')}")
    lines.append("    created: 1749660438112")
    lines.append("    modified: 1749660438112")
    lines.append("    isPrivate: false")
    lines.append("  data:")
    lines.append("    scheme: https")
    lines.append('    base_path: ""')
    lines.append("    base_url: >-")
    lines.append(
        "      {{ _.scheme }}://{{ _.host }}{{ _.base_path }}"
    )
    lines.append("  subEnvironments:")
    lines.append("    - name: Stillness")
    lines.append("      meta:")
    lines.append(f"        id: {md5_id('env', 'stillness-environment')}")
    lines.append("        created: 1749660554120")
    lines.append("        modified: 1749660554120")
    lines.append("        isPrivate: false")
    lines.append("        sortKey: 1749660554120")
    lines.append("      data:")
    lines.append(
        "        host: blockchain-gateway-stillness.live.tech.evefrontier.com"
    )
    lines.append("        api_key: eyABC.123")
    lines.append('      color: "#ff4a00"')

    return "\n".join(lines) + "\n"


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    spec_path = repo_root / "data" / "world-api-stillness.json"

    if not spec_path.exists():
        print(
            f"Error: Swagger spec not found at {spec_path}", file=sys.stderr
        )
        return 1

    with open(spec_path) as f:
        spec = json.load(f)

    yaml_output = generate_collection(spec)
    print(yaml_output, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
