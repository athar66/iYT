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
