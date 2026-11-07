#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build/host
cr=upstream/idrive-apps/native/cluster-render
g++ -std=c++14 -O2 -Wall -Wextra -Werror -Inative/frame-router -Inative/renderers -I"$cr/include" \
    tests/router_test.cpp "$cr/client/client.cpp" "$cr/client/protocol.cpp" -o build/host/router_test
build/host/router_test
g++ -std=c++14 -O2 -Wall -Wextra -Werror -Inative/frame-router -Inative/renderers -I"$cr/include" \
    tests/cluster_socket_test.cpp "$cr/client/client.cpp" "$cr/client/protocol.cpp" -o build/host/cluster_socket_test
build/host/cluster_socket_test
g++ -std=c++14 -O2 -Wall -Wextra -Werror -Isource/native/ytdec/src tests/native_limits_test.cpp \
    source/native/ytdec/src/index.cpp source/native/ytdec/src/nal_reader.cpp -o build/host/native_limits_test
build/host/native_limits_test
g++ -std=c++14 -O2 -Wall -Wextra -Werror -DRTE_CLUSTER_SIMULATOR \
    -Inative/frame-router -Inative/renderers -I"$cr/include" -Isource/native/ytdec/abi/include \
    -c source/native/ytdec/src/main.cpp -o build/host/simulator-main.o
