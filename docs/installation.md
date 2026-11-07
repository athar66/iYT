# MGU Store installation

For private repositories, give the Store's GitHub connection access to athar66/iYT. If using its GitHub App sign-in, allow the repository in that app's GitHub installation; alternatively use a repository-scoped token with the read access documented by MGU Store.

Add athar66/iYT in Store → Sources, choose Releases, refresh, then select iYT → Install. The published catalog release contains the SDK-free app, native service, icon and checked artifact metadata. The Store supplies the SDK from its stock BMW donor. You do not download, extract or supply a BMW SDK yourself.

If jap-node22 is missing from available dependencies, add JustAnotherPU/mgu-apps as a Releases source. Leave the standard Store/default application sources enabled for mgu-deploy, mgu-python, mgu-render and mgu-inputgate.

Both routes are published: Releases reads the catalog release; main reads mgu-repo.json and builds the app on the head unit. Private release artifact URLs use the authenticated GitHub asset API.

Names: iyt_app (app), iyt-daemon (service), /var/opt/iyt-daemon (data), /run/iyt-daemon/ctl.sock (control) and /dev/shm/mgu-video-iyt (video). The bundled iyt-lock enforces one daemon instance; it requires no firmware-provided flock command.

Stop other media applications before using iYT because BMW exposes a shared generic media audio source. Uninstall iYT and iYT playback service only through the Store. Shared dependencies stay if other apps need them.

This release has host tests and target ABI validation, but no real-vehicle installation result. Keep the car parked with stable power during installation. Real cluster video is not enabled.
