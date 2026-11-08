# Implementation boundaries

`source/apps/iyt_app`: original BMW-native Node 8-compatible canvas, speller and controller model, revised graphite theme, diagnostic menu. No web runtime added.

`source/native/iyt-daemon`: platform-Node8 bridge handles account/feed/search, cancellation generations, bounded child restart, BMW SOME/IP calls and audio clock. It uses the runtime already supplied by iDrive for native addon compatibility. The Python fetcher progressively demuxes H.264 and prepares playable audio prefixes; bundled QuickJS handles extraction challenges on demand. No Node22 dependency or default idle Python worker is retained. Existing legacy state protocol remains; a complete twelve-state replacement is outstanding.

`source/native/ytdec`: one Intel MSDK/VAAPI decoder, timestamp-based presentation, reused frame surfaces, bounded queue and triple-slot MGVF writer. Added parser/index allocation limits and synchronous presentation routing hook. Production uses existing main-screen path.

`native/frame-router` and `native/renderers`: main/cluster/dual routing, 8/10/12fps throttle, planar I420 atlas conversion and letterboxing. Cluster adapter links the pinned upstream C++ library, owns only a `map` content layer, sets contend=false/exclusive=false/guide_hold=false, checks id7/map geometry and drops under socket backpressure. Native main.cpp integrates it only with `RTE_CLUSTER_SIMULATOR`; this macro is absent from the production build. Simulator control commands: `output main|cluster|dual`, `vehicle <park:0|1> <speed>`, `vehicle lost`. No state provider is required for development. Once supplied, the provider must report fresh stationary Park; lost/stale data releases the layer.

Socket/protocol lifecycle is tested locally against protocol-framed hello/layer/frame/drop events. No simulator result proves BMW warning priority, safe restore, actual gear parsing, Waze coexistence, CAN/SOME/IP safety or regulatory compliance.
