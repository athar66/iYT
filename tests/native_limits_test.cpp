// SPDX-License-Identifier: GPL-3.0-or-later
#include "index.h"
#include "nal_reader.h"
#include <cassert>
#include <cstdio>
#include <cstdint>
#include <fcntl.h>
#include <unistd.h>
#include <stdexcept>
#include <vector>
int main() {
    char path[] = "/tmp/rte-index-XXXXXX";
    int fd = mkstemp(path);
    assert(fd >= 0);
    uint8_t h[32] = {'M', 'G', 'Y', 'I', 1};
    h[16] = h[17] = h[18] = h[19] = 255;
    assert(write(fd, h, sizeof h) == sizeof h);
    close(fd);
    ytdec::Index index;
    std::string error;
    assert(index.open(path, &error));
    assert(index.recs.empty()); // malicious count never determines allocation
    unlink(path);
    woc::NalReader nal;
    std::vector<uint8_t> oversized((16u << 20) + 1);
    bool caught = false;
    try { nal.push(oversized.data(), oversized.size(), true, [](const woc::AccessUnit &) {}); }
    catch (const std::runtime_error &) { caught = true; }
    assert(caught);
    unsigned count = 0;
    uint8_t valid[] = {0,0,1,0x65,0x88};
    nal.push(valid, sizeof valid, true, [&](const woc::AccessUnit &) { ++count; });
    assert(count == 1); // parser reusable after a limit error
    puts("native allocation limits: passed");
}
