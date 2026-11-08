// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "cluster_render/client.h"
#include "router.h"
#include <memory>

namespace rte {
// Development-only adapter. Hard refuses the production renderer endpoint.
class ClusterAdapter {
public:
    explicit ClusterAdapter(const std::string &socket, bool simulator) {
        if (!simulator || socket == cr::kDefaultSocket || socket.empty())
            throw std::invalid_argument("E_CLUSTER_UNVALIDATED: use a simulator socket");
        client_.reset(new cr::Client("rte-ridetube-simulator", socket));
        client_->on_layer = [this](uint32_t ref, const std::string &state, const std::string &why) {
            if (ref != ref_) return;
            shown_ = state == "shown";
            status = state + ": " + why;
        };
        client_->on_error = [this](const std::string &, uint32_t, const std::string &why) {
            shown_ = false; status = why;
        };
    }
    void poll(int64_t now, bool allowed) {
        if (!allowed) release(); // drop BEFORE reconnect can restore a stale layer
        client_->poll(now);
        if (!client_->connected()) shown_ = false;
        if (allowed && !ref_ && client_->connected()) {
            if (client_->backend != "id7" || client_->targets.find("map:1088x480") == std::string::npos) {
                status = "E_RENDERER_CAPABILITY: map:1088x480 on id7 required";
                return;
            }
            cr::LayerOptions lo;
            lo.target = "map";
            lo.contend = false;
            lo.exclusive = false;
            lo.guide_hold = false;
            cr::VideoOptions vo;
            vo.fps = 8;
            ref_ = client_->video(lo, vo);
            status = "waiting for map ownership";
        }
    }
    bool submit(const uint8_t *p, unsigned w, unsigned h, uint64_t id) {
        if (!ref_ || !shown_ || !client_->connected()) return false;
        if (client_->frame_waiting(ref_)) { ++dropped; return false; }
        atlas(p, w, h, 1088, 480, atlas_);
        if (!client_->frame(ref_, &atlas_, id)) return false;
        submittedBytes += 1088 * 480 * 3 / 2;
        return true;
    }
    void release() { if (ref_) client_->drop(ref_); ref_ = 0; shown_ = false; }
    ~ClusterAdapter() { release(); }
    uint64_t dropped = 0, submittedBytes = 0;
    std::string status = "not connected";
private:
    std::unique_ptr<cr::Client> client_;
    uint32_t ref_ = 0;
    bool shown_ = false;
    std::vector<uint8_t> atlas_;
};
}
