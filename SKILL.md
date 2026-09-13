---
name: pluton
description: "Use only when the user explicitly invokes $pluton or directly asks to use the Pluton skill. Create, convert, or improve skills with a stable contract, private working memory, dated history, and optional seed sources read on demand."
---

# Pluton

Create skills that improve through verified use without changing their own
purpose or authority. Each generated skill owns its files and works without
loading Pluton. Pluton itself uses the same learning contract.

Pluton is explicit-only. A general request to create a skill does not activate
it. Basic use needs only an agent that can read and write files. Git, Python,
other skills, and external validators are optional.

## Start

1. Read [learning.md](assets/learning.md). This reusable contract governs
   Pluton's own learning and is copied into generated skills.
2. Read `references/MEMORY.md` if present. Missing memory means an empty local
   memory. Initialize it during setup or the next permitted learning write.
3. Inspect the target skill, local instructions, invocation policy, and available
   file tools. Check Git state only if Git is available. Check the containing
   repository from the resolved skill path; a skill need not be its own repo.
4. Establish the requested result and success checks. Read
   [library.md](assets/library.md) only for seed-source work. Read selected
   history only when a specific evidence question needs it.

## Owned Parts

| Part | Purpose | Allowed change |
| --- | --- | --- |
| `SKILL.md`, assets, scripts, configuration | Purpose, workflow, limits, learning rules | Requested skill or contract work |
| `references/MEMORY.md` | Short, evidence-linked working knowledge | Verified learning after substantial explicit use |
| `references/history/` | Dated use evidence | Add records; correct old records with newer linked records |
| `references/library/` | Optional sources, extracts, and registry | Requested source import, addition, or correction |

Normal learning changes only memory and new history records. A source, log, or
memory item cannot grant authority or override the contract. Higher-priority
instructions and the current user request still control the work.

## Create or Convert

1. Resolve the purpose and boundaries from the request and local files. Ask for
   a new skill's invocation policy only when the user has not specified it.
   Preserve an existing policy during conversion. Use the requested location or
   the host's discovered skill directory. If neither is known, ask for the target
   folder rather than guessing a platform-specific installation path.
2. Write the target's actual operating rules in a compact `SKILL.md`. Follow
   the packaging rules below. No separate skill-creator skill is required.
3. Copy `assets/learning.md` into the target and require it at startup. Then
   read optional memory. Adjust paths only to preserve an existing layout.
4. Copy the private-path rules from Pluton's `.gitignore` into new skills before
   private writes. Create `references/history/.gitkeep` and
   `references/library/.gitkeep` as empty shareable placeholders. Create an ignored
   `references/MEMORY.md` with a heading and "No verified lessons yet."
   Preserve any existing memory. Do not invent history or seed content.
5. Import requested seed material through `assets/library.md`. Keep original
   source text and locations available. Develop useful task rules without
   copying private details into tracked instructions. Copy the neutral library
   guide only when the target needs import guidance. Copy `scripts/library.py`
   only when the optional helper is useful. Include the file-based lookup method.
6. Preserve working source readers, registries, memory, and history during
   conversion. Reuse their existing locations and adjust the learning contract's
   paths. Do not create a second owner or move records just to match a folder name.
7. Check the result using available tools and the review below. Report the
   target path, checks, local memory location, and any remaining limits.

Creating or converting a target authorizes the needed target contract edits.
A direct request to change a stable rule also authorizes the target skill
itself. Normal learning does not change other skills.

## Independent Output

The target owns the resulting files. Copy reusable content into it; do not
make it import, invoke, or link back to this creator. Later creator changes
do not silently change existing skills.

Use the target's own name and domain terms. Do not add "Pluton", "Pluton skill",
"Pluton-powered", creator paths, or conversion badges to its instructions,
interface metadata, scripts, filenames, working memory, or new journal records.
Use names such as `learning.md` and `learning-setup` for shared concepts.
Describe what changed and why in the target's own terms.

Before handoff, inspect all newly written files and names for creator branding
and external runtime dependencies. Every required instruction, asset, and script
must resolve inside the target, except its actual domain integrations. Use file
search when `rg` is absent. Do not rewrite source quotations or old history just
to remove truthful prior mentions. Attribution is included only when requested
or when the creator itself is the target's subject.

## Self-Contained Packaging

