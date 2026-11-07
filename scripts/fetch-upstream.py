"""Restore pinned public build inputs into this project only."""
from pathlib import Path
import json
import shutil
import subprocess

r = Path(__file__).resolve().parents[1]
lock = json.loads((r/'upstream-lock.json').read_text())
for name, commit in lock.items():
    owner = 'JustAnotherPU' if name == 'ridetube' else 'robertnisipeanu'
    dest = r/'upstream'/name
    if (dest/'.git').is_dir():
        actual = subprocess.check_output(['git', '-C', str(dest), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != commit:
            raise SystemExit(f'{name}: existing checkout differs from lock; preserve it and resolve manually')
        continue
    stage = r/'.tools'/f'fetch-{name}'
    stage.parent.mkdir(exist_ok=True)
    if stage.exists():
        raise SystemExit(f'{stage}: existing staging directory; inspect before retrying')
    subprocess.run(['git', '-c', 'core.autocrlf=false', 'clone', f'https://github.com/{owner}/{name}.git', str(stage)], check=True)
    subprocess.run(['git', '-C', str(stage), 'checkout', '--detach', commit], check=True)
    shutil.copytree(stage, dest, dirs_exist_ok=True)
    print(f'{name}: pinned {commit}')
