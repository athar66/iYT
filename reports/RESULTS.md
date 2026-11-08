# Verification results — 7 November 2026

Enhanced: 13 check groups passed, including 65 daemon integration cases, native parser/player tests, HTTP integrity/partial-write regressions, extractor staging validation, diagnostics, frame routing and local Unix socket cluster protocol integration. Media suite ran 14 tests: 13 passed and 1 live YouTube test skipped (verified extractor build absent). Router/safety tests use simulated state and do not establish vehicle safety.

Baseline: 8 of 9 groups passed. Media group fails because the original reference helper hard-codes `/opt/homebrew/bin/ffprobe`; the enhanced helper discovers FFprobe through PATH. The original results remain unchanged in baseline-media.log.

The first Windows/CRLF baseline attempt and intermediate development failures were investigated; the reproducible comparison uses a fresh LF checkout and Linux Node22. An asynchronous zoom test was corrected to wait for the seek log independently of process-argument logging. No production timeout was increased to make that test pass.

Final selective reruns are stored as final-*.log. checks.json records their exact exit codes. Native simulator main.cpp was compiled with warnings as errors; cluster adapter was linked and exercised against a local protocol server. Hardware decoder, BMW audio, visual UI and vehicle firmware validation were not run.

Five synthetic native host runs per variant are in benchmark.json. These small process-level workloads do not demonstrate a reliable real-world performance gain. Target binaries and SDK-free Store packages were subsequently built; see release-validation.json and docs/known-limitations.md.

## iYT Store packaging validation

The renamed iYT app was built SDK-free. All enhanced groups passed again with the app now built, including native UI frame/controller tests that had previously been skipped. The legacy motion-override assertions were replaced with tests proving that the removed override cannot enable moving video.

Actual MGU Store repoCatalog/packComponent discovers both iYT components and packages the service without out-of-folder licence references. Its linker prepares the actual app package using the upstream synthetic donor; no generated SDK is published. Store linker/packer upstream suite: 74 checks passed (real donors absent). Target decoder built with GCC7.5/glibc2.27 and passed loader/symbol ceilings plus all 18 media imports. Bundled target lock passed duplicate/crash-release/symlink tests.

A live metadata-only smoke test of the public Blender Foundation Big Buck Bunny video passed with the shipped, hash-verified yt-dlp zipapp: compatible H.264 up to 720p30 and AAC-LC were available. No media downloaded. This does not establish on-car playback performance.

See release-validation.json, store-discovery.json, store-sdk-link.json and extraction-smoke.json. No vehicle installation was performed.

## Version 0.4.1

- Reproduced the previous scalar DNS callback failure as ERR_INVALID_IP_ADDRESS: Invalid IP address: undefined under Node22. Shared lookup now supports the requested result shape and validates DNS answers.
- TV-page HTTP requests through uplink DNS pass under Node8.16.2 and Node22. Account/device-code flow tests pass against controlled fixtures; actual vehicle sign-in remains unverified.
- All 14 enhanced groups and all four Node8 platform-compatibility groups pass. The full online media-download regression remains skipped; live public-content metadata extraction passes using the bundled QuickJS target interpreter.
- Service uses the platform Node8 bridge, with no jap-node22 dependency. Native QuickJS is bundled and invoked on demand. The default idle Python worker is disabled. This is not a completely Node-free implementation and no vehicle CPU/RAM improvement is claimed.
- QuickJS source archive, pinned digest and MIT licence are included. Target loader/library checks pass for the interpreter.

## Version 0.4.2

Completed audio is handed to BMW MediaPlayer through a dedicated audio-only path instead of the private download directory. Hard links avoid a second media copy; journaled ownership supports cleanup and protects unrelated files. A root-run Linux test proves that another account cannot read the original private path but can read the published audio. This confirms a permission gap, not the exact MediaPlayer identity or failure cause on the reported firmware.

Platform-runtime playback/account/thumbnail checks and the enhanced suites pass. Audio/container synthetic media tests pass; full online media-download and actual vehicle playback validation remain outstanding. Diagnostics now separate BMW audio/media rejection from native decoder errors and display selected format metadata without signed URLs.

H.264 hardware decoding is unchanged; no software multi-format decoder has been introduced. Refresh Diagnostics after a failure to identify whether the remaining issue is audio access/parsing or native video decoding.

## Version 0.5.0

Production target builds now include the official cluster-render client and map-area route. The native HMI offers an optional Park-only map video setting, off by default. Explicit selector state and exact zero speed are validated for invalid values, conflicting sources, provider loss and two-second sample freshness. Heartbeats preserve source expiry; the native decoder requires a monotonic lease of at most 750 ms. Invalid state, hidden playback or missing heartbeats release the low-priority non-exclusive map layer and close only this client's renderer connection. No panel or HUD output is exposed.

All 18 enhanced check groups and four platform Node8 bridge groups passed. Additional production-safety socket checks prove that missing state prevents a layer and expired state triggers its release. Target ELF and imported MSDK/VAAPI ABI checks pass. Store discovery, SDK-free packaging, synthetic donor linking and every artifact digest pass. Native-setting static audit passes. The real BMW HMI setting, signal freshness, physical video output, warning/navigation behavior and crash/power-loss restoration remain hardware tests; no vehicle deployment was performed here. The complete online media-download regression retains its existing skip.

## Version 0.5.1

Search, Settings and Exit have persistent labelled buttons. Search is removed from the sidebar; Menu retains account and diagnostics access. Settings has a separate native screen. Search suspends the app renderer and controller capture before opening BMW's keyboard, even with no video playing. Duplicate requests share one use case; initial completion notifications are ignored, setup is bounded, cancellation is supported and hung unsubscribe cannot block the result.

Closing or Exit stops media and disconnects the playback service. A cached app can reopen without resuming playback. Host app-flow checks cover keyboard handoff with active and idle playback, confirmation, cancellation, close/reopen and Exit. Unit checks cover named BMW controller enums, fallback arbitration, duplicate suppression and touch bounds including overlap with the invisible player wake target. The direct controller signal is optional and limited to the active app canvas. Actual firmware keyboard, physical rotary behavior and touch alignment still need a vehicle test. The native decoder binary is unchanged from 0.5.0.

All 21 enhanced check groups and four platform bridge groups pass, along with the final Node8 app flow including visibility-only closure. Store packaging, donor linking, target ABI, artifact hashes and the strict static interface audit pass. These are host checks, not visual or physical acceptance on the vehicle.
