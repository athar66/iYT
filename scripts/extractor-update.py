"""Offline, explicitly supplied extractor candidate validation and reversible local staging.
No network downloads, no vehicle writes and no execution of the candidate.
"""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import zipfile

ap = argparse.ArgumentParser()
ap.add_argument('--candidate', type=Path, required=True)
ap.add_argument('--sha256', required=True, help='Expected digest obtained independently from the official release')
ap.add_argument('--stage', type=Path, required=True, help='Local development staging directory')
a = ap.parse_args()
if not a.candidate.is_file() or a.candidate.stat().st_size > 32 << 20:
    ap.error('candidate missing or larger than 32 MiB')
digest = hashlib.file_digest(a.candidate.open('rb'), 'sha256').hexdigest()
if digest.lower() != a.sha256.lower():
    ap.error('E_UPDATE_HASH: SHA-256 mismatch')
with zipfile.ZipFile(a.candidate) as z:
    names = z.namelist()
    if any(n.startswith(('/', '\\')) or '..' in Path(n).parts or n.endswith(('.so', '.dll', '.pyd')) for n in names):
        ap.error('E_UPDATE_LAYOUT: unsafe path or native code')
    if sum(i.file_size for i in z.infolist()) > 128 << 20:
        ap.error('E_UPDATE_LIMIT: uncompressed archive too large')
    required = ['yt_dlp/version.py', 'yt_dlp/__init__.py', '__main__.py']
    if not all(n in names for n in required):
        ap.error('E_UPDATE_LAYOUT: official source zipapp required')
    tree = ast.parse(z.read('yt_dlp/version.py'))
    version = next((n.value.value for n in tree.body if isinstance(n, ast.Assign) and
                    any(isinstance(t, ast.Name) and t.id == '__version__' for t in n.targets) and
                    isinstance(n.value, ast.Constant)), None)
    if not isinstance(version, str):
        ap.error('E_UPDATE_VERSION: version not found')
a.stage.mkdir(parents=True, exist_ok=True)
current = a.stage / 'yt-dlp.zipapp'
if current.exists():
    shutil.copy2(current, a.stage/'yt-dlp.previous.zipapp')
shutil.copyfile(a.candidate, a.stage/'yt-dlp.pending.zipapp')
os.replace(a.stage/'yt-dlp.pending.zipapp', current)
(a.stage/'version.json').write_text(json.dumps({'version': version, 'sha256': digest, 'status': 'staged only; regression testing and Python 3.12 repack still required'}, indent=2))
print(f'Staged {version}; no candidate code executed.')
