# Compatibility

Target: BMW MGU ID7 x86_64. iYT has no real-vehicle validation results. Firmware-specific startup behaviour remains unverified; upstream compatibility reports do not establish compatibility for this release.

UI and service bridge retain the platform Node8 runtime for compatibility with BMW's native addon. QuickJS is bundled for on-demand extraction; Node22 is not a deployment dependency. Native playback requires the original MSDK/VAAPI libraries. The prebuilt decoder, lock wrapper and QuickJS interpreter are target-ABI-checked. Firmware-derived SDKs and binaries are not distributed here.

Cluster client API uses protocol version1 and named `map`; adapter currently requires backend id7 and advertised map:1088x480. It never requests panel/hud or contends for stock navigation. Numeric 0x100 is not treated as a portable application API. Actual transport/ownership/restore behaviour must be validated on each firmware.
