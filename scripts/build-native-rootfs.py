"""Build the real target binary in the upstream's pinned Ubuntu18 userland.
Run as root inside WSL. Uses chroot instead of requiring a Docker daemon.
Only writes a local build cache and this project's build outputs.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import urllib.request
import stat

PROJECT = Path(__file__).resolve().parents[1]
BASE = Path('/home/athar/.cache/iyt-toolchain')
ROOT = BASE/'rootfs'
DIGEST = 'sha256:dca176c9663a7ba4c1f0e710986f5a25e672842963d95b960191e2d9f7185ebe'
if os.geteuid() != 0:
    raise SystemExit('Run inside WSL as root; this builds locally and never contacts the vehicle.')
BASE.mkdir(parents=True, exist_ok=True)
def get(url, headers=None):
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers or {}), timeout=90) as response:
        return response.read()
if not (ROOT/'bin/sh').exists():
    token = json.loads(get('https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/ubuntu:pull'))['token']
    headers = {'Authorization': 'Bearer '+token, 'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}
    raw = get('https://registry-1.docker.io/v2/library/ubuntu/manifests/'+DIGEST, headers)
    assert 'sha256:'+hashlib.sha256(raw).hexdigest() == DIGEST, 'Image manifest hash mismatch'
    manifest = json.loads(raw)
    (BASE/'manifest.json').write_bytes(raw)
    ROOT.mkdir(exist_ok=True)
    for layer in manifest['layers']:
        digest = layer['digest']
        data = get('https://registry-1.docker.io/v2/library/ubuntu/blobs/'+digest, headers)
        assert 'sha256:'+hashlib.sha256(data).hexdigest() == digest, 'Image layer hash mismatch'
        archive = BASE/(digest.replace(':', '-')+'.tar.gz')
        archive.write_bytes(data)
        # The official pinned layer is trusted; reject member traversal explicitly.
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                assert not member.name.startswith('/') and '..' not in Path(member.name).parts
        subprocess.run(['tar', '-xzf', str(archive), '-C', str(ROOT), '--exclude=dev/*'], check=True)
shutil.copyfile('/etc/resolv.conf', ROOT/'etc/resolv.conf')
for name, major, minor in [('null', 1, 3), ('zero', 1, 5), ('random', 1, 8), ('urandom', 1, 9), ('tty', 5, 0)]:
    device = ROOT/'dev'/name
    device.parent.mkdir(exist_ok=True)
    if not device.exists():
        os.mknod(device, stat.S_IFCHR | 0o666, os.makedev(major, minor))
    os.chmod(device, 0o666)
if not (ROOT/'usr/bin/g++').exists():
    (ROOT/'etc/apt/sources.list').write_text('deb http://archive.ubuntu.com/ubuntu bionic main universe\ndeb http://archive.ubuntu.com/ubuntu bionic-updates main universe\n')
    subprocess.run(['chroot', str(ROOT), '/bin/sh', '-c', 'apt-get -o Acquire::ForceIPv4=true -o Acquire::http::Timeout=20 -o Acquire::Retries=1 update && DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::ForceIPv4=true -o Acquire::http::Timeout=20 install -y --no-install-recommends g++ make binutils python3 python3-pyelftools ca-certificates'], check=True)
source = PROJECT/'source/native/ytdec'
work = ROOT/'iyt-build'
shutil.copytree(source, work, dirs_exist_ok=True, ignore=shutil.ignore_patterns('build', '__pycache__'))
command = ['chroot', str(ROOT), '/usr/bin/make', '-C', '/iyt-build', 'target-in-docker', 'VERSION=iYT-0.4.1', 'IMAGE=-']
result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
(PROJECT/'reports/target-build.log').write_text(result.stdout)
print(result.stdout, flush=True)
if result.returncode:
    raise SystemExit(result.returncode)
out = PROJECT/'source/native/iyt-daemon/prebuilt'
out.mkdir(exist_ok=True)
shutil.copy2(work/'build/target/ytdec', out/'ytdec')
shutil.copy2(PROJECT/'native/service-lock.cpp', ROOT/'iyt-lock.cpp')
subprocess.run(['chroot', str(ROOT), '/usr/bin/g++', '-std=c++14', '-O2', '-Wall', '-Wextra', '-Werror', '-Wl,--dynamic-linker=/lib/ld-linux-x86-64.so.2', '/iyt-lock.cpp', '-o', '/iyt-lock'], check=True)
subprocess.run(['chroot', str(ROOT), '/usr/bin/python3', '/iyt-build/tools/abi.py', 'check', '/iyt-lock', '/iyt-build/abi/libvsomeip3.so.3.symbols'], check=True)
shutil.copy2(ROOT/'iyt-lock', out/'iyt-lock')
shutil.copy2(work/'build/target/ytdec', source/'build/target/ytdec') if (source/'build/target').exists() else None
print('Built target ELF with upstream loader, glibc and imported-library ABI checks.')
