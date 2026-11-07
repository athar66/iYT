"""WSL runner: captures failures and skips without hiding subsequent checks."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import time

r = Path(__file__).resolve().parents[1]
cached=Path('/home/athar/.cache/iyt-host-tools/node22-bin')
os.environ['PATH'] = str(cached if (cached/'node').exists() else r/'.tools/node-v22.23.0-linux-x64/bin') + ':' + os.environ['PATH']
reports = r / 'reports'
reports.mkdir(exist_ok=True)
baseline = r / '.tools/baseline'
if not baseline.exists():
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', '--no-hardlinks', str(r/'upstream/ridetube'), str(baseline)], check=True)
only_enhanced = os.environ.get('RTE_CHECK_SUITE') == 'enhanced'
results = [x for x in json.loads((reports/'checks.json').read_text()) if x['suite'] == 'baseline'] if only_enhanced and (reports/'checks.json').exists() else []
for name, tree, daemon in [('baseline', baseline, 'jap-ridetube-d'), ('enhanced', r/'source', 'iyt-daemon')]:
    if only_enhanced and name == 'baseline':
        continue
    checks = [(t, ['node', str(tree/'kit/tools'/f'{t}.js')]) for t in ['test_runtime', 'test_life', 'test_parked', 'test_qr', 'test_ridetube']]
    checks += [('daemon', ['node', str(tree/'native'/daemon/'test/test_ytd.js')]),
               ('thumbnails', ['node', str(tree/'native'/daemon/'test/test_thumb.js')]),
               ('media', ['python3', '-I', str(tree/'native'/daemon/'test/test_ytfetch.py')]),
               ('native', ['make', '-C', str(tree/'native/ytdec'), 'test'])]
    for test, cmd in checks:
        start = time.monotonic()
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=240)
            code, output = p.returncode, p.stdout
        except subprocess.TimeoutExpired as e:
            code, output = 124, str(e.stdout)
        (reports / f'{name}-{test}.log').write_text(output)
        entry = dict(suite=name, test=test, code=code, duration_s=round(time.monotonic()-start, 3))
        results.append(entry)
        print(json.dumps(entry), flush=True)
        (reports/'checks.json').write_text(json.dumps(results, indent=2)+'\n')
for name, cmd in [('regressions', ['python3', str(r/'tests/reliability_test.py')]),
                  ('network-dns', ['node', str(r/'tests/network-regression.js')]),
                  ('updater', ['python3', str(r/'tests/updater_test.py')]),
                  ('diagnostics', ['node', '--test', str(r/'tests/diagnostics.test.js')]),
                  ('router', ['sh', str(r/'scripts/native-tests.sh')])]:
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
    (reports/f'{name}.log').write_text(p.stdout)
    results.append(dict(suite='enhanced', test=name, code=p.returncode))
(reports/'checks.json').write_text(json.dumps(results, indent=2)+'\n')
raise SystemExit(1 if any(x['code'] for x in results if not only_enhanced or x['suite'] == 'enhanced') else 0)
