#!/bin/sh
# LOCAL BUILD ONLY. Never installs to a vehicle or publishes assets.
set -eu
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/node-v22.23.0-linux-x64/bin:$PATH"
test -f source/native/iyt-daemon/prebuilt/ytdec || { echo 'Rebuild target binaries with scripts/build-native-rootfs.py first' >&2; exit 1; }
python3 scripts/prepare-store.py
python3 source/kit/tools/build.py iyt_app
node tests/store-discovery.js
python3 scripts/assemble-release.py
node tests/store-sdk-donor.js
python3 scripts/validate-release.py
