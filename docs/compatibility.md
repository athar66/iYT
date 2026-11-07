# Compatibility

Target: BMW MGU ID7 x86_64. Original upstream reports one tested G05 firmware, P18_23w44.2-1-3. This fork has no real-car results, including for the requested 2022 530 xDrive. RideTube's open startup issue on a 2020 M340i remains unresolved without firmware logs.

UI retains Node8 syntax/runtime conventions; daemon explicitly uses required jap-node22. Native target requires original MSDK/VAAPI libraries and compatible glibc/libstdc++ imports; host test binaries are test-only; prebuilt/ytdec and prebuilt/iyt-lock are target ABI-checked. Firmware-derived SDKs and binaries are not distributed here.

Cluster client API uses protocol version1 and named `map`; adapter currently requires backend id7 and advertised map:1088x480. It never requests panel/hud or contends for stock navigation. Numeric 0x100 is not treated as a portable application API. Actual transport/ownership/restore behaviour must be validated on each firmware.