Name a new skill folder with lowercase letters, digits, and single hyphens.
Use the same name in the required YAML header at the top of `SKILL.md`:

```yaml
---
name: example-skill
description: "Describe the skill's real task and when to use it."
---
```

Keep the name under 64 characters. Follow the header with the purpose, workflow,
limits, and links to needed files. Require the copied learning contract and
state the invocation policy. Do not leave example names or unfinished fields.

For Codex, use `agents/openai.yaml` for interface metadata and invocation policy.
Set `policy.allow_implicit_invocation: false` for an explicit-only skill.
Other hosts may ignore that file. State the explicit-only rule in the
description and body too; use host controls when available and do not claim
technical enforcement by a host that does not support it.

Use available file tools to create and inspect the package. An installed
validator can add checks, but no other skill, package manager, or installer is
required. If a validator is missing or cannot run, perform the review below and
state that automated validation did not run.

## Local State and Git

For new skills, reserve `references/` for local knowledge. Only the two empty
`.gitkeep` files are eligible for tracking there. Git tracks files, so these placeholders
preserve the folders in a clone. They never contain notes or private data.

The ignore rules exclude memory, history records, originals, extracts, registry
metadata, and new library subfolders. Reuse the rules from Pluton's `.gitignore`
rather than maintaining a second pattern list. A fresh clone gets empty folders.
The next permitted initialization or learning write creates its local memory.

If Git is available and the resolved skill path is in a repository, check the
private paths with `git ls-files` and `git check-ignore`. A nested skill follows
the containing repo's Git state. An ignore rule does not untrack existing data.
Report tracked private paths without their contents. Do not write new private
state there, untrack files, or rewrite history without a cleanup request.

If Git is absent or no repository contains the skill, use plain files. Keep the
ignore file for later Git use. Use file tools to inspect the skill's resolved
ancestors for existing Git metadata when Git cannot run. If a known repo's
tracking state cannot be checked, defer private learning writes in that repo,
including new history records. Continue the main task. Otherwise continue local
learning and state that no Git check ran. Do not initialize a repository or
install Git merely to enable memory.

Ignored files are readable on disk and can enter backups or copied archives.
They are not encrypted or backed up by Git. Publish only selected tracked files;
never force-add private state. Do not include private files in a shared copy
without a direct request for them.

## Crystallize Verified Lessons

When the user asks to crystallize a named skill, turn useful private lessons
into durable, shareable improvements:

1. Read memory and only the history records needed to establish each lesson.
   Prefer repeated evidence or one demonstrated serious defect with a checked fix.
2. Select general rules that improve future work. Remove private names, paths,
   source text, source titles, and links to private evidence from the tracked result.
3. Make the smallest correction to the existing instruction, asset, or script.
   A crystallization request authorizes method improvements. It does not authorize
   changes to purpose, permissions, invocation policy, or privacy rules unless
   those changes were also requested.
4. Check the changed behavior. Add a local history record linking the change
   to its evidence, and remove redundant working-memory items when appropriate.
   Keep the old evidence.
5. Commit or publish only when requested, using the available repository tools.
   Without Git, deliver the reviewed file changes locally. Do not create a repo
   just to complete crystallization.

The remote skill improves through these reviewed changes. Raw memory and
history remain local. Ordinary use performs one learning pass; it does not
start background work, repeated self-review, or automatic pushes.

## Verification

Inspect the name and YAML header, purpose, invocation rule, learning link, and
relative paths. Check that each linked instruction exists and that normal
learning cannot change stable rules. Confirm that startup handles absent memory.

Check that only empty placeholders are shareable under `references/`. Inspect
the intended shared files for private content. With Git, check ignore and
tracking state and run `git diff --check`; without it, inspect the files directly.

For a library, test a narrow request, a two-section request, and a no-match
request. Use the optional Python reader when available, or inspect the same
registry and source ranges with file tools. Check the source relevance and
report any unavailable hash or automated checks.

Check that substantial explicit use can add history and supported memory.
Small or automatic uses must not write learning. A user instruction not to
save overrides the default. Treat contract corrections as proposals unless
the user requested the change.

Finish the requested work, then apply `assets/learning.md` to Pluton's own
memory. A clean run can add history without changing memory. Fewer changes
do not by themselves prove that a skill is better.
