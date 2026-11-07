#!/bin/sh
# Offline deployment checks for the extractor, bundled QuickJS and platform bridge.
set -eu
d=$(cd "$(dirname "$0")" && pwd)
[ -x "$d/iyt-lock" ] || { echo 'E_DEPENDENCY: bundled iyt-lock is missing' >&2; exit 1; }
/var/opt/mgu-python/current/bin/python3 -I -c "import sys;sys.path.insert(0,'$d/ytdlp.pyz');import yt_dlp,yt_dlp_ejs"
"$d/qjs" -e 'if (1+1 !== 2) throw Error("QuickJS self-test failed");'
exec /usr/bin/node -e "require('$d/vendor/jpeg-js/decoder.js');require('$d/thumb.js');require('$d/network.js')"
