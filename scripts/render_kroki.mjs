#!/usr/bin/env node
/**
 * Render Mermaid (or other Kroki languages) to SVG/PNG.
 * Tries Kroki first, then mermaid.ink for Mermaid+SVG/PNG if Kroki is blocked.
 *
 *   node render_kroki.mjs --manifest diagrams.json --out-dir output
 *   node render_kroki.mjs flow.mmd --out-dir output
 *   node render_kroki.mjs --manifest diagrams.json --emit-mmd diagrams
 */

import { mkdir, readFile, writeFile } from "node:fs/promises";
import { basename, extname, join } from "node:path";

const DEFAULT_ENDPOINT = (process.env.KROKI_URL || "https://kroki.io").replace(/\/$/, "");
const MERMAID_INK = (process.env.MERMAID_INK_URL || "https://mermaid.ink").replace(/\/$/, "");
const USER_AGENT =
  process.env.KROKI_USER_AGENT ||
  "Mozilla/5.0 (compatible; conversation-diagram-skill/1.0; +https://github.com/fetch-spec/conversation-diagram-skill)";

const EXT_TO_TYPE = {
  ".mmd": "mermaid",
  ".mermaid": "mermaid",
  ".puml": "plantuml",
  ".plantuml": "plantuml",
  ".d2": "d2",
  ".dot": "graphviz",
  ".gv": "graphviz",
};

function parseArgs(argv) {
  const out = {
    files: [],
    format: "svg",
    type: "mermaid",
    endpoint: DEFAULT_ENDPOINT,
    outDir: "output",
    dryRun: false,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--manifest") out.manifest = argv[++i];
    else if (a === "--out-dir") out.outDir = argv[++i];
    else if (a === "--format") out.format = argv[++i];
    else if (a === "--type") out.type = argv[++i];
    else if (a === "--endpoint") out.endpoint = argv[++i];
    else if (a === "--emit-mmd") out.emitMmd = argv[++i];
    else if (a === "--dry-run") out.dryRun = true;
    else if (a.startsWith("-")) throw new Error(`Unknown flag: ${a}`);
    else out.files.push(a);
  }
  return out;
}

async function post(url, body) {
  const res = await fetch(url, {
    method: body == null ? "GET" : "POST",
    headers: {
      "User-Agent": USER_AGENT,
      Accept: "image/svg+xml,image/png,application/pdf,*/*",
      ...(body != null ? { "Content-Type": "text/plain; charset=utf-8" } : {}),
    },
    body: body ?? undefined,
  });
  const buf = Buffer.from(await res.arrayBuffer());
  if (!res.ok) {
    throw new Error(`${res.status} ${url}: ${buf.toString("utf8").slice(0, 400)}`);
  }
  return buf;
}

function mermaidInkUrl(source, fmt) {
  const token = Buffer.from(source, "utf8").toString("base64url").replace(/=+$/, "");
  const path = fmt === "png" ? "img" : "svg";
  return `${MERMAID_INK}/${path}/${token}`;
}

async function render(endpoint, language, fmt, source) {
  try {
    const payload = await post(`${endpoint}/${language}/${fmt}`, source);
    return { payload, via: "kroki" };
  } catch (first) {
    if (language === "mermaid" && (fmt === "svg" || fmt === "png")) {
      try {
        const payload = await post(mermaidInkUrl(source, fmt), null);
        return { payload, via: "mermaid.ink" };
      } catch (second) {
        throw new Error(
          `Render failed.\n  Kroki: ${first.message}\n  mermaid.ink: ${second.message}\n` +
            "Deliver the .mmd / diagrams.json anyway. Do not fake an image.",
        );
      }
    }
    throw first;
  }
}

async function loadJobs(args) {
  const jobs = [];
  if (args.manifest) {
    const data = JSON.parse(await readFile(args.manifest, "utf8"));
    for (const item of data.diagrams || []) {
      let language = (item.type || "mermaid").toLowerCase();
      if (language === "dot") language = "graphviz";
      jobs.push({ id: item.id, type: language, source: item.source });
    }
  }
  for (const file of args.files) {
    const language = EXT_TO_TYPE[extname(file).toLowerCase()] || args.type;
    jobs.push({ id: basename(file, extname(file)), type: language, source: await readFile(file, "utf8") });
  }
  if (!jobs.length) throw new Error("No diagrams. Pass files and/or --manifest.");
  return jobs;
}

const args = parseArgs(process.argv.slice(2));
const formats = args.format.split(",").map((s) => s.trim().toLowerCase()).filter(Boolean);
await mkdir(args.outDir, { recursive: true });
if (args.emitMmd) await mkdir(args.emitMmd, { recursive: true });
const jobs = await loadJobs(args);
for (const job of jobs) {
  if (args.emitMmd) {
    const dest = join(args.emitMmd, `${job.id}.mmd`);
    await writeFile(dest, job.source, "utf8");
    console.log(`wrote ${dest}`);
  }
  if (args.dryRun) continue;
  for (const fmt of formats) {
    const { payload, via } = await render(args.endpoint, job.type, fmt, job.source);
    const dest = join(args.outDir, `${job.id}.${fmt}`);
    await writeFile(dest, payload);
    console.log(`wrote ${dest} (${payload.length} bytes via ${via})`);
  }
}
