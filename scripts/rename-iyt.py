from pathlib import Path
import json

r = Path(__file__).resolve().parents[1]
for directory in ['source', 'native', 'tests', 'scripts', 'docs']:
    for p in (r/directory).rglob('*'):
        if not p.is_file() or any(x in p.relative_to(r).parts for x in ['build', 'dist', '__pycache__']):
            continue
        if p.suffix not in ['.py', '.js', '.cpp', '.h', '.md', '.json', '.sh', '.service', '.svg']:
            continue
        if p.name in ['rename-iyt.py', 'LICENSE', 'THIRD_PARTY_LICENSES']:
            continue
        text = p.read_text()
        text = text.replace('rte_ridetube', 'iyt_app').replace('rte-ridetube-d', 'iyt-daemon')
        text = text.replace('mgu-video-rte-ridetube', 'mgu-video-iyt').replace('RideTube Enhanced', 'iYT')
        p.write_text(text)
for relative in ['README.md', 'DESIGN.md', 'UX-CONTRACT.md', '.gitignore']:
    p = r/relative
    p.write_text(p.read_text().replace('RideTube Enhanced', 'iYT').replace('rte_ridetube', 'iyt_app').replace('rte-ridetube-d', 'iyt-daemon').replace('mgu-video-rte-ridetube', 'mgu-video-iyt'))
for old, new in [('source/apps/rte_ridetube', 'source/apps/iyt_app'), ('source/native/rte-ridetube-d', 'source/native/iyt-daemon')]:
    (r/old).rename(r/new)
old = r/'source/native/iyt-daemon/systemd/rte-ridetube-d.service'
old.rename(old.with_name('iyt-daemon.service'))
for p in (r/'source/apps/iyt_app').glob('*.js'):
    p.write_text(p.read_text().replace('RideTube', 'iYT'))
p = r/'source/apps/iyt_app/app.json'
a = json.loads(p.read_text())
a['title'] = 'iYT'
a['description'] = 'YouTube for BMW iDrive 7: search, signed-in shelves and native audio playback. Picture while parked; optional cluster simulator output.'
a['iconGlyph'] = 'iYT'
a['mguHmi'] = ['ID7']
for screen in a['screens']:
    screen['title'] = screen['title'].replace('RideTube', 'iYT')
p.write_text(json.dumps(a, indent=2)+'\n')
p = r/'source/native/iyt-daemon/component.json'
a = json.loads(p.read_text())
a['title'] = 'iYT playback service'
a['description'] = 'iYT native YouTube playback service: verified yt-dlp, BMW MediaPlayer audio and Intel H.264 decoder; independent of original RideTube.'
p.write_text(json.dumps(a, indent=2)+'\n')
print('Renamed application, service, data and frame namespaces to iYT.')
