# Remaining work and hardware validation

This is an implemented reliability fork and tested cluster development integration, not the fully completed production rebuild described in the brief.

- Target binaries and Store install artifacts are now built and ABI-checked. No local SDK is needed. Real firmware/emulator validation remains outstanding.
- The full extraction/download regression remains skipped in the offline suite; a separate live public-content metadata extraction smoke test passed using the hash-verified shipped extractor, with compatible H.264 and AAC formats found. New YouTube access failures have not been reproduced on the target vehicle; no claim that all videos now play.
- Version 0.5.0 enables optional map-only cluster video with explicit Park/zero-speed checks and native lease expiry. Target firmware signal freshness, navigation priority, Waze coexistence and crash/power-loss restoration still need hardware testing. No legal or safety certification claimed.
- Current audio handover is preserved. BMW MediaPlayer pause/seek/clock accuracy and sustained A/V drift require the actual 2022 530's firmware. No continuous audio API is invented.
- Resource guards cap accepted video at 256MiB and audio at 128MiB; long content can stop with an explicit quota error. Disk use includes intermediate audio copies and indexes. This is not a rolling cache with arbitrary seeking. A configurable cache quota and buffer-range model remain outstanding.
- Full twelve-state lifecycle replacement, independent yt-dlp in-car updater, complete favourites/playlists feature set, adaptive bandwidth quality selection, comprehensive settings and total native UI redesign remain outstanding. Existing signed-in shelves and continue watching are preserved.
- Broad startup compatibility, GPU recovery and sustained leak/bandwidth benchmarks remain hardware work. The generic MediaPlayer source is shared; cross-app concurrent audio arbitration cannot be guaranteed.
- Simulator adapter uses the official client; only the simulator native main translation unit is compiled here, not a fully linked hardware-accelerated simulator player executable.
- Tests that skip or fail are recorded in reports; static/source checks do not substitute for hardware validation.
