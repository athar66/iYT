#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
export PATH="$PWD/.tools/node-v22.23.0-linux-x64/bin:$PATH"
mode=${1:-enhanced}
if [ "$mode" = baseline ]; then
    tree=upstream/ridetube
    daemon=jap-ridetube-d
else
    tree=source
    daemon=iyt-daemon
fi
for test in test_runtime test_life test_parked test_qr; do
    node "$tree/kit/tools/$test.js"
done
node "$tree/native/$daemon/test/test_ytd.js"
node "$tree/native/$daemon/test/test_thumb.js"
python3 -I "$tree/native/$daemon/test/test_ytfetch.py"
make -C "$tree/native/ytdec" test
if [ "$mode" != baseline ]; then
    python3 tests/reliability_test.py
    node --test tests/diagnostics.test.js
fi
