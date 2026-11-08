# Playback fails after buffering

Version 0.4.2 addresses an audio-file access gap and adds diagnostics to distinguish it from video decoding failures.

Downloaded media remains in a private directory owned by the download account. Passing that path directly to BMW MediaPlayer assumes the player can traverse that directory. That assumption is not valid for a player running under another unprivileged account. A Linux cross-account test reproduces access denial for the old path.

Completed audio is now published through a separate, randomly named audio-only directory. It uses hard links on the same filesystem, so no audio is downloaded or copied twice. The download cache stays private. A bounded ownership manifest supports cleanup after stopping or restarting, and cleanup checks inode identity before removing a file.

This fixes a confirmed permission gap. The actual MediaPlayer account and the cause of the reported vehicle error have not been established from firmware logs, so it is not a claim that every playback failure is resolved.

After updating both iYT and its playback service to 0.4.2, retry playback. If it fails, open the app's Diagnostics page and choose Refresh. Record:

- Video and audio formats, resolution and frame rate.
- BMW MediaPlayer's rejection, if present.
- Native video-decoder error, if present.

An `E_AUDIO_MEDIA` error identifies the BMW media/audio path. `E_VIDEO_DECODE` identifies the native video path. A white frame alone does not prove successful video decoding.

The format policy still selects H.264 video and AAC-LC audio. No software multi-codec decoder is added by this release. Additional hardware format paths require validated decoder capabilities and an appropriate demuxing path; they do not resolve audio-file access failures.
