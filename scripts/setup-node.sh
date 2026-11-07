#!/bin/sh
set -eu
mkdir -p "$(dirname "$0")/../.tools"
cd "$(dirname "$0")/../.tools"
version=v22.23.0
name=node-$version-linux-x64
curl -fLsS https://nodejs.org/dist/$version/SHASUMS256.txt -o SHASUMS256.txt
curl -fLsS https://nodejs.org/dist/$version/$name.tar.xz -o $name.tar.xz
grep " $name.tar.xz$" SHASUMS256.txt | sha256sum -c -
tar -xf $name.tar.xz
