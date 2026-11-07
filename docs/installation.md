# MGU Store installation

Add athar66/iYT in Store → Sources, choose main, refresh, then select iYT → Install. The Store discovers the app and service through root mgu-repo.json and builds the app locally using its stock BMW donor SDK. You do not download, extract or supply a BMW SDK yourself.

If jap-node22 is missing from available dependencies, add JustAnotherPU/mgu-apps as a Releases source. Leave the standard Store/default application sources enabled for mgu-deploy, mgu-python, mgu-render and mgu-inputgate.

The main branch path is ready once the repository files are pushed. A separate Releases channel requires the catalog release assets to be published; the prepared assets are in dist/release.

Names: iyt_app (app), iyt-daemon (service), /var/opt/iyt-daemon (data), /run/iyt-daemon/ctl.sock (control) and /dev/shm/mgu-video-iyt (video). The bundled iyt-lock enforces one daemon instance; it requires no firmware-provided flock command.

Original RideTube is preserved. Stop its playback before using iYT because BMW exposes the same generic media audio source. Uninstall iYT and iYT playback service only through the Store. Shared dependencies stay if other apps need them.

This release has host tests and target ABI validation, but no actual car installation result. Keep the car parked with stable power during the owner's eventual Store installation. Real cluster video is not enabled.
