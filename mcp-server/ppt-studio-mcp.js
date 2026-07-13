#!/usr/bin/env node
/**
 * ppt-studio-mcp — dependency-free MCP server for PPT Pro Studio.
 *
 * Exposes the PPT production pipeline as MCP tools so ANY MCP-capable
 * LLM (Claude, GPT, Gemini, Cursor, Codex, or any agent runtime) can
 * generate commercial-grade, editable .pptx without needing the skill file.
 *
 * Tools:
 *   generate_ppt  — render a structured brief JSON into .pptx
 *   qa_check      — programmatic quality-gate scan of a .pptx
 *   list_styles   — list available design palettes
 *
 * MIT License. No external dependencies. Runs on stdio JSON-RPC.
 */
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawnSync } = require('child_process');

const SKILL_DIR = path.resolve(__dirname, '..');
// Primary engine: ppt-master SVG->PPTX (hugohe3/ppt-master, 16.6k★, MIT —
// the highest-starred PPTX skill). Wrapped by ppt_master_hifi.py.
const HIFI = path.join(SKILL_DIR, 'scripts', 'ppt_master_hifi.py');
// Deterministic fallback: pure python-pptx renderer (zero external deps
// beyond python-pptx itself).
const GEN = path.join(SKILL_DIR, 'scripts', 'ppt_studio_generate.py');

// --- python resolver (portable across environments) -----------------------
function resolvePython() {
  const candidates = [
    process.env.PPT_STUDIO_PYTHON,
    'python3',
    'python',
    'C:\\Users\\Administrator\\.workbuddy\\binaries\\python\\versions\\3.13.12\\python.exe',
  ].filter(Boolean);
  for (const c of candidates) {
    try {
      const r = spawnSync(c, ['--version'], { timeout: 5000 });
      if (r.status === 0) return c;
    } catch (_) { /* try next */ }
  }
  return 'python3';
}

// --- minimal MCP stdio transport -----------------------------------------
let buf = '';
process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => {
  buf += chunk;
  let idx;
  while ((idx = buf.indexOf('\n')) >= 0) {
    const line = buf.slice(0, idx).trim();
    buf = buf.slice(idx + 1);
    if (line) handleMessage(line);
  }
});
process.stdin.on('end', () => process.exit(0));

function send(obj) {
  process.stdout.write(JSON.stringify(obj) + '\n');
}

const TOOLS = [
  {
    name: 'generate_ppt',
    description: 'Render a structured PPT brief (JSON) into a commercial-grade, fully editable .pptx. Primary engine is ppt-master SVG->PPTX (hugohe3/ppt-master, 16.6k★, MIT) with random per-slide transitions; deterministic python-pptx is the automatic fallback. Supports 5 design palettes and 12 slide types (cover, section, agenda, content, two_column, table, chart, timeline, quote, image, summary, contact). No watermarks, no network.',
    inputSchema: {
      type: 'object',
      properties: {
        brief: {
          type: 'object',
          description: 'The PPT brief JSON. Must contain "slides" array; optional "style" (tech_dark|business_blue|creative_purple|academic_white|minimal_gray), "title", "footer", "page_numbers".',
        },
        out: { type: 'string', description: 'Output .pptx path (e.g. "./deck.pptx").' },
      },
      required: ['brief', 'out'],
    },
  },
  {
    name: 'qa_check',
    description: 'Programmatic quality-gate scan of a generated .pptx: empty-slide detection, placeholder/leftover scanning. Returns a pass/fail report.',
    inputSchema: {
      type: 'object',
      properties: {
        pptx_path: { type: 'string', description: 'Path to the .pptx file to validate.' },
      },
      required: ['pptx_path'],
    },
  },
  {
    name: 'list_styles',
    description: 'List the available design palettes (color schemes) for the PPT brief "style" field.',
    inputSchema: { type: 'object', properties: {} },
  },
];

function handleMessage(line) {
  let msg;
  try { msg = JSON.parse(line); } catch (_) { return; }
  const { id, method } = msg;

  if (method === 'initialize') {
    send({
      jsonrpc: '2.0', id,
      result: {
        protocolVersion: '2024-11-05',
        capabilities: { tools: {} },
        serverInfo: { name: 'ppt-studio-mcp', version: '1.0.0' },
      },
    });
    return;
  }
  if (method === 'notifications/initialized' || method === 'initialized') return;
  if (method === 'tools/list') {
    send({ jsonrpc: '2.0', id, result: { tools: TOOLS } });
    return;
  }
  if (method === 'tools/call') {
    const name = msg.params && msg.params.name;
    const args = (msg.params && msg.params.arguments) || {};
    let result;
    try {
      if (name === 'generate_ppt') result = doGenerate(args);
      else if (name === 'qa_check') result = doQa(args);
      else if (name === 'list_styles') result = doStyles();
      else throw new Error('Unknown tool: ' + name);
      send({ jsonrpc: '2.0', id, result: { content: [{ type: 'text', text: JSON.stringify(result, null, 2) }] } });
    } catch (e) {
      send({ jsonrpc: '2.0', id, error: { code: -32603, message: String(e.message || e) } });
    }
    return;
  }
  // ping etc.
  if (method === 'ping') { send({ jsonrpc: '2.0', id, result: {} }); return; }
}

