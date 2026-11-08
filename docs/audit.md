# Source audit and issue matrix

Audited revisions are pinned in `upstream-lock.json`; `source/` contains the modified GPL source. An upstream report describes a service startup failure on a 2020 M340i. Its cause remains unconfirmed without logs from that firmware.

Reviewed components: native app/kit lifecycle, parked signal adapter, control socket model; Node daemon search, device sign-in, stream lookup, fetch UID, cache pruning, progressive audio and MediaPlayer methods; Python MP4/Annex-B conversion and range transfer; native NAL parser, index, frame pacing, VAAPI/MSDK surfaces, MGVF publication; service/check/build/release manifests. Cluster review includes C++ client/protocol, Waze decoder reuse, named map targets, frame atlas and non-contending ownership. Store review includes tool manifests, deploy artifact entry point, OAP packing and catalog schema. This is source-level review, not exhaustive firmware validation.

| Finding | Evidence | Classification and disposition |
|---|---|---|
| Range responses accepted on status 206 alone | `ytfetch.ranged_get` | Confirmed integrity gap; exact Content-Range, encoding and length checked; short writes handled; HTTP regression passes |
| Index count drives allocation without file-size bound | `Index::refresh` | Confirmed allocation risk; bounded to present records, 4096 per batch, 2M total; malformed-count test |
| Unbounded NAL assembly / large access units | `NalReader`, `Player::feed_one` | Confirmed resource risk; explicit 16 MiB caps and isolated decoder failure |
| MP4 box sizes used directly in reads | `read_box` | Confirmed resource risk; 32 MiB cap, truncated extended header and NAL checks |
| Audio fallback accepts incompatible codecs | AUDIO_FMT falls through to unrestricted `ba` | Confirmed capability gap; restrict to AAC-LC m4a; no software transcoding introduced |
| Video fallback permits >30 fps | video_fmt final branch | Confirmed policy gap; all branches H.264 MP4 HTTPS ≤30fps and resolution cap |
| Full download despite progressive start | Existing fetch pipeline | Architectural tradeoff; preserved progressive prefix, added 128 MiB audio / 256 MiB video limits. Rolling cache and unrestricted long-video seeking NOT implemented |
| Generic audio connections swept at service startup | sourceID 1046, `dropLeftovers` | Confirmed coexistence hazard; no source-wide sweep; busy source refused. Simultaneous original/fork audio and race-free cross-app arbitration not validated |
| Service launches system node despite Node22 dependency | original service ExecStart | Compatibility risk; pinned dependency path used, restart burst capped, flock single-instance guard. Check /usr/bin/flock on target |
| Test helper hard-codes Homebrew ffprobe | test/mgyi.py | Confirmed Linux test failure; PATH/env discovery fixes enhanced suite; baseline failure retained |
| Initial baseline daemon failures on Windows checkout | CRLF executable test shebangs | Environment issue; fresh LF baseline checkout in .tools used for comparison |
| Audio head-to-full handover | MediaPlayer replay path | Hardware-reported limitation preserved; no undocumented continuous-audio API invented |
| Native decoder pools, B-frames, A/V clock | Existing decoder/player tests | Already implemented upstream; kept. No hardware performance improvement claimed |
| MGVF triple-slot publication | Existing release/acquire atomics | Kept; isolated fork pathname. No unverified change to renderer wire ABI |
| map 0x100 assumption | current cluster protocol and backend | Client must use target `map`; id7 1088×480 capability checked. Numeric target not exposed as an app API |
| Vehicle gear signal / layer restoration | no validated target-vehicle evidence | 0.5.0 explicit gear/speed guard and map-only route implemented; target firmware validation pending |

Licences: RideTube GPL-3.0-or-later, kit MIT, upstream decoder attribution GPL; cluster client/protocol MPL-2.0; Store GPL-3.0; bundled fonts Ubuntu Font Licence / OFL; jpeg-js BSD-3-Clause; yt-dlp Unlicense; SponsorBlock data CC BY-NC-SA 4.0. Preserve upstream LICENSE and THIRD_PARTY_LICENSES. Source releases include modified GPL source and build scripts. Do not distribute BMW SDK files. Packaging tools and external toolchains retain their own notices.
