# Rollback and uninstall

The original app and all vehicle files remain untouched by local development.

For a future authorised installation, stop playback in iYT, use MGU Store to uninstall iyt_app and iyt-daemon only, or select the Store's retained previous version. Never remove shared dependencies while other apps use them. Sign out before uninstalling; revoke the YouTube TV grant in your Google account if needed.

Do not uninstall the Store or run a global cleanup. Do not remove OEM binaries, unrelated sockets or someone else's shared-memory objects. Resume the original RideTube only after Enhanced has released its own audio connection. Store-compatible target packages are prepared; no vehicle has been modified, so no vehicle shell rollback is needed for local development.

For local extractor staging rollback, copy the explicitly retained yt-dlp.previous.zipapp back to yt-dlp.zipapp in the staging directory, revalidate its recorded digest, rebuild and retest; staging is not an on-car updater.
