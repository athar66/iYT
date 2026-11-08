# Native interaction ownership

| Capability | Owner | Contract | Verification |
|---|---|---|---|
| Search/list navigation | apps/iyt_app/main.js + yt.js | Native speller; preserve focus and explicit paging | Upstream client/model tests |
| Select/Listbox | app.json and kit native settings | HMI owns choices and focus; no safety override | Manifest inspection; hardware pending |
| Feedback | daemon state/error JSON and native canvas | Actionable message, bounded retry; retain original wire states | Daemon offline integration tests |
| Forms | Native HMI speller | No browser form | Hardware pending |
| Keyboard handoff | speller.js and Display.suspend | Stop media, hide the overlay and release controller capture before opening BMW's keyboard; no duplicate use cases; cancel/timeout restores controls | tests/speller.js; test_ridetube.js |
| Exit and visibility | app visibility plus Ctl connection | Closing or Exit stops audio/video and disconnects; internal menus and keyboard handoff are not app exit; reopening stays idle | test_ridetube.js |
| Scrolling | Existing canvas/controller owner | No web scrollbar surface | Host runtime checks, rotary hardware pending |
| App actions | Native canvas toolbar plus HMI buttons | Search, Settings and Exit have visible matching touch targets; no sidebar Search target | test_ridetube.js; touch-layout.js |
| Output modes | Native frame router and native HMI setting | Production main or dual, map target only; explicit fresh Park and zero speed required | router_test.cpp; cluster-vehicle.js; cluster-control.js; cluster_socket_test.cpp |

Absent vehicle-state input is allowed only in simulation. Production offers the optional “Cluster map video (Park only)” native setting, off by default. Explicit Park and exact zero speed must remain fresh. Provider loss clears state; conflicting or invalid values block output. The decoder lease expires in at most 750 ms without renewed authorization, bounded by the source sample expiry. Hiding playback, turning the setting off, stopping playback or disconnecting the app releases the map layer. The layer is non-exclusive, below other content, does not contend for the OEM slot and leaves the guidance box enabled. Settings never expose an interlock bypass. Actual firmware behavior remains a hardware test.
