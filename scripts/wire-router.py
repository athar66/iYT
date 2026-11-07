from pathlib import Path
r = Path(__file__).resolve().parents[1] / 'source/native/ytdec'
p = r / 'src/player.h'
t = p.read_text().replace('    /* counters, for stats and tests */', '''    // Synchronous presentation observer. No decoding duplication or retained frame pointer.
    using Present = std::function<void(const uint8_t *, size_t, int64_t, int64_t)>;
    Present present;

    /* counters, for stats and tests */''')
p.write_text(t)
p = r / 'src/player.cpp'
t = p.read_text().replace('    memcpy(out_->begin(), s.i420.data(), s.i420.size());\n    out_->commit();', '''    if (present) present(s.i420.data(), s.i420.size(), s.pts, now);
    else {
        memcpy(out_->begin(), s.i420.data(), s.i420.size());
        out_->commit();
    }''')
p.write_text(t)
p = r / 'src/main.cpp'
t = p.read_text().replace('#include "player.h"', '#include "player.h"\n#ifdef RTE_CLUSTER_SIMULATOR\n#include "cluster_adapter.h"\n#endif')
t = t.replace('    bool fill = false;', '''    bool fill = false;
#ifdef RTE_CLUSTER_SIMULATOR
    std::string simulator_socket;
#endif''')
t = t.replace('        else if (a == "--log"', '''#ifdef RTE_CLUSTER_SIMULATOR
        else if (a == "--cluster-simulator-socket" && i + 1 < argc)
            simulator_socket = argv[++i];
#endif
        else if (a == "--log"''')
t = t.replace('    cpu_pct();\n    fcntl', '''#ifdef RTE_CLUSTER_SIMULATOR
    rte::Safety safety(true);
    rte::Router router;
    std::unique_ptr<rte::ClusterAdapter> cluster;
    if (!simulator_socket.empty()) cluster.reset(new rte::ClusterAdapter(simulator_socket, true));
    router.main = [&](const uint8_t *p, size_t n, int64_t) {
        memcpy(out.begin(), p, n); out.commit();
    };
    router.cluster = [&](const uint8_t *p, size_t, int64_t pts) {
        if (cluster) cluster->submit(p, w, h, (uint64_t)pts);
    };
    player.present = [&](const uint8_t *p, size_t n, int64_t pts, int64_t now) {
        router.route(p, n, pts, now, safety.allowed(now));
    };
#endif
    cpu_pct();
    fcntl''')
t = t.replace('        const int wait = player.step(mono_ms());', '''#ifdef RTE_CLUSTER_SIMULATOR
        if (cluster) cluster->poll(mono_ms(), router.mode != rte::Mode::Main && safety.allowed(mono_ms()));
#endif
        const int wait = player.step(mono_ms());''')
t = t.replace('            quit = !player.command(line, mono_ms());', '''#ifdef RTE_CLUSTER_SIMULATOR
            if (line == "output main" || line == "output cluster" || line == "output dual") {
                router.mode = line == "output main" ? rte::Mode::Main : line == "output cluster" ? rte::Mode::Cluster : rte::Mode::Dual;
                if (cluster && router.mode == rte::Mode::Main) cluster->release();
                continue;
            }
            if (line == "vehicle lost") { safety.lost(); if (cluster) cluster->release(); continue; }
            int park; double speed;
            if (sscanf(line.c_str(), "vehicle %d %lf", &park, &speed) == 2) {
                safety.update({park == 1, speed, mono_ms()});
                if (cluster && !safety.allowed(mono_ms())) cluster->release();
                continue;
            }
#endif
            quit = !player.command(line, mono_ms());''')
p.write_text(t)
print('Native frame presentation wired; cluster compilation remains simulator-only.')
