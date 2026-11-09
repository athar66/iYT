# Implementation boundaries

`source/apps/iyt_app`: original BMW-native Node 8-compatible canvas, speller and controller model, revised graphite theme, diagnostic menu. No web runtime added.

`source/native/iyt-daemon`: platform-Node8 bridge handles account/feed/search, cancellation generations, bounded child restart, BMW SOME/IP calls and audio clock. It uses the runtime already supplied by iDrive for native addon compatibility. The Python fetcher progressively demuxes H.264 and prepares playable audio prefixes; bundled QuickJS handles extraction challenges on demand. No Node22 dependency or default idle Python worker is retained. Existing legacy state protocol remains; a complete twelve-state replacement is outstanding.

`source/native/ytdec`: one Intel MSDK/VAAPI decoder, timestamp-based presentation, reused frame surfaces, bounded queue and triple-slot MGVF writer. Added parser/index allocation limits and synchronous presentation routing hook. Production retains the main-screen path and can additionally submit the same decoded frame to the cluster map renderer.

`source/native/ytdec/src/cluster` owns the frame router, map adapter and pinned MPL-2.0 client from idrive-apps commit 05e38eca8ca6f3bcde7e43d67127da664401caa8. Root native headers include this canonical implementation. Production builds define `RTE_CLUSTER_OUTPUT`; development builds may use `RTE_CLUSTER_SIMULATOR`. Only the default production renderer socket is accepted outside simulation. The native HMI setting selects main or dual output; no full-cluster target is exposed.

The explicit VehicleInformation selector fields and Vehicle2 speed feed `cluster-vehicle.js`. Invalid/conflicting data, provider loss and two-second staleness block the map output. Each app heartbeat carries the original source expiry, so the daemon cannot extend old data. The decoder requires a valid lease of at most 750 ms and releases the non-exclusive low-priority map layer when it expires, playback is hidden, video is off, or the app exits. The renderer frame-stall timeout is its minimum one second. The map layer uses Park-gated contend=true and guide_hold=false. Native leases use a monotonic clock; the app-to-service absolute expiry is validated before conversion.

Socket/protocol lifecycle is tested locally against protocol-framed hello/layer/frame/drop events. No simulator result proves BMW warning priority, safe restore, actual gear parsing, Waze coexistence, CAN/SOME/IP safety or regulatory compliance.
