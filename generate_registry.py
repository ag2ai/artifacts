#!/usr/bin/env python3
"""Generate registry.json from all artifact.json files in the repo.

Run from the repo root:
    python generate_registry.py

Or via CI: this script runs on every push to main and commits
the updated registry.json if it changed.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent

# Artifact type -> directory name
TYPE_DIRS = {
    "skills": "skills",
    "templates": "templates",
    "tools": "tools",
    "datasets": "datasets",
    "agents": "agents",
    "bundles": "bundles",
}


def find_artifacts() -> list[dict]:
    """Walk all type directories and collect artifact metadata."""
    artifacts = []

    for type_key, dir_name in TYPE_DIRS.items():
        type_dir = REPO_ROOT / dir_name
        if not type_dir.is_dir():
            continue

        for artifact_dir in sorted(type_dir.iterdir()):
            if not artifact_dir.is_dir():
                continue
            manifest = artifact_dir / "artifact.json"
            if not manifest.exists():
                continue

            try:
                raw = json.loads(manifest.read_text())
            except json.JSONDecodeError as e:
                print(f"  WARNING: invalid JSON in {manifest}: {e}", file=sys.stderr)
                continue

            # Resolve owner: explicit > first author > default
            authors = raw.get("authors", [])
            owner = raw.get("owner", authors[0] if authors else "ag2ai")

            entry = {
                "name": raw["name"],
                "owner": owner,
                "type": raw.get("type", type_key.rstrip("s")),
                "display_name": raw.get("display_name", raw["name"]),
                "description": raw.get("description", ""),
                "version": raw.get("version", "0.0.0"),
                "path": f"{dir_name}/{artifact_dir.name}",
                "tags": raw.get("tags", []),
            }
            artifacts.append(entry)
            print(f"  {entry['type']:10s} {owner}/{entry['name']} v{entry['version']}")

    return artifacts


def main():
    print("Scanning for artifacts...\n")
    artifacts = find_artifacts()

    registry = {
        "version": "1",
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
    }

    output = REPO_ROOT / "registry.json"
    output.write_text(json.dumps(registry, indent=2) + "\n")
    print(f"\nGenerated registry.json with {len(artifacts)} artifacts.")


if __name__ == "__main__":
    main()
