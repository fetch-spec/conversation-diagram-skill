# Mermaid rules (Kroki-safe)

Kroki runs Mermaid server-side. Invalid syntax returns HTTP 400. Follow these
for **any** conversation — the samples below are syntax, not domain templates.

## Frontmatter (optional)

```mermaid
---
config:
  theme: base
  themeVariables:
    darkMode: true
    background: transparent
    primaryColor: "#1c1e21"
    primaryTextColor: "#ecece6"
    primaryBorderColor: "#4d5358"
    lineColor: "#9aa3a8"
    secondaryColor: "#24272b"
    tertiaryColor: "#151719"
---
flowchart TB
  A[Start] --> B[End]
```

You may omit the frontmatter. The render script does not inject it.

## IDs and labels

```text
GOOD:  API["lookupSku()"]
GOOD:  PDF["PDF page"]
BAD:   PDF page["PDF page"]     # spaces in ID
BAD:   A[don't]                 # unquoted apostrophe
GOOD:  A["don't invent a step"]
```

- IDs: letters, digits, underscore. Start with a letter.
- Multi-line labels: `"line one<br/>line two"`
- Decision nodes: `READY{"Ready to ship?"}`
- Subgraphs: `subgraph vlm["VLM arm"]` … `end`

## Flowchart

```mermaid
flowchart TB
  IN["Input"] --> STEP["Work"]
  STEP --> OUT["Output"]
```

Directions: `TB` (pipeline), `LR` (call chain).

## Sequence

```mermaid
sequenceDiagram
  participant A as Alice
  participant B as Service
  A->>B: request
  B-->>A: response
```

## Class / contract

```mermaid
classDiagram
  class Root {
    +model
    +confidence
    +notes
  }
  Root --> Model
```

Prefer a small flowchart for JSON shapes if class syntax gets messy.

## Limits

- Stay under ~20 nodes per diagram. Split instead of cramming.
- Do not put raw secrets, full API keys, or PII in labels.
- Do not use HTML except `<br/>`.
- Avoid experimental diagram types unless you have verified Kroki's Mermaid version supports them.
- `mindmap` and `sankey` are version-sensitive — skip them unless you can re-render after a failure.
