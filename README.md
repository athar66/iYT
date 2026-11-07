# iYT

A native YouTube player for BMW iDrive 7.

iYT combines an iDrive interface with BMW's native audio playback and Intel hardware-accelerated H.264 video decoding.

## Features

- Search YouTube and browse signed-in feeds.
- Continue watching and access subscriptions and Watch later.
- Control playback, seek and select video quality using the iDrive controller.
- View playback and service diagnostics.
- Play audio through the vehicle's media system.
- Show video on the main display while parked.

## Requirements

- BMW MGU head unit running iDrive 7 (ID7).
- MGU Store and a working internet connection through `mgu-uplink`.
- The standard Store sources and `cauliflowermossgrape/idrive7-apps`.
- `JustAnotherPU/mgu-apps` as a Releases source for the Node.js 22 runtime.

Required service and runtime dependencies are declared in the package manifests and installed by the Store when available.

## Installation

1. Open **MGU Store → Sources**.
2. Add **athar66/iYT** and select **Releases**.
3. Refresh the source, select **iYT**, then choose **Install**.

For a private repository, grant the Store's GitHub connection access before adding the source. The **main** branch also supports installation from source.

No separate BMW SDK download is required. The Store supplies `oap-sdk` from a stock BMW application already installed on the head unit.

## Compatibility

iYT targets x86-64 MGU head units running ID7. Native binaries are checked against the target loader and library interfaces. Automated checks cover playback control, native UI flows, media handling and Store packaging.

Real-vehicle installation and sustained playback have not yet been validated. Firmware compatibility may vary. Stop other media playback before starting iYT to avoid conflicts with BMW's shared generic media source.

Instrument-cluster video is not enabled in the vehicle release. Cluster output is available only for development and simulation.

## Development

See [build instructions](docs/build.md), [compatibility](docs/compatibility.md), [known limitations](docs/known-limitations.md) and [test results](reports/RESULTS.md).

## Uninstall

Stop playback, sign out if needed, then remove **iYT** and **iYT playback service** through MGU Store. Keep shared dependencies that other applications use.

## Licence

GPL-3.0-or-later. See [LICENSE](source/LICENSE), [attribution and notices](licenses/NOTICE.md) and [third-party licences](source/THIRD_PARTY_LICENSES).