// --- tool implementations -------------------------------------------------
function runRender(py, script, tmp, out, extra) {
  return spawnSync(py, [script, tmp, '--out', out].concat(extra || []),
                   { encoding: 'utf8', timeout: 180000 });
}

function doGenerate(args) {
  const brief = args.brief;
  if (!brief || !Array.isArray(brief.slides)) throw new Error('brief.slides[] required');
  const out = args.out || path.join(os.tmpdir(), 'ppt-studio-out.pptx');
  const tmp = path.join(os.tmpdir(), 'ppt-studio-brief-' + Date.now() + '.json');
  fs.writeFileSync(tmp, JSON.stringify(brief, null, 2), 'utf8');
  const py = resolvePython();

  // PRIMARY: ppt-master SVG->PPTX (highest-starred PPTX skill).
  let engine = 'ppt-master (ppt_master_hifi.py)';
  let r = runRender(py, HIFI, tmp, out, ['--transition-duration', '0.5']);
  if (r.error || r.status !== 0) {
    // FALLBACK: deterministic python-pptx renderer.
    const why = (r.stderr || r.stdout || String(r.error || '')).trim().slice(0, 300);
    engine = 'python-pptx (ppt_studio_generate.py fallback)';
    r = runRender(py, GEN, tmp, out, []);
    if (r.error) throw new Error('python error: ' + r.error.message);
    if (r.status !== 0) {
      throw new Error('render failed (primary: ' + why + ' | fallback: '
                      + (r.stderr || r.stdout) + ')');
    }
  }
  return { ok: true, file: path.resolve(out), engine, stdout: (r.stdout || '').trim() };
}

function doQa(args) {
  const p = args.pptx_path;
  if (!p || !fs.existsSync(p)) throw new Error('pptx_path not found: ' + p);
  const py = resolvePython();
  // Accurate scan: only inspect real text runs (<a:t>) inside slide XML,
  // so binary/XML boilerplate (e.g. chart OOXML) never causes false positives.
  const code = [
    'import sys, zipfile, re, json',
    "z = zipfile.ZipFile(sys.argv[1])",
    "slides = sorted([n for n in z.namelist() if re.match(r'ppt/slides/slide\\d+\\.xml$', n)])",
    "ph_list = ['TODO','Lorem','[图片缺失','【待','xxxx']",
    "found = set(); empty = 0",
    'for n in slides:',
    '    xml = z.read(n).decode("utf-8","ignore")',
    "    texts = re.findall(r'<a:t>(.*?)</a:t>', xml, re.S)",
    "    joined = ' '.join(texts)",
    '    if not texts: empty += 1',
    '    for ph in ph_list:',
    "        if ph in joined: found.add(ph)",
    "    if re.search(r'\\{\\{[^}]+\\}\\}', joined): found.add('{{...}}')",
    "print(json.dumps({'slides':len(slides),'empty':empty,'placeholders':sorted(found),'pass': len(found)==0 and empty==0}))",
  ].join('\n');
  const r = spawnSync(py, ['-c', code, p], { encoding: 'utf8', timeout: 30000 });
  if (r.error) throw new Error('python error: ' + r.error.message);
  if (r.status !== 0) throw new Error('qa failed: ' + (r.stderr || r.stdout));
  let parsed;
  try { parsed = JSON.parse(r.stdout.trim().split('\n').pop()); }
  catch (_) { throw new Error('qa parse error: ' + r.stdout); }
  return { ok: true, file: path.resolve(p), ...parsed };
}

function doStyles() {
  return {
    ok: true,
    styles: [
      { id: 'tech_dark', label: '深色科技风 (Tech Dark)' },
      { id: 'business_blue', label: '商务蓝 (Business Blue)' },
      { id: 'creative_purple', label: '创意紫 (Creative Purple)' },
      { id: 'academic_white', label: '学术白 (Academic White)' },
      { id: 'minimal_gray', label: '简约灰 (Minimal Gray)' },
    ],
  };
}

// banner to stderr so stdout stays clean for JSON-RPC
process.stderr.write('ppt-studio-mcp running...\n');
