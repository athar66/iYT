// SPDX-License-Identifier: GPL-3.0-or-later
// Verified upstream protocol on a local Unix socket; no BMW hardware involved.
#include "cluster_adapter.h"
#include <cassert>
#include <cstring>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <iostream>
int main() {
    std::string path = "/tmp/rte-cr-" + std::to_string(getpid()) + ".sock";
    int server = socket(AF_UNIX, SOCK_STREAM | SOCK_NONBLOCK, 0);
    assert(server >= 0);
    sockaddr_un address{};
    address.sun_family = AF_UNIX;
    std::strcpy(address.sun_path, path.c_str());
    assert(bind(server, (sockaddr *)&address, sizeof address) == 0);
    assert(listen(server, 1) == 0);
    rte::ClusterAdapter adapter(path, true);
    rte::Safety vehicle;
    int peer = -1;
    std::string input;
    bool layer = false, frame = false, dropped = false;
    auto event = [&](const std::string &json) {
        std::string msg = cr::encode(cr::kJson, json);
        assert(send(peer, msg.data(), msg.size(), MSG_NOSIGNAL) == (ssize_t)msg.size());
    };
    auto pump = [&](int64_t now, bool permitted) {
        adapter.poll(now, permitted && vehicle.allowed(now));
        if (peer < 0) peer = accept4(server, nullptr, nullptr, SOCK_NONBLOCK);
        if (peer < 0) return;
        char bytes[65536];
        ssize_t n;
        while ((n = recv(peer, bytes, sizeof bytes, 0)) > 0) input.append(bytes, (size_t)n);
        for (;;) {
            size_t consumed, len; uint8_t type; const char *body; bool bad = false;
            if (!cr::next_message(input.data(), input.size(), &consumed, &type, &body, &len, &bad)) { assert(!bad); break; }
            if (type == cr::kJson) {
                cr::Json json; assert(cr::parse_json(std::string(body, len), &json));
                if (json["op"] == "hello") event("{\"ev\":\"hello\",\"proto\":1,\"backend\":\"id7\",\"targets\":\"map:1088x480\",\"repeat\":1}");
                if (json["op"] == "layer") {
                    assert(json["target"] == "map" && json["contend"] == "0" && json["exclusive"] == "0");
                    assert(json["z"] == "-100" && json["guide_hold"] == "0");
                    layer = true;
                    event("{\"ev\":\"layer\",\"ref\":" + json["ref"] + ",\"state\":\"shown\"}");
                }
                if (json["op"] == "drop") dropped = true;
            } else if (type == cr::kFrame) {
                cr::FrameHeader header;
                assert(cr::parse_frame(body, len, &header));
                frame = true;
            }
            input.erase(0, consumed);
        }
    };
    for (int i=0; i<10; ++i) pump(i, true);
    assert(!layer);
    vehicle.update({true, 0, 10});
    for (int i=10; i<100 && !layer; ++i) pump(i, true);
    assert(layer);
    for (int i=100; i<110; ++i) pump(i, true);
    std::vector<uint8_t> pixels(64*36*3/2, 128);
    assert(adapter.submit(pixels.data(), 64, 36, 1));
    for (int i=110; i<1000 && !frame; ++i) pump(i, true);
    assert(frame && adapter.submittedBytes == 1088*480*3/2);
    for (int i=1000; i<1100 && !dropped; ++i) pump(i, true); // expires without an app update
    assert(dropped);
    assert(!adapter.submit(pixels.data(), 64, 36, 2));
    close(peer); close(server); unlink(path.c_str());
    std::cout << "cluster socket: hello, map layer, atlas frame and safety release passed (simulated)\n";
}
