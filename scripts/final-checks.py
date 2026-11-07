"""Rerun changed checks and preserve all earlier baseline results."""
from pathlib import Path
import json
import os
import subprocess
r = Path(__file__).resolve().parents[1]
os.environ['PATH'] = str(r/'.tools/node-v22.23.0-linux-x64/bin') + ':' + os.environ['PATH']
report = json.loads((r/'reports/checks.json').read_text())
checks = [
    ('regressions', ['python3', str(r/'tests/reliability_test.py')]),
    ('updater', ['python3', str(r/'tests/updater_test.py')]),
    ('diagnostics', ['node', '--test', str(r/'tests/diagnostics.test.js')]),
    ('media', ['python3', '-I', str(r/'source/native/iyt-daemon/test/test_ytfetch.py')]),
    ('native', ['make', '-C', str(r/'source/native/ytdec'), 'test']),
    ('router', ['sh', str(r/'scripts/native-tests.sh')])]
for name, cmd in checks:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=120)
    (r/'reports'/f'final-{name}.log').write_text(result.stdout)
    report = [x for x in report if not (x['suite'] == 'enhanced' and x['test'] == name)]
    report.append({'suite': 'enhanced', 'test': name, 'code': result.returncode, 'log': f'final-{name}.log'})
    print(f'{name}: {result.returncode}', flush=True)
    (r/'reports/checks.json').write_text(json.dumps(report, indent=2)+'\n')
raise SystemExit(any(x['code'] for x in report if x['suite'] == 'enhanced'))
