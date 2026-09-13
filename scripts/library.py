#!/usr/bin/env python3
"""Read a skill's private source library. This program never writes files."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1] / "references" / "library"
STOP = set("a an and are as at be by for from how i in is it of on or that the this to with".split())


def local_path(root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError("Registry paths must stay inside the library")
    resolved = (root / path).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Registry path points outside the library")
    return resolved


def load_registry(root: Path) -> dict:
    registry_path = root / "registry.json"
    if not registry_path.is_file():
        raise ValueError("No local library registry. Import the needed source first.")
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("Expected library registry version 1")
    for group in ("sources", "sections"):
        entries = data.get(group)
        if not isinstance(entries, list) or not entries:
            raise ValueError(f"Registry needs a non-empty {group} list")
        ids = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(f"Invalid {group} entry")
            required = ["id", "title", "path", "sha256"]
            if group == "sections":
                required += ["source_id", "locator"]
            if any(not isinstance(entry.get(key), str) or not entry[key].strip() for key in required):
                raise ValueError(f"Missing or invalid {group} fields")
            if entry["id"] in ids:
                raise ValueError(f"Duplicate {group} ID: {entry['id']}")
            ids.add(entry["id"])
            if not re.fullmatch(r"[0-9a-f]{64}", entry["sha256"]):
                raise ValueError(f"Invalid SHA-256: {entry['id']}")
            local_path(root, entry["path"])
    source_ids = {source["id"] for source in data["sources"]}
    for section in data["sections"]:
        if section["source_id"] not in source_ids:
            raise ValueError(f"Unknown source for section: {section['id']}")
        keywords = section.get("keywords")
        if not isinstance(keywords, list) or any(not isinstance(word, str) for word in keywords):
            raise ValueError(f"Invalid keywords: {section['id']}")
        if "lines" in section:
            lines = section["lines"]
            if (not isinstance(lines, list) or len(lines) != 2
                    or any(type(number) is not int for number in lines)
                    or not 1 <= lines[0] <= lines[1]):
                raise ValueError(f"Invalid line range: {section['id']}")
    return data


def words(value: str) -> set[str]:
    return set(re.findall(r"\w+", value.casefold())) - STOP


def route(data: dict, query: str, limit: int = 3) -> list[dict]:
    if limit < 1:
        raise ValueError("Limit must be at least 1")
    query_words = words(query)
    matches = []
    for section in data["sections"]:
        title_hits = query_words & words(section["title"])
        keyword_hits = query_words & words(" ".join(section["keywords"]))
        score = 3 * len(title_hits) + 2 * len(keyword_hits)
        if query.strip().casefold() == section["id"].casefold():
            score += 100
        if score:
            matches.append({**section, "score": score,
                            "matched": sorted(title_hits | keyword_hits)})
    return sorted(matches, key=lambda entry: -entry["score"])[:limit]


def read_section(root: Path, data: dict, section_id: str) -> tuple[dict, str]:
    section = next((entry for entry in data["sections"] if entry["id"] == section_id), None)
    if section is None:
        raise ValueError(f"Unknown section: {section_id}")
    payload = local_path(root, section["path"]).read_bytes()
    if hashlib.sha256(payload).hexdigest() != section["sha256"]:
        raise ValueError(f"Source text changed: {section_id}. Check the original before re-indexing.")
    text = payload.decode("utf-8")
    if "lines" in section:
        lines = io.StringIO(text, newline="").readlines()
        start, end = section["lines"]
        if end > len(lines):
            raise ValueError(f"Line range exceeds source text: {section_id}")
        text = "".join(lines[start - 1:end])
    return section, text


def verify(root: Path, data: dict) -> None:
    hashes = {}
    for entry in data["sources"] + data["sections"]:
        path = local_path(root, entry["path"])
        if path in hashes:
            if hashes[path] != entry["sha256"]:
                raise ValueError("Conflicting hashes for the same file")
            continue
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != entry["sha256"]:
            raise ValueError(f"File changed: {entry['id']}. Check the original before re-indexing.")
        hashes[path] = entry["sha256"]
    line_counts = {}
    for section in data["sections"]:
        path = local_path(root, section["path"])
        if path not in line_counts:
            with path.open(encoding="utf-8") as stream:
                line_counts[path] = sum(1 for _ in stream)
        if line_counts[path] == 0:
            raise ValueError(f"Empty section file: {section['id']}")
        if section.get("lines", [1, 1])[1] > line_counts[path]:
            raise ValueError(f"Line range exceeds source text: {section['id']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    route_parser = commands.add_parser("route", help="Find relevant source sections")
    route_parser.add_argument("query")
    route_parser.add_argument("--limit", type=int, default=3)
    route_parser.add_argument("--json", action="store_true")
    list_parser = commands.add_parser("list", help="List registered sections without reading sources")
    list_parser.add_argument("--json", action="store_true")
    read_parser = commands.add_parser("read", help="Read one section with its source location")
    read_parser.add_argument("section_id")
    commands.add_parser("verify", help="Check all source hashes and text ranges")
    args = parser.parse_args()
    try:
        data = load_registry(ROOT)
        if args.command == "verify":
            verify(ROOT, data)
            print(f"Verified {len(data['sources'])} sources and {len(data['sections'])} sections.")
        elif args.command == "read":
            section, text = read_section(ROOT, data, args.section_id)
            source = next(item for item in data["sources"] if item["id"] == section["source_id"])
            print(f"Source: {source['title']}\nSection: {section['title']}\nLocation: {section['locator']}\n")
            print(text, end="" if text.endswith("\n") else "\n")
        else:
            entries = route(data, args.query, args.limit) if args.command == "route" else data["sections"]
            if args.json:
                print(json.dumps(entries, ensure_ascii=False, indent=2))
            elif not entries:
                print("No matching section. List the registry or search the relevant source text.")
            else:
                for entry in entries:
                    location = f"{entry['path']}" + (f" lines {entry['lines']}" if "lines" in entry else "")
                    print(f"{entry['id']}: {entry['title']}\n  {entry['locator']}\n  {location}")
        return 0
    except (OSError, ValueError) as error:
        print(f"Library error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
