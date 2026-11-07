"""Update app/service and release tooling version references before packaging."""
from pathlib import Path
import argparse
import re
p = argparse.ArgumentParser()
p.add_argument('old')
p.add_argument('new')
a = p.parse_args()
assert re.fullmatch(r'\d+\.\d+\.\d+', a.new)
r = Path(__file__).resolve().parents[1]
for directory in ['source', 'scripts', 'tests']:
    for file in (r/directory).rglob('*'):
        if file == Path(__file__).resolve() or not file.is_file() or file.suffix not in ['.js','.py','.sh','.json','.ps1']:
            continue
        if any(part in file.relative_to(r).parts for part in ['build','dist','prebuilt','__pycache__']): continue
        text=file.read_text()
        if a.old in text: file.write_text(text.replace(a.old,a.new))
file=r/'mgu-repo.json'
file.write_text(file.read_text().replace(a.old,a.new))
