---
name: conversation-diagram
description: >
  Turn any conversation, transcript, design note, meeting recap, or workflow
  write-up into Mermaid diagrams and render them with Kroki (SVG/PNG, mermaid.ink
  fallback). Use when the user wants a visual of a discussion, process,
  architecture, sequence, or decision tree. Triggers on "diagram this
  conversation", "mermaid", "kroki", "workflow from this chat", "visualize this
  discussion", "draw the pipeline", "diagram these notes".
metadata:
  short-description: "Any conversation → Mermaid → Kroki SVG/PNG"
user-invocable: true
---

# Conversation → Mermaid → Kroki

Generic skill. Conversation in, diagrams out.

**Do not** hard-code the Image Understanding / PTC sample. That lives only in
`examples/` so you can test the renderer. Every new request starts from the
conversation the user just provided (or a file they point at).

## When to use

The user pastes or points at:

- a chat / design thread
- a setup + code + pipeline write-up
- meeting notes, a runbook, or an architecture dump

and wants diagrams (workflow, sequence, contract, decision tree).

## What you produce

1. One or more **valid Mermaid** sources (plain text).
2. Rendered **SVG** (default) and optional **PNG**.
3. A `diagrams.json` manifest so the run is repeatable.
4. Optional `diagrams/<id>.mmd` files if they want sources they can edit.

## Agent workflow (do this every time)

### 1. Read the source

Treat the user's message (and any attached files) as the **only** source of
truth. Do not invent systems, APIs, services, or steps that are not in the text.
If something is ambiguous, omit it or label the node `"unclear in source"`.

Redact secrets. Never put API keys, tokens, passwords, or raw PII in labels.

### 2. Choose 1–6 diagrams

Pick the smallest set that covers the conversation. Typical split:

| Conversation contains | Diagram type |
| --- | --- |
| Ordered process / pipeline / worker | `flowchart TB` or `LR` |
| Two parties / API request-response | `sequenceDiagram` |
| Branching decisions / checks | `flowchart` with `{decision}` nodes |
| Data shape / JSON / schema | small `flowchart` (or `classDiagram` if clean) |
| Parallel options (SDK vs HTTP, etc.) | `flowchart` with subgraphs |
| Org / topic map | `mindmap` only if Kroki's Mermaid version is known to support it |

A technical write-up often becomes:

1. End-to-end pipeline
2. The critical call / loop
3. Alternatives (clients, backends)
4. Verification / quick check
5. Output contract (only if a schema is specified)

A meeting recap often becomes: one flowchart of decisions + one sequence of
who-does-what.

### 3. Write Mermaid

Follow [references/mermaid-rules.md](references/mermaid-rules.md).

- Node IDs: `[A-Za-z][A-Za-z0-9_]*` — **no spaces in IDs**.
- Labels: quoted `"text"` if they contain punctuation or parentheses.
- Prefer `<br/>` over long single-line labels.
- No emoji in nodes.
- Keep each diagram under ~20 nodes. Split rather than cram.
- Dark-friendly theme frontmatter is optional (see the rules file).

### 4. Write the manifest

Save `diagrams.json` next to the conversation (or in the working directory):

```json
{
  "title": "short title from the conversation",
  "source": "conversation.md",
  "diagrams": [
    {
      "id": "pipeline",
      "title": "Worker pipeline",
      "kicker": "End-to-end",
      "blurb": "One sentence.",
      "type": "mermaid",
      "source": "flowchart TB\n  A[Start] --> B[End]\n"
    }
  ]
}
```

`id` is the output filename stem (`pipeline.svg`). Use kebab-case.

Schema: [manifest.schema.json](manifest.schema.json).

### 5. Render

From this skill directory (or any checkout):

```bash
python3 scripts/render_kroki.py --manifest diagrams.json --out-dir output --emit-mmd diagrams
# or a single file:
python3 scripts/render_kroki.py diagrams/pipeline.mmd --out-dir output
```

Node 18+ equivalent:

```bash
node scripts/render_kroki.mjs --manifest diagrams.json --out-dir output --emit-mmd diagrams
```

Default Kroki endpoint: `https://kroki.io` (free public instance). Override with
`KROKI_URL` or `--endpoint` for a self-hosted server.

The script sends a browser-like User-Agent (public Kroki's CDN blocks the
default Python urllib agent). If Kroki is still unreachable, it falls back to
`https://mermaid.ink` for Mermaid SVG/PNG.

If both fail, still deliver the `.mmd` / `diagrams.json` and say rendering
failed. **Do not fake an image.** Use `--dry-run` to emit sources only.

### 6. Present

Show the diagrams. Offer the Mermaid source. Do not tell the user to paste
into mermaid.live unless they ask.

## Point another Grok / Grok CLI at this folder

Paste [PROMPT.md](PROMPT.md), or say:

```text
Read SKILL.md in this directory. Take the conversation I paste (or a file I
name) and produce diagrams.json + Kroki SVGs. Then run
python3 scripts/render_kroki.py --manifest diagrams.json --out-dir output.
```

Install for Grok CLI / Grok Build:

```bash
# project-local
cp -R conversation-diagram-skill .grok/skills/conversation-diagram

# or user-global
cp -R conversation-diagram-skill ~/.grok/skills/conversation-diagram
```

The folder must contain `SKILL.md` at its root.

## Non-negotiables

- Conversation in → diagrams out. No leftover domain-specific logic.
- Do not send secrets into diagram labels; redact.
- Kroki / mermaid.ink are render-only. The model authors the Mermaid.
- Prefer SVG. Add `--format png` only if asked.
- Validate Mermaid mentally before calling the renderer (matching arrows,
  closed subgraphs, quoted labels).

## Layout of this package

```text
SKILL.md                 this file — instructions for Grok / any LLM
PROMPT.md                paste-this prompt for another Grok instance
README.md                human install / CLI notes
LICENSE                  MIT
manifest.schema.json     diagrams.json shape
scripts/render_kroki.py  stdlib Python renderer (Kroki + mermaid.ink)
scripts/render_kroki.mjs Node 18+ renderer
references/mermaid-rules.md
examples/                one worked sample (not a template to copy blindly)
```
