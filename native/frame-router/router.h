// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include <algorithm>
#include <cstdint>
#include <functional>
#include <stdexcept>
#include <string>
#include <vector>

namespace rte {
enum class Mode { Main, Cluster, Dual };
struct VehicleState { bool park = false; double speed = -1; int64_t at = -1; };
class Safety {
public:
    // No vehicle provider is required in simulation. Production remains disabled
    // until independent input provenance and OEM layer restoration are validated.
    explicit Safety(bool simulator = false) : simulator_(simulator) {}
    bool allowed(int64_t now) const {
        return simulator_ && (!has_state_ || (state_.park && state_.speed == 0 &&
            state_.at <= now && now - state_.at <= 2000));
    }
    void update(VehicleState state) { state_ = state; has_state_ = true; }
    void lost() { has_state_ = true; state_ = VehicleState{}; }
private:
    bool simulator_, has_state_ = false;
    VehicleState state_;
};
class Router {
public:
    using Sink = std::function<void(const uint8_t *, size_t, int64_t)>;
    Mode mode = Mode::Main;
    Sink main, cluster;
    unsigned fps = 8;
    uint64_t sent = 0, throttled = 0;
    void route(const uint8_t *data, size_t n, int64_t pts, int64_t now, bool permitted) {
        if (mode != Mode::Cluster && main) main(data, n, pts);
        if (mode == Mode::Main || !cluster || !permitted) return;
        if (fps != 8 && fps != 10 && fps != 12) throw std::invalid_argument("cluster fps must be 8, 10 or 12");
        if (last_ >= 0 && now - last_ < (1000 + fps - 1) / fps) { ++throttled; return; }
        last_ = now;
        cluster(data, n, pts);
        ++sent;
    }
private:
    int64_t last_ = -1;
};

// Planar I420 -> renderer atlas: Y then rows with U and V side by side.
// Nearest-neighbour scaling with letterboxing, once per submitted cluster frame.
inline void atlas(const uint8_t *src, unsigned sw, unsigned sh, unsigned dw,
                  unsigned dh, std::vector<uint8_t> &out) {
    if (!src || sw < 2 || sh < 2 || dw < 4 || dh < 2 || sw % 2 || sh % 2 || dw % 4 || dh % 2)
        throw std::invalid_argument("invalid YUV420 dimensions");
    out.assign(size_t(dw) * dh * 3 / 2, 128);
    std::fill(out.begin(), out.begin() + size_t(dw) * dh, 16);
    unsigned w = dw, h = unsigned(uint64_t(sh) * dw / sw) & ~1u;
    if (h > dh) { h = dh; w = unsigned(uint64_t(sw) * dh / sh) & ~1u; }
    if (w < 2 || h < 2) throw std::invalid_argument("aspect ratio too extreme");
    const unsigned x = ((dw - w) / 2) & ~1u, y = ((dh - h) / 2) & ~1u;
    for (unsigned r = 0; r < h; ++r)
        for (unsigned c = 0; c < w; ++c)
            out[size_t(y+r)*dw+x+c] = src[size_t(uint64_t(r)*sh/h)*sw+uint64_t(c)*sw/w];
    for (unsigned plane = 0; plane < 2; ++plane) {
        const uint8_t *p = src + size_t(sw)*sh + plane*size_t(sw)*sh/4;
        for (unsigned r = 0; r < h/2; ++r)
            for (unsigned c = 0; c < w/2; ++c)
                out[size_t(dw)*dh+size_t(y/2+r)*dw+plane*dw/2+x/2+c] =
                    p[size_t(uint64_t(r)*(sh/2)/(h/2))*(sw/2)+uint64_t(c)*(sw/2)/(w/2)];
    }
}
}
