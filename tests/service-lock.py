from pathlib import Path
import subprocess
import sys
import tempfile
import time
r = Path(__file__).resolve().parents[1]
binary = r/'source/native/iyt-daemon/prebuilt/iyt-lock'
loader = '/lib64/ld-linux-x86-64.so.2'
with tempfile.TemporaryDirectory() as tmp:
    lock = str(Path(tmp)/'instance.lock')
    command = [loader, str(binary), lock]
    first = subprocess.Popen(command + [sys.executable, '-c', 'import time; time.sleep(30)'])
    try:
        for _ in range(100):
            if Path(lock).exists():
                break
            time.sleep(0.01)
        second = subprocess.run(command + ['/bin/true'], capture_output=True, text=True)
        assert second.returncode == 75 and 'E_ALREADY_RUNNING' in second.stderr
    finally:
        first.terminate()
        first.wait()
    assert subprocess.run(command + ['/bin/true']).returncode == 0
    link = Path(tmp)/'symlink.lock'
    link.symlink_to(lock)
    assert subprocess.run([loader, str(binary), str(link), '/bin/true'], capture_output=True).returncode == 73
print('Bundled target lock: duplicate refused, crash releases lock, symlink refused.')
