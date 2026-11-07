# iYT playback service

The service connects the native iDrive interface to BMW MediaPlayer audio, the hardware H.264 decoder and the media fetcher.

## Runtime

- BMW's platform Node8 runtime hosts the SOME/IP addon and control bridge.
- `mgu-python` runs yt-dlp and progressive media handling on demand.
- Bundled QuickJS handles extraction JavaScript challenges on demand.
- Native `ytdec` decodes H.264 through Intel Media SDK/VAAPI.

No separate Node22 package or `jap-node22` source is required. The service is not completely Node-free: its BMW audio bridge uses the runtime already supplied by iDrive. The default idle Python extraction worker is disabled.

## Installation and diagnostics

Install and update through MGU Store. The component manifest declares dependencies, payloads and service ownership. Data is stored under `/var/opt/iyt-daemon`; the application communicates through `/run/iyt-daemon/ctl.sock`.

Version 0.4.1 fixes the DNS callback contract that caused `Invalid IP address: undefined` during sign-in. Authentication and thumbnails share the validated DNS adapter. See [runtime details](../../../docs/runtime.md).

The package check verifies the bundled lock, extractor, QuickJS interpreter and platform JavaScript modules without starting playback. Vehicle-specific audio, graphics and account behaviour still require validation.

## Source and licences

See the repository's [build instructions](../../../docs/build.md), [notices](../../../licenses/NOTICE.md), `LICENSE`, `THIRD_PARTY_LICENSES` and `QuickJS-MIT.txt`. Complete QuickJS source and its pinned digest are under `native/quickjs` at the repository root.
