# Native interaction ownership

| Capability | Owner | Contract | Verification |
|---|---|---|---|
| Search/list navigation | apps/iyt_app/main.js + yt.js | Native speller; preserve focus and explicit paging | Upstream client/model tests |
| Settings/select | app.json and kit native settings | HMI owns choices and focus; no safety override | Manifest inspection; hardware pending |
| Feedback | daemon state/error JSON and native canvas | Actionable message, bounded retry; retain original wire states | Daemon offline integration tests |
| Forms | Native HMI speller | No browser form | Hardware pending |
| Scrolling | Existing canvas/controller owner | No web scrollbar surface | Host runtime checks, rotary hardware pending |
| Output modes | Native frame router | Simulator main/cluster/dual; production main only | router_test.cpp |

Absent vehicle-state input is allowed in simulation. If a simulator provider is supplied, stale/negative/nonzero speed or missing Park closes the cluster output. Real cluster rendering remains disabled. Settings never expose an interlock bypass.
