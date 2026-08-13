#!/usr/bin/env python3
"""Render Mermaid (or other Kroki languages) to SVG/PNG.

Tries Kroki first, then mermaid.ink for Mermaid+SVG if Kroki is blocked.

Examples:
  python3 render_kroki.py flow.mmd --out-dir output
  python3 render_kroki.py --manifest diagrams.json --out-dir output
  python3 render_kroki.py --manifest diagrams.json --format svg,png
  python3 render_kroki.py --manifest diagrams.json --emit-mmd diagrams
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_ENDPOINT = os.environ.get("KROKI_URL", "https://kroki.io").rstrip("/")
MERMAID_INK = os.environ.get("MERMAID_INK_URL", "https://mermaid.ink").rstrip("/")
USER_AGENT = os.environ.get(
    "KROKI_USER_AGENT",
    "Mozilla/5.0 (compatible; conversation-diagram-skill/1.0; +https://github.com/fetch-spec/conversation-diagram-skill)",
)

SUPPORTED = {
    "mermaid",
    "plantuml",
    "d2",
    "graphviz",
    "dot",
    "bpmn",
    "excalidraw",
    "blockdiag",
    "seqdiag",
    "actdiag",
    "nwdiag",
    "c4plantuml",
    "structurizr",
    "nomnoml",
    "erd",
    "svgbob",
    "wavedrom",
    "pikchr",
    "vega",
    "vegalite",
}

EXT_TO_TYPE = {
    ".mmd": "mermaid",
    ".mermaid": "mermaid",
    ".puml": "plantuml",
    ".plantuml": "plantuml",
    ".d2": "d2",
    ".dot": "graphviz",
    ".gv": "graphviz",
}


def _request(url: str, data: bytes | None, timeout: int, accept: str) -> bytes:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": accept,
    }
    if data is not None:
        headers["Content-Type"] = "text/plain; charset=utf-8"
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{err.code} {url}: {body[:400]}") from err
    except urllib.error.URLError as err:
        raise RuntimeError(f"unreachable {url}: {err}") from err


def render_kroki(endpoint: str, language: str, fmt: str, source: str, timeout: int) -> bytes:
    return _request(
        f"{endpoint}/{language}/{fmt}",
        source.encode("utf-8"),
        timeout,
        "image/svg+xml,image/png,application/pdf,*/*",
    )


def render_mermaid_ink(source: str, fmt: str, timeout: int) -> bytes:
    if fmt not in {"svg", "png"}:
        raise RuntimeError(f"mermaid.ink does not support format {fmt}")
    token = base64.urlsafe_b64encode(source.encode("utf-8")).decode("ascii").rstrip("=")
    path = "svg" if fmt == "svg" else "img"
    return _request(f"{MERMAID_INK}/{path}/{token}", None, timeout, "image/svg+xml,image/png,*/*")


def render(endpoint: str, language: str, fmt: str, source: str, timeout: int) -> tuple[bytes, str]:
    try:
        return render_kroki(endpoint, language, fmt, source, timeout), "kroki"
    except RuntimeError as first:
        if language == "mermaid" and fmt in {"svg", "png"}:
            try:
                return render_mermaid_ink(source, fmt, timeout), "mermaid.ink"
            except RuntimeError as second:
                raise SystemExit(
                    f"Render failed.\n  Kroki: {first}\n  mermaid.ink: {second}\n"
                    "Deliver the .mmd / diagrams.json anyway. Do not fake an image."
                ) from second
        raise SystemExit(f"Kroki failed: {first}") from first


def load_jobs(args: argparse.Namespace) -> list[dict]:
    jobs: list[dict] = []
    if args.manifest:
        data = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
        for item in data.get("diagrams", []):
            language = (item.get("type") or "mermaid").lower()
            if language == "dot":
                language = "graphviz"
            jobs.append({"id": item["id"], "type": language, "source": item["source"]})
    for path_str in args.files:
        path = Path(path_str)
        language = EXT_TO_TYPE.get(path.suffix.lower(), args.type)
        jobs.append({"id": path.stem, "type": language, "source": path.read_text(encoding="utf-8")})
    if not jobs:
        raise SystemExit("No diagrams. Pass files and/or --manifest.")
    return jobs


def main() -> int:
    parser = argparse.ArgumentParser(description="Render diagrams via Kroki (mermaid.ink fallback)")
    parser.add_argument("files", nargs="*", help=".mmd / .puml / .d2 / .dot files")
    parser.add_argument("--manifest", help="diagrams.json from the skill")
    parser.add_argument("--out-dir", default="output")
    parser.add_argument("--format", default="svg", help="svg, png, or svg,png")
    parser.add_argument("--type", default="mermaid", help="Kroki language when extension is unknown")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--emit-mmd", help="Also write <id>.mmd sources into this directory")
    parser.add_argument("--dry-run", action="store_true", help="Validate jobs and emit .mmd only; skip network")
    args = parser.parse_args()

    formats = [f.strip().lower() for f in args.format.split(",") if f.strip()]
    for fmt in formats:
        if fmt not in {"svg", "png", "jpeg", "pdf"}:
            raise SystemExit(f"Unsupported format: {fmt}")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    emit_dir = Path(args.emit_mmd) if args.emit_mmd else None
    if emit_dir:
        emit_dir.mkdir(parents=True, exist_ok=True)

    jobs = load_jobs(args)
    for job in jobs:
        language = job["type"]
        if language not in SUPPORTED:
            raise SystemExit(f"Unsupported Kroki type: {language}")
        if emit_dir:
            dest_mmd = emit_dir / f"{job['id']}.mmd"
            dest_mmd.write_text(job["source"], encoding="utf-8")
            print(f"wrote {dest_mmd}")
        if args.dry_run:
            continue
        for fmt in formats:
            payload, via = render(args.endpoint, language, fmt, job["source"], args.timeout)
            dest = out_dir / f"{job['id']}.{fmt}"
            dest.write_bytes(payload)
            print(f"wrote {dest} ({len(payload)} bytes via {via})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
