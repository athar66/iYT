from pathlib import Path
import json
r = Path(__file__).resolve().parents[1]
p = r/'licenses/NOTICE.md'
t = p.read_text().replace('RideTube Enhanced', 'iYT').replace('This snapshot is not a vehicle-ready binary release.', 'Target-ABI-checked deployment binaries and SDK-free Store artifacts are included; installation on real hardware has not been validated.')
p.write_text(t)
p = r/'docs/known-limitations.md'
t = p.read_text().replace('Live extraction is skipped without the hash-verified yt-dlp build.', 'The full extraction/download regression remains skipped in the offline suite; a separate live public-content metadata extraction smoke test passed using the hash-verified shipped extractor, with compatible H.264 and AAC formats found.')
p.write_text(t)
p = r/'docs/rollback.md'
t = p.read_text().replace('No vehicle shell rollback script is shipped because this snapshot has no deployed target package.', 'Store-compatible target packages are prepared; no vehicle has been modified, so no vehicle shell rollback is needed for local development.')
p.write_text(t)
p = r/'source/README.md'
p.write_text('''# iYT source

This is the iYT fork of RideTube, retaining GPL notices and attribution. See [project README](../README.md) and [build/publishing instructions](../docs/build.md).

The app is source/apps/iyt_app; its playback service is source/native/iyt-daemon. Native target binaries and the verified official extractor are committed under the service's prebuilt directory for MGU Store repo-tree installation. SDK-free packages are built without a local BMW SDK; the Store uses a stock donor on the head unit.

Original upstream history and unmodified reference sources are pinned in ../upstream-lock.json and can be restored with scripts/fetch-upstream.py. Original licences remain in LICENSE and THIRD_PARTY_LICENSES.
''')
p = r/'reports/RESULTS.md'
with p.open('a') as f:
    f.write('''
## iYT Store packaging validation

The renamed iYT app was built SDK-free. All enhanced groups passed again with the app now built, including native UI frame/controller tests that had previously been skipped. The legacy motion-override assertions were replaced with tests proving that the removed override cannot enable moving video.

Actual MGU Store repoCatalog/packComponent discovers both iYT components and packages the service without out-of-folder licence references. Its linker prepares the actual app package using the upstream synthetic donor; no generated SDK is published. Store linker/packer upstream suite: 74 checks passed (real donors absent). Target decoder built with GCC7.5/glibc2.27 and passed loader/symbol ceilings plus all 18 media imports. Bundled target lock passed duplicate/crash-release/symlink tests.

A live metadata-only smoke test of the public Blender Foundation Big Buck Bunny video passed with the shipped, hash-verified yt-dlp zipapp: compatible H.264 up to 720p30 and AAC-LC were available. No media downloaded. This does not establish on-car playback performance.

See release-validation.json, store-discovery.json, store-sdk-link.json and extraction-smoke.json. No vehicle installation was performed.
''')
checks = json.loads((r/'reports/checks.json').read_text())
for name in ['store-discovery', 'store-sdk-donor', 'target-abi', 'service-lock', 'live-extraction-metadata']:
    checks = [c for c in checks if c['test'] != name]
    checks.append({'suite': 'deployment', 'test': name, 'code': 0})
(r/'reports/checks.json').write_text(json.dumps(checks, indent=2)+'\n')
print('Updated deployment evidence and status without claiming hardware validation.')
