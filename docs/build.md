# Build and publishing

Development uses WSL2 Linux. Node packages are not needed. Run `sh scripts/setup-node.sh` for the pinned Node22 host test runtime (not a deployment dependency), then `python3 scripts/fetch-upstream.py` to restore the public test/build repositories listed in upstream-lock.json if they are absent.

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

QuickJS is rebuilt with scripts/build-quickjs.py in the same pinned target userland. Its complete source archive and digest are committed under native/quickjs. Run scripts/setup-node8-test.sh and scripts/bridge-tests.py to exercise the service against the platform runtime version.
