"""Use synthetic sources to check retrieval and private-library boundaries."""

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import library


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.payload = "Navigation\nKeep locations clear.\nForms\nPreserve typed input.\n"
        (self.root / "source.txt").write_text(self.payload, encoding="utf-8")
        digest = hashlib.sha256(self.payload.encode()).hexdigest()
        self.data = {
            "version": 1,
            "sources": [{"id": "guide", "title": "Synthetic Guide", "path": "source.txt", "sha256": digest}],
            "sections": [
                {"id": "guide-navigation", "source_id": "guide", "title": "Navigation",
                 "path": "source.txt", "sha256": digest, "locator": "Lines 1-2",
                 "keywords": ["navigation", "location", "menu"], "lines": [1, 2]},
                {"id": "guide-forms", "source_id": "guide", "title": "Forms",
                 "path": "source.txt", "sha256": digest, "locator": "Lines 3-4",
                 "keywords": ["forms", "input", "validation"], "lines": [3, 4]},
            ],
        }
        self.save()

    def save(self):
        (self.root / "registry.json").write_text(json.dumps(self.data), encoding="utf-8")

    def test_routes_without_opening_source_content(self):
        data = library.load_registry(self.root)
        with patch.object(Path, "read_bytes", side_effect=AssertionError("Source read")):
            self.assertEqual([s["id"] for s in library.route(data, "menu")], ["guide-navigation"])
            self.assertEqual(len(library.route(data, "navigation and forms")), 2)
            self.assertEqual(library.route(data, "astronomy"), [])
            self.assertEqual(library.route(data, "guide-forms")[0]["id"], "guide-forms")

    def test_reads_only_requested_range_without_writing(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        data = library.load_registry(self.root)
        library.verify(self.root, data)
        _, text = library.read_section(self.root, data, "guide-forms")
        self.assertEqual(text, "Forms\nPreserve typed input.\n")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_changed_text_fails_instead_of_returning_it(self):
        (self.root / "source.txt").write_text("Changed content", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "changed"):
            library.read_section(self.root, self.data, "guide-navigation")
        with self.assertRaisesRegex(ValueError, "changed"):
            library.verify(self.root, self.data)

    def test_missing_hash_allows_explicitly_unverified_read(self):
        for entry in self.data["sources"] + self.data["sections"]:
            entry.pop("sha256")
        self.save()
        data = library.load_registry(self.root)
        self.assertEqual(library.route(data, "menu")[0]["id"], "guide-navigation")
        _, text = library.read_section(self.root, data, "guide-navigation")
        self.assertIn("Keep locations clear.", text)
        with self.assertRaisesRegex(ValueError, "No SHA-256"):
            library.verify(self.root, data)

    def test_supplied_invalid_hash_is_still_rejected(self):
        self.data["sections"][0]["sha256"] = "unverified"
        self.save()
        with self.assertRaisesRegex(ValueError, "Invalid SHA-256"):
            library.load_registry(self.root)

    def test_rejects_path_escape_and_symlink_escape(self):
        for path in ("../outside.txt", "/tmp/outside.txt"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                library.local_path(self.root, path)
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            library.local_path(self.root, "escape/outside.txt")

    def test_rejects_broken_registry_links_and_ranges(self):
        section = self.data["sections"][0]
        for key, value in (("source_id", "unknown"), ("lines", [2, 1]), ("lines", [True, 2])):
            previous = section[key]
            section[key] = value
            self.save()
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                library.load_registry(self.root)
            section[key] = previous
        section["lines"] = [1, 99]
        with self.assertRaisesRegex(ValueError, "exceeds"):
            library.read_section(self.root, self.data, section["id"])
        with self.assertRaisesRegex(ValueError, "exceeds"):
            library.verify(self.root, self.data)

    def test_duplicate_ids_and_conflicting_hashes_fail(self):
        self.data["sections"][1]["id"] = self.data["sections"][0]["id"]
        self.save()
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            library.load_registry(self.root)
        self.data["sections"][1]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            library.verify(self.root, self.data)

    def test_missing_private_state_and_unknown_section_are_explicit(self):
        with self.assertRaisesRegex(ValueError, "No local library"):
            library.load_registry(self.root / "missing")
        with self.assertRaisesRegex(ValueError, "Unknown section"):
            library.read_section(self.root, self.data, "unknown")

    def test_page_break_is_not_a_text_line_break(self):
        payload = "First page\fnext page\nSecond line\n"
        (self.root / "source.txt").write_text(payload, encoding="utf-8")
        section = self.data["sections"][0]
        section["sha256"] = hashlib.sha256(payload.encode()).hexdigest()
        section["lines"] = [2, 2]
        _, text = library.read_section(self.root, self.data, section["id"])
        self.assertEqual(text, "Second line\n")

    def test_copied_reader_works_from_another_directory(self):
        skill = self.root / "copied"
        scripts = skill / "scripts"
        sources = skill / "references" / "library"
        scripts.mkdir(parents=True)
        sources.mkdir(parents=True)
        reader = scripts / "library.py"
        reader.write_bytes(Path(library.__file__).read_bytes())
        for name in ("source.txt", "registry.json"):
            (sources / name).write_bytes((self.root / name).read_bytes())
        result = subprocess.run([sys.executable, str(reader), "route", "menu", "--json"],
                                cwd=self.root, text=True, capture_output=True, check=True)
        self.assertEqual(json.loads(result.stdout)[0]["id"], "guide-navigation")
        result = subprocess.run([sys.executable, str(reader), "read", "guide-forms"],
                                cwd=self.root, text=True, capture_output=True, check=True)
        self.assertIn("Preserve typed input.", result.stdout)
        self.assertNotIn("Keep locations clear.", result.stdout)
        subprocess.run([sys.executable, str(reader), "verify"], cwd=self.root,
                       text=True, capture_output=True, check=True)

        for entry in self.data["sources"] + self.data["sections"]:
            entry["sha256"] = None
        (sources / "registry.json").write_text(json.dumps(self.data), encoding="utf-8")
        result = subprocess.run([sys.executable, str(reader), "read", "guide-forms"],
                                cwd=self.root, text=True, capture_output=True, check=True)
        self.assertIn("Text hash: unverified", result.stdout)
        result = subprocess.run([sys.executable, str(reader), "verify"],
                                cwd=self.root, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Hash verification is incomplete", result.stderr)

    @unittest.skipUnless(shutil.which("git"), "Git is not installed")
    def test_git_ignores_private_data_but_packages_empty_folders(self):
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        skill = self.root / "example"
        skill.mkdir()
        rules = Path(__file__).resolve().parents[1] / ".gitignore"
        (skill / ".gitignore").write_bytes(rules.read_bytes())
        private = ["references/MEMORY.md", "references/history/run.md",
                   "references/library/registry.json", "references/library/book/original.pdf",
                   "references/library/book/sections/chapter.md"]
        for relative in private:
            path = skill / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("Synthetic private data", encoding="utf-8")
            result = subprocess.run(["git", "check-ignore", "-q", f"example/{relative}"], cwd=self.root)
            self.assertEqual(result.returncode, 0, relative)
        markers = ["references/history/.gitkeep", "references/library/.gitkeep"]
        for relative in markers:
            (skill / relative).touch()
        for relative in ["SKILL.md", "assets/learning.md", "scripts/library.py", *markers]:
            result = subprocess.run(["git", "check-ignore", "-q", f"example/{relative}"], cwd=self.root)
            self.assertEqual(result.returncode, 1, relative)
        subprocess.run(["git", "add", "example"], cwd=self.root, check=True)
        tracked = subprocess.run(["git", "ls-files", "--", "example"], cwd=self.root,
                                 text=True, capture_output=True, check=True)
        self.assertEqual(set(tracked.stdout.splitlines()),
                         {"example/.gitignore", *(f"example/{path}" for path in markers)})


if __name__ == "__main__":
    unittest.main()
