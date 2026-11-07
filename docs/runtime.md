# Runtime and sign-in fixes in 0.4.1

The service uses the head unit's platform Node runtime for the BMW SOME/IP addon and control bridge. It does not install or run a separate Node22 daemon. The native UI also remains on BMW's platform runtime. This is not a completely Node-free implementation.

The additional `jap-node22` dependency is removed. A bundled QuickJS 2026-06-04 interpreter handles yt-dlp's supported JavaScript challenges only when extraction requests it. The target interpreter is 1,018,064 bytes, built against glibc2.27. Its complete MIT source archive, pinned source digest and licence are included. Binary size is not a vehicle RAM or CPU benchmark.

The default idle Python extraction worker is disabled. Fetching and thumbnail jobs run on demand; native H.264 decoding remains in ytdec. These changes remove the additional runtime requirement and idle worker, rather than claiming measured on-car performance gains.

The 0.4.0 DNS lookup adapter returned a single address even when Node22 requested all addresses for automatic address-family selection. Node then interpreted the result incorrectly, producing `Invalid IP address: undefined`. The shared DNS adapter now handles scalar/list and IPv4/IPv6 contracts, validates addresses and reports empty answers explicitly. Both authentication HTTP requests and thumbnails use it.

Regression tests cover the DNS contracts and a real local HTTP connection. The YouTube TV sign-in page returns HTTP200 using uplink DNS under Node8.16.2 and Node22 in host testing. Device-code/account tests use controlled fixtures; successful sign-in on the actual vehicle still requires verification. Public-content metadata extraction passes using the shipped QuickJS target interpreter.
