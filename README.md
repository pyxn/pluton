# Pluton

**Create skills that learn from use—without rewriting their own rules.**

Pluton is an agent skill that creates and converts other skills. It gives each
one a stable contract, private working memory, dated history, and an optional
source library. The resulting skill owns those files. It does not need Pluton
to keep working.

Use it for recurring work where verified experience should improve the next
result: code review, research, operations, writing, or a source-backed workflow.

No database. No background service. No required Python runtime.

[Get started](#get-started) · [How learning works](#how-learning-works) ·
[Seed knowledge](#seed-knowledge) · [Privacy](#privacy-and-control)

## Why Pluton

A static skill can repeat a mistake after the task that exposed it has ended.
A growing log can preserve the evidence, but make it hard to find the useful
lesson. Unrestricted self-editing creates another problem: a skill can change
the rules that were meant to control it.

Pluton separates those concerns:

| Part | Purpose | When it changes |
| --- | --- | --- |
| **Contract** | Purpose, workflow, permissions, and learning rules | A requested skill or contract change |
| **Memory** | Short, current lessons linked to evidence | Verified learning after substantial explicit use |
| **History** | Dated results, failures, checks, and decisions | New records; corrections link back to old records |
| **Library** | Optional books, papers, documents, extracts, and source map | Requested source import or correction |

The contract controls actions. Sources and history supply evidence. Memory
helps the agent choose its next step. Neither a book nor a saved lesson can
grant permission or override the contract.

## Get started

Pluton is **explicit-only**. Invoke `$pluton` or directly ask your agent to use
the Pluton skill. A general request to create a skill does not activate it.

### Codex

1. Clone the repository into your skills directory. The command below uses
   `CODEX_HOME` when set, or the default `~/.codex` location. If `pluton` already
   exists there, inspect it before replacing anything.

   ```bash
   git clone https://github.com/pyxn/pluton.git "${CODEX_HOME:-$HOME/.codex}/skills/pluton"
   ```

2. Start a new turn so Codex can discover the skill.

3. Give Pluton a concrete task:

   ```text
   Use $pluton to create an explicit-only skill named api-review.
   It should review API changes for compatibility and clear failure behavior.
   Keep its sources, memory, and history private.
   ```

Repository access may require GitHub authentication. If Git is unavailable,
download the repository through GitHub and place its contents in a skill folder
named `pluton`. Keep hidden files, including `.gitignore`.

### Other agents

Use an agent that can read and write local files. Register the folder through
that agent's skill mechanism, or ask it to read `pluton/SKILL.md` and follow it.
Codex-specific metadata lives in `agents/openai.yaml`; other hosts may ignore it.
Discovery and permission enforcement depend on the host.

Pluton does not require a separate `skill-creator` skill. Git, Python, and
external validators are optional. Reading a PDF or scanned document may need
additional tools; plain-text sources do not.

## Common requests

### Convert an existing skill

```text
Use $pluton to convert the skill at /path/to/api-review.
Back up the entire skill first. Preserve its purpose, invocation policy,
learning approvals, existing sources, and history. Show the plan before editing.
```

Conversion preserves working readers and existing storage locations. It does
not move records just to match a template. The default structure below applies
to new skills; an existing skill can keep a different layout.

### Add seed knowledge

```text
Use $pluton to add the supplied API design guide to api-review.
Preserve the original source, check the extracted sections, and index them
for task-based lookup. Keep the source and its registry private.
```

### Turn proven lessons into shared rules

```text
Use $pluton to crystallize api-review's verified lessons.
Make the smallest useful changes to its shared instructions.
Keep private evidence local. Do not commit or push.
```

Here, **crystallize** means promoting verified lessons into reviewed, stable
instructions or code. It is a requested maintenance step, not an automatic
result of ordinary use.

## How learning works

1. **Read the contract and current memory.** Open source sections or history
   records only when the task needs them.
2. **Do the requested work.** Verify the result before considering a memory
   change. A verified failure can be useful evidence too.
3. **Check whether saving is allowed.** By default, learning requires explicit
   use of the skill, substantial checked work, writable private files, and no
   instruction against saving.
4. **Add one dated record.** Keep the outcome, checks, relevant friction, and
   learning decision. Correct an accepted record with a newer linked record.
5. **Update memory only when justified.** Link each lesson to its evidence.
   Replace or remove weak lessons instead of adding endless exceptions.
6. **Stop.** One use gets at most one learning pass. There is no background
   loop, scheduled self-review, or automatic push.

For example, two checked failures might show that a review needs to inspect
the current schema before using a saved field name. The skill records the
failures, then adds a short, supported lesson to memory. It does not rewrite
its permissions or turn that local result into a universal claim.

A directly verified fact or explicit user preference can qualify on its own.
A general rule inferred from friction needs repeated evidence, or one serious
defect with a checked correction. A clean run can add history and leave memory
unchanged.

The default learning rule is separate from activation. A generated skill can
activate automatically while limiting learning to explicit use. During
conversion, preserve the user's accepted recording and approval policy.

Pluton uses this same contract for its own learning.

## File structure

A new skill with a local library can look like this:

```text
api-review/
├── SKILL.md                    # Stable purpose, workflow, and limits
├── .gitignore                  # Private-path rules
├── agents/
│   └── openai.yaml             # Codex interface and invocation policy
├── assets/
│   ├── learning.md             # Owned learning contract
│   └── library.md              # Optional source-use guide
├── references/
│   ├── MEMORY.md               # Local, evidence-linked working memory
│   ├── history/
│   │   ├── .gitkeep            # Empty, shareable folder marker
│   │   └── YYYY-MM-DD-topic.md # Local use record
│   └── library/
│       ├── .gitkeep            # Empty, shareable folder marker
│       ├── registry.json       # Local source map, created on import
│       └── source-id/          # Local originals and readable extracts
└── scripts/
    └── library.py              # Optional source reader
```

Normal learning changes only memory and new history records. Stable files and
source metadata require a relevant change request.

The public package contains no seed material, registry, or working memory.
Under `references/`, it includes only the two empty `.gitkeep` files. Local
memory is created during setup or the next permitted learning write.

The generated skill keeps its own name and domain language. It gets no
“Pluton-powered” label, creator path, or dependency back to this repository.
Later changes to Pluton do not silently change skills it has already created.

## Seed knowledge

Supply a book, paper, manual, or other document when a skill needs a knowledge
base. Pluton preserves the source and uses real chapters or sections as lookup
units. It does not replace the source with a generated summary.

The private registry records source locations, section titles, task keywords,
and extraction limits. SHA-256 hashes, when available, detect changed files.
A hash verifies file identity—not whether a claim is true.

Lookup starts with registry metadata. The agent selects the smallest useful
section set, then reads those sections. It opens the original when a figure,
exact wording, or extraction problem matters. Unreadable material remains
marked unreadable; missing sources are reported, not invented.

“Dynamic” means selection based on the current task. It does not mean rewriting
the book or registry after every use.

### Optional Python reader

The reader uses Python 3.10 or later and only the standard library. From a
skill folder that includes the helper and an imported source:

```bash
python3 scripts/library.py list
python3 scripts/library.py route "review API error responses"
python3 scripts/library.py route "validation and compatibility" --limit 5 --json
python3 scripts/library.py read SECTION_ID
python3 scripts/library.py verify
```

Replace `SECTION_ID` with an ID from `list`. Routing reads metadata only and
returns up to three sections by default. `read` checks the section file's hash
when recorded. Missing hashes produce an explicit unverified read; `verify`
requires all source hashes and valid section references and ranges.

The helper does not write files, update the registry, import documents, or
execute source text. Without Python, the agent uses the same registry with
file tools. See the [source library guide](assets/library.md) for the format
and file-based procedure.

## Privacy and control

- **Private by default in Git.** Memory, history, source files, extracts, and
  registry metadata are ignored. Only empty folder markers are shareable under
  `references/`.
- **Existing tracking needs a separate check.** `.gitignore` does not untrack
  files or remove earlier commits. Pluton checks the containing repository,
  not just whether the skill folder has its own `.git` directory.
- **No Git is required.** Outside a repository, learning uses plain files. If
  a repository is known but its tracking state cannot be checked, private
  learning writes wait. The main task can continue.
- **Ignored does not mean encrypted.** Private files remain readable on disk
  and may enter backups or copied archives. Text read by a remote model is not
  confined to the local machine.
- **History excludes unnecessary sensitive data.** Use compact evidence links,
  not credentials, raw private payloads, or full transcripts.
- **Publication is separate.** Ordinary learning does not commit or push.
  Share only reviewed files after a publishing request.

These are instructions for the agent, not an operating-system security
boundary. The host's permissions and the user's current request still apply.

## Limits

Pluton does not train model weights, guarantee perfect behavior, or prove that
a skill has improved merely because it changes less often. It does not provide
cross-device memory sync, encrypted storage, or a document extraction service.

The Python reader and Git packaging have automated tests. The file-tool-only
workflow is documented; it is not a claim of tested compatibility with every
agent or host.

## Development

Run the tests from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

Tests use synthetic sources. They cover routing, bounded section reads, source
changes, missing hashes, unsafe paths, invalid references and ranges, copied
reader behavior, and private Git packaging. The Git-specific test is skipped
when Git is absent.

For a proposed change:

1. Describe the real failure or use case.
2. Make the smallest change that addresses it.
3. Add a focused test when behavior changes.
4. Keep private sources, memory, and history out of the patch.

Start with the [skill contract](SKILL.md), [learning contract](assets/learning.md),
or [source library guide](assets/library.md), depending on the change.

## The name

Pluton's name comes from this idea:

> It's the slow, private crystallization of experience—beliefs, values, scars—that hardened into something solid while nobody was watching.

The design applies that idea to skills: preserve experience, keep useful
lessons close, and change stable rules only through deliberate review.

## License

Licensed under the [MIT License](LICENSE). Copyright (c) 2026 Paul Yu.
