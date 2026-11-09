// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
#include "cluster_render/client.h"
#include "router.h"
#include <memory>
#include <sys/socket.h>

namespace rte {
class ClusterAdapter {
public:
    explicit ClusterAdapter(const std::string &socket, bool simulator) {
        if (socket.empty() || (simulator ? socket == cr::kDefaultSocket : socket != cr::kDefaultSocket))
            throw std::invalid_argument("invalid cluster endpoint for build mode");
        client_.reset(new cr::Client("iyt-map-video", socket));
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
        permitted_ = allowed;
        if (!allowed) release(); // drop BEFORE reconnect can restore a stale layer
        client_->poll(now);
        if (!client_->connected()) shown_ = false;
        if (allowed && !ref_ && client_->connected()) {
            if (!ready()) {
                status = "E_RENDERER_CAPABILITY: map:1088x480 on id7 required";
                return;
            }
            cr::LayerOptions lo;
            lo.target = "map";
            lo.contend = true; // Park-gated map request; renderer only takes over the stock map.
            lo.exclusive = false;
            lo.guide_hold = false;
            lo.z = -100;
            cr::VideoOptions vo;
            vo.fps = 8;
            vo.stall_ms = 1000;
            ref_ = client_->video(lo, vo);
            status = "waiting for map ownership";
        }
    }
    bool submit(const uint8_t *p, unsigned w, unsigned h, uint64_t id) {
        // The renderer needs a first frame before its layer can become "shown".
        // Visibility is diagnostic state, not permission to bootstrap the stream.
        if (!permitted_ || !ref_ || !client_->connected()) return false;
        if (client_->frame_waiting(ref_)) { ++dropped; return false; }
        atlas(p, w, h, 1088, 480, atlas_);
        if (!client_->frame(ref_, &atlas_, id)) return false;
        submittedBytes += 1088 * 480 * 3 / 2;
        return true;
    }
    void release() {
        if (ref_) {
            client_->drop(ref_);
            // EOF also removes our layers if a partially sent frame delays DROP.
            if (client_->fd() >= 0) shutdown(client_->fd(), SHUT_RDWR);
        }
        ref_ = 0; shown_ = false; permitted_ = false;
    }
    bool shown() const { return shown_ && ref_ && client_->connected(); }
    bool ready() const { return client_->connected() && client_->backend == "id7" && ("," + client_->targets + ",").find(",map:1088x480,") != std::string::npos; }
    ~ClusterAdapter() { release(); }
    uint64_t dropped = 0, submittedBytes = 0;
    std::string status = "not connected";
private:
    std::unique_ptr<cr::Client> client_;
    uint32_t ref_ = 0;
    bool shown_ = false, permitted_ = false;
    std::vector<uint8_t> atlas_;
};
}
