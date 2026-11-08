# iYT native interface

Audience: BMW iDrive 7 users navigating with the rotary controller.
Purpose: find content and control playback with stable native focus and minimal visual noise.

The existing canvas, native HMI speller, bundled Ubuntu/Noto font atlases, 1600×520 layout and controller focus paths remain canonical. No browser framework or external fonts.

Canonical runtime tokens: `source/apps/iyt_app/theme.js` → main.js canvas primitives. Graphite background #10151b, card #1b232d, placeholder #293441, text #f2f5f8, secondary #adb9c7, selection accent #479be8, supporting accent #9bcdf8, warning #f3c16a. The legacy `red` key means selection accent, retained to avoid changing canvas call sites.

Typography: existing bold atlas for titles/selection; label atlas for supporting metadata; existing numeric glyphs for playback time. Thumbnail geometry and 56-image pool stay bounded. Focus uses existing outlined tiles and selection rail, without adding animations. This pass changes palette and branding; a complete redesign is not claimed.

UK English is the development locale. Existing localisation remains upstream-owned. Visual rendering and physical controller checks need the SDK/emulator and car; host runtime tests cannot establish visual acceptance.

Persistent Search, Settings and Exit actions use the existing graphite canvas tokens and native fonts. The visible rounded button bounds also define their touch targets and take priority over the player's invisible wake region. The sidebar Menu retains secondary account and diagnostic actions. Settings uses a separate native HMI screen.
