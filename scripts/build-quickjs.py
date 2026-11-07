"""Build pinned official QuickJS source in the target Ubuntu18 userland."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import tarfile
import urllib.request
import os
r = Path(__file__).resolve().parents[1]
root = Path('/home/athar/.cache/iyt-toolchain/rootfs')
version = '2026-06-04'
source = r/'native/quickjs'
source.mkdir(exist_ok=True)
archive = source/f'quickjs-{version}.tar.xz'
url = f'https://bellard.org/quickjs/quickjs-{version}.tar.xz'
if not archive.exists():
    with urllib.request.urlopen(url, timeout=60) as response: archive.write_bytes(response.read())
digest = hashlib.sha256(archive.read_bytes()).hexdigest()
record = source/'source.json'
if record.exists():
    assert json.loads(record.read_text())['sha256'] == digest, 'Pinned source digest mismatch'
else:
    record.write_text(json.dumps({'version':version,'url':url,'sha256':digest,'license':'MIT'},indent=2)+'\n')
if os.geteuid()!=0: raise SystemExit('Run as root in WSL to build within the local target userland')
with tarfile.open(archive) as tar:
    assert all(not n.startswith('/') and '..' not in Path(n).parts for n in tar.getnames())
    tar.extractall(root/'quickjs-source', filter='data')
    license_member = next(m for m in tar.getmembers() if m.name.endswith('/LICENSE'))
    (r/'licenses/QuickJS-MIT.txt').write_bytes(tar.extractfile(license_member).read())
work = f'/quickjs-source/quickjs-{version}'
loader = root/'lib/ld-linux-x86-64.so.2'
if not loader.exists():
    loader.symlink_to('/lib/x86_64-linux-gnu/ld-2.27.so')
result = subprocess.run(['chroot', str(root), 'make', '-C', work, '-j2', 'CONFIG_LTO=', 'LDFLAGS=-g -Wl,--dynamic-linker=/lib/ld-linux-x86-64.so.2', 'qjs'], capture_output=True,text=True)
(r/'reports/quickjs-build.log').write_text(result.stdout+result.stderr)
print((result.stdout+result.stderr)[-1800:])
if result.returncode: raise SystemExit(result.returncode)
out = r/'source/native/iyt-daemon/prebuilt/qjs'
shutil.copy2(root/work.lstrip('/')/'qjs', out)
subprocess.run(['strip', str(out)],check=True)
subprocess.run(['python3',str(r/'source/native/ytdec/tools/abi.py'),'check',str(out),str(r/'source/native/ytdec/abi/libvsomeip3.so.3.symbols')],check=True)
print(f'QuickJS target binary: {out.stat().st_size} bytes')
