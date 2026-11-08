"""Read-only host preflight; reports missing capabilities rather than faking artifacts."""
from pathlib import Path
import json
import platform
import shutil
import subprocess
import os
r = Path(__file__).resolve().parents[1]
os.environ['PATH'] = str(r/'.tools/node-v22.23.0-linux-x64/bin') + ':' + os.environ['PATH']
facts = {name: shutil.which(name) for name in ['node', 'python3.12', 'g++', 'make', 'docker', 'ffmpeg', 'flock']}
facts['platform'] = platform.platform()
facts['sdk_present'] = (r/'source/oap-sdk/index.js').is_file() and (r/'source/oap-sdk/package.json').is_file()
facts['target_toolchain'] = 'Ubuntu 18.04 amd64, GCC 7.5, glibc 2.27; pinned Dockerfile in source/native/ytdec/docker'
facts['local_sdk_required'] = False
facts['sdk_source'] = 'MGU Store stock donor on the head unit'
facts['store_package_ready'] = all((r/'dist/release'/n).is_file() for n in ['catalog.json', 'iyt_app@0.5.0.tgz', 'iyt-daemon@0.5.0.tgz'])
facts['target_binaries_built'] = all((r/'source/native/iyt-daemon/prebuilt'/n).is_file() for n in ['ytdec', 'iyt-lock'])
facts['vehicle_connected'] = False
(r/'reports/preflight.json').write_text(json.dumps(facts, indent=2)+'\n')
print(json.dumps(facts, indent=2))
