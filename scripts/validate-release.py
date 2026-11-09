from pathlib import Path
import hashlib
import json
import subprocess
import tarfile

r = Path(__file__).resolve().parents[1]
release = r/'dist/release'
catalog = json.loads((release/'catalog.json').read_text())
report = {'name': 'iYT', 'version': '0.5.4', 'checks': []}
for component in catalog['components']:
    artifact = component['artifact']
    data = (release/artifact['name']).read_bytes()
    assert len(data) == artifact['size']
    assert hashlib.sha256(data).hexdigest() == artifact['sha256']
    report['checks'].append(component['id']+': size and SHA256 verified')
with tarfile.open(release/'iyt_app@0.5.4.tgz') as app:
    names = app.getnames()
    assert not any('oap-sdk' in n for n in names)
    package = json.load(app.extractfile('package/package.json'))
    assert package['name'] == 'iyt_app' and package['version'] == '0.5.4'
    spec = json.load(app.extractfile('package/javascript/kit/app-spec.json'))
    assert spec['title'] == 'iYT'
    assert not any(s['key'] == 'video_driving' for s in spec['settings'])
    assert any(s['key'] == 'clusterVideo' and s['default'] is False for s in spec['settings'])
    permissions = json.load(app.extractfile('package/manifest.json'))
    gear = permissions['proxies']['de.bmw.infrastructure.VehicleInformation']['attributes']
    assert gear['statusGearboxDrive'] == 's' and gear['DataPowerTrain2'] == 's'
    assert 'package/javascript/kit/cluster-vehicle.js' in app.getnames()
    assert 'SETTINGS' in spec['stateIds']
    view = next(s for s in spec['screens'] if s['name'] == 'VIEW')
    assert {'BTN_SETTINGS','BTN_EXIT'}.issubset({b[0] for b in view['buttons']})
    report['checks'].append('SDK-free app identity, native screens and settings verified')
with tarfile.open(release/'iyt-daemon@0.5.4.tgz') as tool:
    manifest = json.load(tool.extractfile('component.json'))
    for file in manifest['files']:
        data = tool.extractfile('files/'+file['path']).read()
        assert hashlib.sha256(data).hexdigest() == file['sha256']
    assert not any(n.endswith('.so') or '/stub/' in n for n in tool.getnames())
    unit = tool.extractfile('units/iyt-daemon.service').read().decode()
    assert '/current/iyt-lock ' in unit and '/var/opt/iyt-daemon/current/ytd.js' in unit
    assert '/usr/bin/node ' in unit and 'jap-node22' not in unit
    assert 'jap-node22' not in manifest['requires']
    assert manifest['requires']['cluster-render'] == '0.4.2'
    assert any(f['path'] == 'cluster-render-MPL-2.0.txt' for f in manifest['files'])
    assert {'qjs','network.js','audio-files.js','QuickJS-MIT.txt'}.issubset({f['path'] for f in manifest['files']})
    report['checks'].append('service manifest, bundled lock, unit and every payload digest verified; no link stubs shipped')
native = r/'source/native/ytdec'
assert 'jap-node22' not in json.loads((r/'source/native/iyt-daemon/component.json').read_text())['requires']
for name in ['ytdec', 'iyt-lock', 'qjs']:
    binary = r/'source/native/iyt-daemon/prebuilt'/name
    assert binary.read_bytes().startswith(b'\x7fELF')
    abi = subprocess.run(['python3', str(native/'tools/abi.py'), 'check', str(binary), str(native/'abi/libvsomeip3.so.3.symbols')], capture_output=True, text=True, check=True)
    report['checks'].append(name+': '+abi.stdout.strip())
imports = subprocess.run(['python3', str(native/'tools/woc_abi.py'), 'check-imports', str(r/'source/native/iyt-daemon/prebuilt/ytdec'), '--prefix', 'MFX', 'va', '--', str(native/'abi/libmfx.symbols'), str(native/'abi/libva.symbols'), str(native/'abi/libva-drm.symbols')], capture_output=True, text=True, check=True)
report['checks'].append(imports.stdout.strip())
report['hardwareValidated'] = False
report['status'] = 'Store discovery and install artifacts ready; actual vehicle validation pending'
(r/'reports/release-validation.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
