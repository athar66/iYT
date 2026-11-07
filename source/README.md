# iYT source

iYT application and playback-service source. See the [project README](../README.md), [build instructions](../docs/build.md) and [attribution](../licenses/NOTICE.md).

The app is source/apps/iyt_app; its playback service is source/native/iyt-daemon. Native target binaries and the verified official extractor are committed under the service's prebuilt directory for MGU Store repo-tree installation. SDK-free packages are built without a local BMW SDK; the Store uses a stock donor on the head unit.

Original upstream history and unmodified reference sources are pinned in ../upstream-lock.json and can be restored with scripts/fetch-upstream.py. Original licences remain in LICENSE and THIRD_PARTY_LICENSES.
