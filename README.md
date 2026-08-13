# Conversation diagram skill

Turn **any** conversation into Mermaid diagrams and render them with
[Kroki](https://kroki.io) (falls back to [mermaid.ink](https://mermaid.ink)).

Portable Grok skill: drop the folder into a skills path, or tell another Grok
instance to read `SKILL.md`, paste a conversation, get SVGs.

## What to send another Grok

Use [PROMPT.md](PROMPT.md), or this:

> Read `SKILL.md` in this folder. Diagram the conversation I paste. Write
> `diagrams.json`, then run
> `python3 scripts/render_kroki.py --manifest diagrams.json --out-dir output`.

## Render only (no model)

You already have Mermaid in a `.mmd` file or a `diagrams.json` manifest:

```bash
python3 scripts/render_kroki.py --manifest diagrams.json --out-dir output
python3 scripts/render_kroki.py path/to/flow.mmd --format svg --out-dir output
python3 scripts/render_kroki.py --manifest diagrams.json --emit-mmd diagrams --dry-run
```

Node 18+:

```bash
node scripts/render_kroki.mjs --manifest diagrams.json --out-dir output
```

| Variable | Default | Meaning |
| --- | --- | --- |
| `KROKI_URL` | `https://kroki.io` | Kroki base URL (self-host if you want) |
| `MERMAID_INK_URL` | `https://mermaid.ink` | Fallback renderer for Mermaid |
| `KROKI_USER_AGENT` | browser-like | Public Kroki's CDN blocks bare Python urllib |

No API key. Public Kroki is free; self-host for production volume.

The Python script is **stdlib only** (3.9+). The Node script needs Node 18+.

## Grok CLI / Grok Build

Copy this directory into a skills path:

```bash
cp -R conversation-diagram-skill ~/.grok/skills/conversation-diagram
# or, inside a project
cp -R conversation-diagram-skill .grok/skills/conversation-diagram
```

Keep `SKILL.md` at the root of that folder. Then:

```text
Diagram this conversation using the conversation-diagram skill.
```

## Sample

`examples/` is the Image Understanding / crop → JSON write-up used to develop
this pack. Use it to test the renderer. Do **not** reuse those diagrams for an
unrelated conversation.

```bash
python3 scripts/render_kroki.py --manifest examples/diagrams.json --out-dir examples/output --emit-mmd examples/diagrams
```

## Files

| File | Role |
| --- | --- |
| [SKILL.md](SKILL.md) | Instructions for Grok / any LLM |
| [PROMPT.md](PROMPT.md) | Paste-this prompt for another instance |
| [scripts/render_kroki.py](scripts/render_kroki.py) | Python 3 stdlib renderer |
| [scripts/render_kroki.mjs](scripts/render_kroki.mjs) | Node renderer |
| [references/mermaid-rules.md](references/mermaid-rules.md) | Syntax Kroki's Mermaid accepts |
| [manifest.schema.json](manifest.schema.json) | Shape of `diagrams.json` |

## License

MIT — see [LICENSE](LICENSE).
