"""Deterministic GPL source distribution, explicitly not a Store package."""
from pathlib import Path
import gzip
import hashlib
import io
import json
import tarfile

r = Path(__file__).resolve().parents[1]
out = r/'dist'
out.mkdir(exist_ok=True)
files = []
for directory in ['source', 'native', 'tests', 'scripts', 'docs', 'licenses']:
    for p in (r/directory).rglob('*'):
        rel = p.relative_to(r)
        if p.is_file() and not any(x in rel.parts for x in ['build', 'dist', '__pycache__', 'oap-sdk']):
            files.append(p)
# Cluster client sources required to compile the adapter retain their own licence.
cr = r/'upstream/idrive-apps/native/cluster-render'
for d in ['client', 'include/cluster_render']:
    files.extend(p for p in (cr/d).glob('*') if p.is_file())
for name in ['README.md', 'DESIGN.md', 'UX-CONTRACT.md', 'upstream-lock.json']:
    files.append(r/name)
files.extend(p for p in (r/'reports').glob('*') if p.is_file() and 'issues' not in p.name)
for name in ['LICENSE', 'PROTOCOL.md']:
    if (cr/name).exists(): files.append(cr/name)
archive = out/'iyt-0.4.0-source.tar.gz'
with archive.open('wb') as f, gzip.GzipFile(fileobj=f, mode='wb', filename='', mtime=0) as gz, tarfile.open(fileobj=gz, mode='w', format=tarfile.PAX_FORMAT) as tar:
    for p in sorted(set(files)):
        data = p.read_bytes()
        info = tarfile.TarInfo('iyt/' + p.relative_to(r).as_posix())
        info.size = len(data)
        info.mode = 0o755 if p.suffix == '.sh' else 0o644
        info.uid = info.gid = info.mtime = 0
        tar.addfile(info, io.BytesIO(data))
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
(out/'SHA256SUMS').write_text(f'{digest}  {archive.name}\n')
with tarfile.open(archive) as t:
    assert not any('/oap-sdk/' in n or '/.git/' in n for n in t.getnames())
print(f'{archive.name}: {archive.stat().st_size} bytes, SHA256 {digest}')
