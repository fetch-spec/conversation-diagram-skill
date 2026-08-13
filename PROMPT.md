# Prompt to send another Grok / Grok CLI

Copy everything below the line. Point the other instance at this folder first
(`cd` into it, or pass the path). Then paste your conversation after the
marker.

---

Read `SKILL.md` and `references/mermaid-rules.md` in this folder.

You are running the **conversation-diagram** skill. It is generic: any
conversation in, Mermaid + Kroki diagrams out. Ignore `examples/` unless I
explicitly ask you to re-render the sample.

Do this:

1. Treat the conversation I paste below (or the file I name) as the **only**
   source of truth. Do not invent systems, APIs, or steps that are not in it.
   Redact secrets.
2. Choose 1–6 diagrams that cover the discussion (pipeline, sequence,
   decisions, contract, alternatives). Keep each under ~20 nodes.
3. Write valid Mermaid. Node IDs: `[A-Za-z][A-Za-z0-9_]*`. Quote labels that
   contain punctuation. Use `<br/>` for line breaks. No emoji.
4. Write `diagrams.json` next to the conversation, matching
   `manifest.schema.json`.
5. Render:

   ```bash
   python3 scripts/render_kroki.py --manifest diagrams.json --out-dir output --emit-mmd diagrams
   ```

   If Python is missing:

   ```bash
   node scripts/render_kroki.mjs --manifest diagrams.json --out-dir output --emit-mmd diagrams
   ```

6. Show me the SVGs and the Mermaid source. If rendering fails, still give me
   `diagrams.json` and the `.mmd` files — do not fake images.

Conversation starts here:

<!-- paste the conversation or write: use file PATH -->
