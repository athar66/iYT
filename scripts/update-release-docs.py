from pathlib import Path
import json

r = Path(__file__).resolve().parents[1]
documents = {
'README.md': '''# iYT

Native YouTube app for BMW MGU iDrive 7, derived from RideTube. Includes native audio, Intel hardware H.264 video, signed-in feeds, search, continue watching, quality controls and diagnostics.

## Install from MGU Store

Add **athar66/iYT** as a source and select the **main branch**. The repository's `mgu-repo.json` lists **iYT** and **iYT playback service**. Install iYT; the Store installs its declared dependencies first. If the Store offers Releases, that channel uses the `catalog` release and requires its assets to have been published; main works directly from this repository.

The required Node22 runtime is published by **JustAnotherPU/mgu-apps**. Add that repository's Releases source if it is not already available. Standard Store sources supply mgu-deploy, mgu-python and mgu-render; mgu-inputgate comes from cauliflowermossgrape/idrive7-apps.

**You do not need a BMW SDK on your PC.** The Store generates `oap-sdk` from a stock BMW app already on the head unit. No BMW SDK or firmware is included here.

## Included deployment files

- Root `mgu-repo.json`: Store discovery and on-head-unit app build.
- `source/apps/iyt_app`: native app, settings and icon.
- `source/native/iyt-daemon`: service manifest and committed target binaries under prebuilt/.
- `dist/release`: SDK-free app package, native service package, checksummed catalog and icon, ready for a GitHub release tagged `catalog`.

App id `iyt_app`; service id `iyt-daemon`; separate data/cache/control/frame namespaces preserve original RideTube. Avoid simultaneous audio playback in both apps: BMW's generic media source is shared.

## Verification and limits

Target decoder and lock wrapper built with GCC7.5/glibc2.27 in the exact pinned Ubuntu18 image userland. Loader/library ABI and all 18 media imports passed checks. The actual Store reader discovers both components, packages the service, and prepares the real SDK-free app using a synthetic donor in host tests. Native app frames and controller flows run against the upstream head-unit stub.

**Store-ready does not mean verified on your car.** No installation or vehicle test has been performed. Firmware-specific startup, audio clock, GPU behaviour and sustained playback still need validation. See [release validation](reports/release-validation.json), [test results](reports/checks.json) and [remaining work](docs/known-limitations.md).

Real cluster video remains disabled; cluster modes are development/simulator-only. Vehicle-state input is optional in the simulator. Main-screen hardware playback retains parked-only behaviour.

GPL-3.0-or-later, derived from JustAnotherPU/RideTube with original notices preserved. See [licences](licenses/NOTICE.md), source/LICENSE and source/THIRD_PARTY_LICENSES.
''',
'docs/build.md': '''# Build and publishing

Development uses WSL2 Linux. Node packages are not needed. Run `sh scripts/setup-node.sh` for the pinned Node22 host runtime, then `python3 scripts/fetch-upstream.py` to restore the public test/build repositories listed in upstream-lock.json if they are absent.

Run `python3 source/kit/tools/build.py iyt_app` to build the native app. **No local BMW SDK is required.** If source/oap-sdk is absent, the package intentionally omits it and the Store supplies it from a stock donor on the head unit. A repo-tree installation asks the Store to supply source/oap-sdk to the writable build copy; that generated SDK is never committed or published.

Native binaries are committed under source/native/iyt-daemon/prebuilt. To rebuild: run scripts/build-native-rootfs.py as root inside WSL, or use the original source/native/ytdec Docker build and target ABI checks. The WSL builder downloads the exact upstream-pinned Ubuntu18 OCI manifest/layers and verifies each digest, then uses GCC7.5/glibc2.27. It does not require Docker or contact a vehicle. Its Linux build cache is /home/athar/.cache/iyt-toolchain.

Run `python3 scripts/prepare-store.py` to verify/stage the official pinned yt-dlp source zipapp, with its expected SHA256. Source form runs under the declared mgu-python Python3.12 dependency without host bytecode or local Python3.12 precompilation.

With the local Node22 directory on PATH:

1. Run `node tests/store-discovery.js` to exercise the real Store repo reader and tool packer.
2. Run `python3 scripts/assemble-release.py` to create dist/release assets for athar66/iYT.
3. Run `node tests/store-sdk-donor.js` for synthetic-donor SDK generation against the actual app package.
4. Run `python3 scripts/validate-release.py` for payload digests and target ABI checks (needs binutils and pyelftools).
5. Run `python3 scripts/run_checks.py` for baseline/enhanced suites; baseline's original macOS-only FFprobe helper is a recorded failure. Enhanced tests must pass.

Commit mgu-repo.json, source and prebuilt payloads to main. Users can then add athar66/iYT and choose main. For the Releases channel, upload every dist/release file to a non-draft GitHub release tagged catalog. Catalog URLs are already set to https://github.com/athar66/iYT/releases/download/catalog/.

No publication script installs to a vehicle. Release packages contain no SDK, link-only stubs or simulator binaries.
''',
'docs/installation.md': '''# MGU Store installation

Add athar66/iYT in Store → Sources, choose main, refresh, then select iYT → Install. The Store discovers the app and service through root mgu-repo.json and builds the app locally using its stock BMW donor SDK. You do not download, extract or supply a BMW SDK yourself.

If jap-node22 is missing from available dependencies, add JustAnotherPU/mgu-apps as a Releases source. Leave the standard Store/default application sources enabled for mgu-deploy, mgu-python, mgu-render and mgu-inputgate.

The main branch path is ready once the repository files are pushed. A separate Releases channel requires the catalog release assets to be published; the prepared assets are in dist/release.

Names: iyt_app (app), iyt-daemon (service), /var/opt/iyt-daemon (data), /run/iyt-daemon/ctl.sock (control) and /dev/shm/mgu-video-iyt (video). The bundled iyt-lock enforces one daemon instance; it requires no firmware-provided flock command.

Original RideTube is preserved. Stop its playback before using iYT because BMW exposes the same generic media audio source. Uninstall iYT and iYT playback service only through the Store. Shared dependencies stay if other apps need them.

This release has host tests and target ABI validation, but no actual car installation result. Keep the car parked with stable power during the owner's eventual Store installation. Real cluster video is not enabled.
'''
}
for name, content in documents.items():
    (r/name).write_text(content)
# Replace obsolete packaging blockers in the remaining status documents.
for name in ['docs/known-limitations.md', 'docs/deliverables.md', 'docs/compatibility.md', 'reports/RESULTS.md']:
    p = r/name
    text = p.read_text()
    text = text.replace('No Docker/Python3.12/BMW SDK: target release binary, ABI verification and Store package remain blocked. Emulator visual/controller verification is unavailable.', 'Target binaries and Store install artifacts are now built and ABI-checked. No local SDK is needed. Real firmware/emulator validation remains outstanding.')
    text = text.replace('Build pipeline supplied; no installable artifact because target tools/SDK missing', 'SDK-free app and genuine target service artifacts built; root Store manifest validated; vehicle installation untested')
    text = text.replace('No deployable target binary or Store package was generated; see preflight.json and docs/known-limitations.md.', 'Target binaries and SDK-free Store packages were subsequently built; see release-validation.json and docs/known-limitations.md.')
    text = text.replace('current host binaries are test-only', 'host test binaries are test-only; prebuilt/ytdec and prebuilt/iyt-lock are target ABI-checked')
    p.write_text(text)
print('Updated iYT Store installation/build documentation; corrected local SDK requirement.')
