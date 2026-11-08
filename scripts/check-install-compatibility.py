"""Compare real built-package permissions with the working 0.4.2 artifact."""
from pathlib import Path
import io
import json
import subprocess
import tarfile

r = Path(__file__).resolve().parents[1]
baseline = subprocess.check_output(['git', 'show', 'v0.4.2:dist/release/iyt_app@0.4.2.tgz'], cwd=r)
def read_manifest(data):
    with tarfile.open(fileobj=io.BytesIO(data)) as package:
        return json.load(package.extractfile('package/manifest.json'))
old = read_manifest(baseline)
new = read_manifest((r/'dist/release/iyt_app@0.5.2.tgz').read_bytes())
for name, permissions in old['proxies'].items():
    assert new['proxies'][name] == permissions, f'Working proxy permissions changed: {name}'
assert old['services'] == new['services'], 'Working offered services changed'
added = set(new['proxies']) - set(old['proxies'])
assert added == {'de.bmw.infrastructure.VehicleInformation', 'de.bmw.infotainment.controlelements.FrontCCU'}
assert new['proxies']['de.bmw.infrastructure.VehicleInformation']['attributes'] == {
    'statusGearboxDrive': 's', 'DataPowerTrain2': 's'}
assert new['proxies']['de.bmw.infotainment.controlelements.FrontCCU']['attributes'] == {'statusRotaryEncoderState': 's'}
report = {'candidate': '0.5.2', 'baseline': 'user-confirmed working 0.4.2 package',
          'existingProxyPermissionsUnchanged': True, 'offeredServicesUnchanged': True,
          'newFieldsNotificationOnly': True,
          'reportedFailureStage': 'GenerateSomeipInterface',
          'bmwAppManagerExecuted': False, 'vehicleInstallValidated': False,
          'stableCatalogChanged': False}
(r/'reports/install-compatibility.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
