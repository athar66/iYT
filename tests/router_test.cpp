// SPDX-License-Identifier: GPL-3.0-or-later
#include "router.h"
#include "cluster_adapter.h"
#include <cassert>
#include <iostream>
int main() {
    rte::Safety real;
    real.update({true, 0, 100});
    assert(!real.allowed(100));
    rte::Safety sim(true);
    assert(sim.allowed(100)); // optional provider in development
    sim.update({true, 0, 100}); assert(sim.allowed(100));
    assert(!sim.allowed(2101));
    sim.update({false, 0, 100}); assert(!sim.allowed(100));
    sim.update({true, 1, 100}); assert(!sim.allowed(100));
    sim.lost(); assert(!sim.allowed(100));
    int main = 0, cluster = 0;
    rte::Router r;
    r.mode = rte::Mode::Dual;
    r.main = [&](const uint8_t *, size_t, int64_t) { ++main; };
    r.cluster = [&](const uint8_t *, size_t, int64_t) { ++cluster; };
    uint8_t p[24] = {0};
    for (int t=0; t<1000; ++t) r.route(p, sizeof p, t, t, true);
    assert(main == 1000 && cluster == 8);
    for (unsigned fps : {8u, 10u, 12u}) {
        rte::Router profile;
        profile.mode = rte::Mode::Cluster;
        profile.fps = fps;
        profile.cluster = [](const uint8_t *, size_t, int64_t) {};
        for (int t=0; t<1000; ++t) profile.route(p, sizeof p, t, t, true);
        assert(profile.sent == fps);
    }
    r.route(p, sizeof p, 1000, 1000, false); assert(cluster == 8);
    r.mode = rte::Mode::Cluster;
    r.route(p, sizeof p, 2000, 2000, true); assert(main == 1001 && cluster == 9);
    std::fill(p, p+16, 32); std::fill(p+16, p+20, 64); std::fill(p+20, p+24, 192);
    std::vector<uint8_t> out;
    rte::atlas(p, 4, 4, 4, 4, out);
    assert(out.size() == 24 && out[16] == 64 && out[18] == 192 && out[20] == 64);
    rte::atlas(p, 4, 4, 8, 4, out);
    assert(out[0] == 16 && out[2] == 32); // letterboxing
    bool rejected = false;
    try { rte::ClusterAdapter adapter(cr::kDefaultSocket, true); }
    catch (const std::invalid_argument &) { rejected = true; }
    assert(rejected);
    std::cout << "router: modes, fps, atlas, optional state, fail-closed hardware passed\n";
}
