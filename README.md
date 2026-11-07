# iYT

Native YouTube app for BMW MGU iDrive 7, derived from RideTube. Includes native audio, Intel hardware H.264 video, signed-in feeds, search, continue watching, quality controls and diagnostics.

## Install from MGU Store

Add **athar66/iYT** as a source and select the **main branch**. The repository's `mgu-repo.json` lists **iYT** and **iYT playback service**. Install iYT; the Store installs its declared dependencies first. If the Store offers Releases, that channel uses the `catalog` release and requires its assets to have been published; main works directly from this repository.

The required Node22 runtime is published by **JustAnotherPU/mgu-apps**. Add that repository's Releases source if it is not already available. Standard Store sources supply mgu-deploy, mgu-python and mgu-render; mgu-inputgate comes from cauliflowermossgrape/idrive7-apps.

**You do not need a BMW SDK on your PC.** The Store generates `oap-sdk` from a stock BMW app already on the head unit. No BMW SDK or firmware is included here.

## Included deployment files

- Root `mgu-repo.json`: Store discovery and on-head-unit app build.
- `source/apps/iyt_app`: native app, settings and icon.
- `source/native/iyt-daemon`: service manifest and committed target binaries under prebuilt/.
- `dist/release`: SDK-free app package, native service package, checksummed catalog and icon, ready for a GitHub release tagged `catalog`.

App id `iyt_app`; service id `iyt-daemon`; separate data/cache/control/frame namespaces preserve original RideTube. Avoid simultaneous audio playback in both apps: BMW's generic media source is shared.

## Verification and limits

Target decoder and lock wrapper built with GCC7.5/glibc2.27 in the exact pinned Ubuntu18 image userland. Loader/library ABI and all 18 media imports passed checks. The actual Store reader discovers both components, packages the service, and prepares the real SDK-free app using a synthetic donor in host tests. Native app frames and controller flows run against the upstream head-unit stub.

**Store-ready does not mean verified on your car.** No installation or vehicle test has been performed. Firmware-specific startup, audio clock, GPU behaviour and sustained playback still need validation. See [release validation](reports/release-validation.json), [test results](reports/checks.json) and [remaining work](docs/known-limitations.md).

Real cluster video remains disabled; cluster modes are development/simulator-only. Vehicle-state input is optional in the simulator. Main-screen hardware playback retains parked-only behaviour.

GPL-3.0-or-later, derived from JustAnotherPU/RideTube with original notices preserved. See [licences](licenses/NOTICE.md), source/LICENSE and source/THIRD_PARTY_LICENSES.
