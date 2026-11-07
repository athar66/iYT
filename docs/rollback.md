# Rollback and uninstall

Remove or roll back iYT through MGU Store.

Stop playback in iYT, use MGU Store to uninstall iyt_app and iyt-daemon only, or select the Store's retained previous version. Keep shared dependencies while other apps use them. Sign out before uninstalling; revoke the YouTube TV grant in your Google account if needed.

Leave the Store, OEM binaries and unrelated applications installed. Stop iYT before resuming another application that uses the same audio source.

For local extractor staging rollback, copy the explicitly retained yt-dlp.previous.zipapp back to yt-dlp.zipapp in the staging directory, revalidate its recorded digest, rebuild and retest; staging is not an on-car updater.
