from pathlib import Path
import hashlib
import json
import shutil

r = Path(__file__).resolve().parents[1]
(r/'licenses').mkdir(exist_ok=True)
shutil.copy2(r/'source/LICENSE', r/'licenses/GPL-3.0.txt')
shutil.copy2(r/'upstream/idrive-apps/LICENSES/MPL-2.0.txt', r/'licenses/MPL-2.0.txt')
(r/'licenses/NOTICE.md').write_text('''# Attribution and modifications

iYT is a modified RideTube, GPL-3.0-or-later, based on the exact revision in upstream-lock.json. Original copyright JustAnotherPU and Robert Nisipeanu retained. Modifications in this development snapshot were made 7 November 2026: fork identities, service lifecycle, download integrity/resource limits, diagnostics/theme, native allocation guards and presentation observer. Original functionality and tests remain unless explicitly documented in docs/audit.md.

Cluster client/protocol source: Robert Nisipeanu, MPL-2.0, unmodified, from the pinned iDrive Apps repository. MPL text is included. Other original notices remain in source/THIRD_PARTY_LICENSES, source/kit/LICENSE and source/native/ytdec/abi/include/mfx/LICENSE. No BMW SDK or firmware binary is redistributed.

New project code is GPL-3.0-or-later unless its file states otherwise. All corresponding modified source and build scripts are included in the source distribution. This snapshot is not a vehicle-ready binary release.
''')
changes = []
for p in sorted((r/'source').rglob('*')):
    if not p.is_file() or any(x in p.relative_to(r/'source').parts for x in ['build', 'dist', '__pycache__']):
        continue
    rel = p.relative_to(r/'source').as_posix()
    original = rel.replace('iyt-daemon', 'jap-ridetube-d').replace('iyt_app', 'jap_ridetube')
    before = r/'upstream/ridetube'/original
    data = p.read_bytes()
    old = before.read_bytes().replace(b'\r\n', b'\n') if before.exists() else None
    if data.replace(b'\r\n', b'\n') != old:
        if p.suffix in ['.js', '.cpp', '.h', '.py']:
            text = p.read_text()
            marker = ('#' if p.suffix == '.py' else '//') + ' Modified 2026-11-07 for iYT; see licenses/NOTICE.md and docs/audit.md.\n'
            if marker not in text:
                if text.startswith('#!'):
                    first, rest = text.split('\n', 1)
                    text = first + '\n' + marker + rest
                else:
                    text = marker + text
                p.write_text(text)
            data = p.read_bytes()
        changes.append({'path': 'source/' + rel, 'status': 'modified' if before.exists() else 'added', 'sha256': hashlib.sha256(data).hexdigest()})
(r/'reports/changed-files.json').write_text(json.dumps(changes, indent=2)+'\n')
print(f'{len(changes)} changed/added fork source files recorded; licence notices preserved.')
