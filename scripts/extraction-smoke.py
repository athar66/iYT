"""Public test-content metadata smoke test, no media download or access bypass."""
from pathlib import Path
import json
import subprocess
import sys
import shlex
r = Path(__file__).resolve().parents[1]
wrapper = r/'.tools/qjs-host'
wrapper.write_text('#!/bin/sh\nexec /lib64/ld-linux-x86-64.so.2 '+shlex.quote(str(r/'source/native/iyt-daemon/prebuilt/qjs'))+' "$@"\n')
wrapper.chmod(0o755)
command = [sys.executable, str(r/'source/native/iyt-daemon/prebuilt/ytdlp.pyz'),
    '--skip-download', '--dump-single-json', '--no-playlist', '--no-remote-components',
    '--js-runtimes', 'quickjs:'+str(wrapper),
    '--socket-timeout', '10', '--retries', '1', '--extractor-retries', '1',
    'https://www.youtube.com/watch?v=aqz-KE-bpKQ']
try:
    result = subprocess.run(command, capture_output=True, text=True, timeout=60)
    report = {'content': 'Blender Foundation public Big Buck Bunny test video', 'runtime': 'bundled QuickJS target binary via host loader', 'mediaDownloaded': False, 'code': result.returncode}
    if result.returncode == 0:
        info = json.loads(result.stdout)
        report['title'] = info.get('title')
        report['compatibleH264'] = [{'id':f.get('format_id'), 'height':f.get('height'), 'fps':f.get('fps')} for f in info.get('formats', []) if str(f.get('vcodec', '')).startswith('avc1') and f.get('ext') == 'mp4' and f.get('protocol') == 'https' and 0 < (f.get('fps') or 0) <= 30 and 0 < (f.get('height') or 0) <= 720]
        report['aacLcAvailable'] = any(f.get('acodec') == 'mp4a.40.2' for f in info.get('formats', []))
    else:
        # No signed URLs/auth material is written; keep only the final diagnostic line.
        report['error'] = result.stderr.strip().splitlines()[-1][:500] if result.stderr.strip() else 'extractor failed'
except subprocess.TimeoutExpired:
    report = {'content':'public test video', 'mediaDownloaded':False, 'code':124, 'error':'metadata extraction exceeded 60s; not a playback pass'}
(r/'reports/extraction-smoke.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
