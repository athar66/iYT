# iYT native interface

Audience: BMW iDrive 7 users navigating with the rotary controller.
Purpose: find content and control playback with stable native focus and minimal visual noise.

The existing canvas, native HMI speller, bundled Ubuntu/Noto font atlases, 1600×520 logical layout and controller focus paths remain canonical. No browser framework or external fonts. The user selected the original Slate logo with Horizon's large-list organization.

Canonical runtime tokens: `source/apps/iyt_app/theme.js` → main.js canvas primitives. Graphite background #10151b, card #1b232d, placeholder #293441, text #f2f5f8, secondary #adb9c7, selection accent #479be8, supporting accent #9bcdf8, warning #f3c16a. The legacy `red` key means selection accent, retained to avoid changing canvas call sites.

Typography: bold titles at 30 logical pixels, label metadata at 22, and existing numeric glyphs for playback time. Browsing uses approximately three wide rows with left thumbnails, short metadata and a clear blue focus outline. Vertical virtualization draws only visible rows; neighbouring controller targets scroll into view but cannot receive touches outside the viewport. The existing 56-image pool remains bounded.

UK English is the development locale. Existing localisation remains upstream-owned. Visual rendering and physical controller checks need the SDK/emulator and car; host runtime tests cannot establish visual acceptance.

Home has a compact navigation row and labelled Search, Settings and Exit actions. Playback has only a persistent Back button; transport controls appear on interaction and fade. Back stops playback and returns to the list. Settings uses a separate native HMI screen. The original blue logo geometry in brand.js generates icon.svg and icon.png through scripts/build-brand.js and draws the in-app mark; no legacy logo is reused.
