from pathlib import Path
import json
r = Path(__file__).resolve().parents[1] / 'source'
# Namespace verified shared memory endpoint consistently on producer and consumer.
for p in r.rglob('*'):
    if p.is_file() and p.suffix in ('.js', '.cpp', '.h', '.md'):
        p.write_text(p.read_text().replace('mgu-video-ridetube', 'mgu-video-iyt'))
p = r / 'native/iyt-daemon/ytd.js'
t = p.read_text().replace("const readline = require('readline');", "const readline = require('readline');\nconst diagnostics = require('./diagnostics');")
t = t.replace("    case 'status':", "    case 'diagnostics': return this.emit(diagnostics.report(this));\n    case 'display_mode': return this.emit({ev: 'error', code: 'E_CLUSTER_UNVALIDATED', msg: 'Only iDrive Screen Only is enabled on hardware; cluster modes require simulator build'});\n    case 'status':")
t = t.replace("    this.emit({ ev: 'error', msg: msg });", "    this.lastError = {code: diagnostics.errorCode(msg), message: msg, at: new Date().toISOString()};\n    this.emit({ ev: 'error', code: this.lastError.code, msg: msg });")
p.write_text(t)
p = r / 'native/iyt-daemon/component.json'
c = json.loads(p.read_text())
c['files'].append({'path': 'diagnostics.js', 'from': 'diagnostics.js', 'mode': '0644'})
p.write_text(json.dumps(c, indent=2) + '\n')
p = r / 'apps/iyt_app/main.js'
t = p.read_text()
start = t.index('        // the drive lock:')
end = t.index('        /* ---------- the daemon', start)
t = t[:start] + '''        // Vehicle input is optional in the desktop simulator. Production remains fail closed.
        const simulator = process.env.RTE_SIMULATOR === '1';
        const noVideo = () => !simulator && parked.moving();

''' + t[end:]
t = t.replace("        const C = { bg: '#0b0f1e', card: '#1a2038', ph: '#232a46', text: '#f1f3ff', dim: '#a4abc8', red: '#ff3f8e', cyan: '#3ad6ff', amber: '#ffd36b' };   // red: the accent (neon pink)", "        const C = require('./theme');")
p.write_text(t)
# Build tooling copies every app .js; theme remains Node 8 compatible.
(r / 'apps/iyt_app/theme.js').write_text("'use strict';\n// BMW-inspired restrained graphite palette; native canvas fonts remain unchanged.\nmodule.exports = { bg: '#10151b', card: '#1b232d', ph: '#293441', text: '#f2f5f8', dim: '#adb9c7', red: '#479be8', cyan: '#9bcdf8', amber: '#f3c16a' };\n")
print('Diagnostics, isolated SHM and parked-only UI integrated.')
