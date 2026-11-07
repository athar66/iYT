"""Assemble actual SDK-free app and native-service Store release assets."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import shutil
import tarfile

r = Path(__file__).resolve().parents[1]
out = r/'dist/release'
out.mkdir(parents=True, exist_ok=True)
app = r/'source/dist/iyt_app@0.4.0.tgz'
if not app.is_file() or not (out/'iyt-daemon@0.4.0.tgz').is_file():
    raise SystemExit('Build the SDK-free app and run tests/store-discovery.js first.')
# Sorted entries, fixed timestamp and ownership; never redistribute donor SDK.
with tarfile.open(app) as source, (out/app.name).open('wb') as f, gzip.GzipFile(fileobj=f, mode='wb', filename='', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w') as target:
    for member in sorted(source.getmembers(), key=lambda m:m.name):
        if 'node_modules/oap-sdk' in member.name:
            continue
        member.uid = member.gid = member.mtime = 0
        member.uname = member.gname = ''
        data = source.extractfile(member).read() if member.isfile() else None
        member.pax_headers = {}
        target.addfile(member, io.BytesIO(data) if data is not None else None)
shutil.copy2(r/'source/apps/iyt_app/icon.png', out/'iyt_app.png')
shutil.copy2(r/'mgu-store.json', out/'mgu-store.json')
base = 'https://github.com/athar66/iYT/releases/download/catalog/'
published = r/'reports/published-release.json'
private_urls = {}
if published.exists():
    record = json.loads(published.read_text())
    if record.get('private') and record.get('repository') == 'athar66/iYT':
        private_urls = {a['name']: a['url'] for a in record.get('assets', [])}
def artifact(name):
    data = (out/name).read_bytes()
    return {'name': name, 'size': len(data), 'sha256': hashlib.sha256(data).hexdigest(), 'url': private_urls.get(name, base+name)}
service = json.loads((r/'source/native/iyt-daemon/component.json').read_text())
app_entry = {'id': 'iyt_app', 'kind': 'app', 'version': '0.4.0', 'title': 'iYT',
    'description': 'YouTube for BMW iDrive 7: search, signed-in shelves, native audio and hardware H.264 video.',
    'mguHmi': ['ID7'], 'uninstallable': True,
    'requires': {'iyt-daemon': '0.4.0', 'mgu-render': '0.6.11', 'mgu-inputgate': '1.0.0'},
    'artifact': artifact('iyt_app@0.4.0.tgz'), 'icon': 'iyt_app.png',
    'iconSha256': hashlib.sha256((out/'iyt_app.png').read_bytes()).hexdigest()}
tool_entry = {k:service[k] for k in ['id', 'kind', 'version', 'title', 'description', 'requires', 'mguHmi', 'uninstallable']}
tool_entry['artifact'] = artifact('iyt-daemon@0.4.0.tgz')
(out/'catalog.json').write_text(json.dumps({'schema': 2, 'components': [app_entry, tool_entry]}, indent=2)+'\n')
(out/'SHA256SUMS').write_text(''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(out.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'))
print('Prepared real iYT Store catalog assets for https://github.com/athar66/iYT')
