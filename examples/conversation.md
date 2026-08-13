# Sample conversation (Image Understanding VLM arm)

This file is a **worked example**, not a template. New conversations should
replace this content entirely.

---

Minimal Image Understanding path for a VLM arm (order/options crop → partial JSON).

Docs: Image understanding. Model with image input: `grok-4.6`.

## 1. Setup

```bash
pip install xai-sdk openai httpx
export XAI_API_KEY="your_key"  # console.x.ai — separate from SuperGrok
```

## 2. Local crop → API (xAI SDK)

`understand_order_crop(crop_path)`:

- Reject images over 20 MiB
- Encode PNG/JPEG as a `data:` URL
- `Client` + `chat.create(model="grok-4.6")`
- `user(PROMPT, image(image_url=..., detail="high"))`
- `chat.sample()`, strip accidental markdown fences, `json.loads`

Input must be PNG/JPEG, not PDF. Rasterize first (pdf2image, PyMuPDF).

## 3. Same call, OpenAI-compatible client

`OpenAI(api_key=..., base_url="https://api.x.ai/v1")` then `responses.create`
with `input_image` + `input_text`. Same prompt, same model.

## 4. Wire into the worker

```text
PDF page
  → crop order/options → order_crop.png
  → understand_order_crop() → model/options JSON
  → Docling on full page → specs/tables
  → merge → ptc.json → validate → done
```

Only the crop goes to Image Understanding. Docling stays local/text.

## Limits

| Item | Value |
|------|--------|
| Formats | jpg / jpeg / png |
| Max size | 20 MiB |
| Detail | `"high"` for diagrams |
| PDF | rasterize first |
| Billing | API tokens, not SuperGrok quota |
| History | do not store image request/response on server |

## Quick check

1. Real order-box crop at `order_crop.png`
2. Set `XAI_API_KEY`
3. Run the script — JSON with `model.verbatim` / `options`

If the SDK field name differs, print `response` and map `.content` / `.text` / `.output_text`.
