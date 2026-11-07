#!/bin/sh
set -eu
cd "$(dirname "$0")/../.tools"
name=node-v8.16.2-linux-x64
curl -fLsS https://nodejs.org/dist/v8.16.2/SHASUMS256.txt -o node8-SHASUMS256.txt
curl -fLsS "https://nodejs.org/dist/v8.16.2/$name.tar.xz" -o "$name.tar.xz"
grep " $name.tar.xz$" node8-SHASUMS256.txt | sha256sum -c -
tar -xf "$name.tar.xz"
