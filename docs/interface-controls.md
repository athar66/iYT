# iYT controls in 0.5.3

**Search**, **Settings** and **Exit** are labelled buttons on the main screens.
Playback has only a persistent **Back** button; transport controls appear on
interaction and fade. Back stops playback and returns to the list. The painted
button bounds are also the touch bounds.
Persistent actions take priority over the invisible full-player wake target.
Native HMI buttons provide the same actions when the renderer is unavailable.
The top navigation Menu opens recent searches, account actions and Diagnostics.

Settings opens its own BMW-native screen. Use the normal Back control to return.
Exit stops playback, releases the main and cluster video outputs, closes the
playback-service connection and closes the app's screens. Leaving through the
vehicle's normal app/Home controls also stops playback. Reopening reconnects
without automatically resuming the old video.

Search stops current playback before opening BMW's keyboard. The renderer and
controller capture remain suspended throughout keyboard entry, including from
a fresh start with no active video. Keyboard visibility is an intentional
handoff, not an app-exit event. A temporary keyboard activity hold keeps the
parent app available without keeping media playing in the background. Setup is
bounded to ten seconds; an idle keyboard session is released after three minutes.
Cancelling returns to the app, and duplicate Search presses share one request.

Controller input normally comes through the renderer. An optional subscription
to BMW FrontCCU can supply missing events while iYT's own canvas is active.
Named BMW button/deflection enums are normalized; recent renderer input takes
precedence and duplicate states are suppressed. Fallback input is ignored while
the app is hidden or the native keyboard/menu is active. Diagnostics displays
the input source that has actually supplied an event. Physical operation and
touch placement still require verification on the unit's firmware.
