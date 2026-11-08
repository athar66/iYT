# Cluster map video: 0.5.0 hardware test

Update **both iYT and iYT playback service to 0.5.0** from MGU Store.
The Store dependency is `cluster-render` 0.4.2 or newer. Leave the standard
Store sources enabled so it can resolve this dependency.

1. With the vehicle stationary in Park, open iYT Settings and turn on
   **Cluster map video (Park only)**. The setting starts off by default.
2. Select the cluster's map view using the normal vehicle controls, then play
   a short video in iYT and keep its player visible on the main screen.
3. If the map video does not appear, open **Diagnostics → Refresh**.
   Record the complete status, video/audio format and decoder rows. The status
   includes the selected output, whether map video is shown, and the vehicle guard reason.
4. While stationary, switch the setting off, hide the player and stop playback
   separately. Each action should release the map video. Confirm normal map
   behavior returns. Keep the feature off if it does not.

The output is the 1088×480 `map` target at at most 8 fps, letterboxed from the
existing hardware decoder. No panel, HUD or full-cluster target is requested.
Navigation/other content is above this non-exclusive layer; the app does not
retry a slot taken by the stock HMI and does not suppress the guidance box.
It may therefore wait behind stock content rather than force itself visible.

Only explicit Park and zero speed qualify. Neutral, the ambiguous `NP` value,
invalid/conflicting signals, provider loss or samples older than two seconds
block output. The decoder also requires renewed short leases; app/bridge stalls
cannot renew them. Leases carry a fixed Linux monotonic deadline, so time spent
waiting in the decoder's input queue cannot make an old update fresh again.
The renderer receives its minimum one-second frame-stall timeout, and the
client drops its layer and closes its own connection on release. Firmware
crash/power-loss restoration and sustained playback still need real-unit testing.

The gear fields are polled where the installed BMW schema supports getters.
If your firmware exposes only notifications and stops refreshing them in Park,
Diagnostics will report stale gear and cluster video will remain blocked.
That result needs the unit's interface definition/logs; it is not a decoder failure.

This release preserves the 0.4.2 audio handoff. It does not establish that the
previous “video not playable” error is resolved on the vehicle. Previous 0.4.2
packages remain in the GitHub catalog release for rollback.
