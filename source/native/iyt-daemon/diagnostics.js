// Modified 2026-11-07 for iYT; see licenses/NOTICE.md and docs/audit.md.
'use strict';
// SPDX-License-Identifier: GPL-3.0-or-later
const fs = require('fs');
const CODES = [
    [/BMW MediaPlayer rejected audio|E_AUDIO_EXPORT/i, 'E_AUDIO_MEDIA'],
    [/age|private|members|login|sign.in|restricted/i, 'E_ACCESS_RESTRICTED'],
    [/no avc1|format.*available|unsupported.*codec/i, 'E_FORMAT_UNSUPPORTED'],
    [/403|expired/i, 'E_URL_EXPIRED'],
    [/ENOSPC|disk|space/i, 'E_DISK_SPACE'],
    [/permission|EACCES/i, 'E_PERMISSION'],
    [/decoder|MFX|surface/i, 'E_DECODER'],
    [/timed? ?out|timeout/i, 'E_TIMEOUT'],
    [/network|ECONN|HTTP|socket|ENOTFOUND/i, 'E_NETWORK']
];
function errorCode(message) {
    const match = CODES.find(x => x[0].test(String(message)));
    return match ? match[1] : 'E_PLAYBACK';
}
function report(daemon) {
    let gpu;
    try { fs.accessSync('/dev/dri/renderD128', fs.constants.R_OK | fs.constants.W_OK); gpu = 'accessible'; }
    catch (e) { gpu = e.code === 'ENOENT' ? 'unavailable' : 'permission-denied'; }
    return {
        ev: 'diagnostics', version: '0.5.3', node: process.version,
        uptime_s: process.uptime(), memory: process.memoryUsage(),
        gpuDevice: gpu, hardwareAcceleration: 'unverified',
        decoderRunning: !!daemon.child, state: daemon.state,
        decoderStats: daemon.child ? daemon.decoderStats || null : null,
        mediaFormats: daemon.mediaFormats || null,
        bufferedVideo_ms: daemon.fetchedMs === undefined ? null : daemon.fetchedMs,
        audioPosition_ms: daemon.elapsed === undefined ? null : daemon.elapsed,
        lastError: daemon.lastError || null,
        lastMediaPlayerError: daemon.lastMediaPlayerError || null,
        lastDecoderError: daemon.lastDecoderError || null,
        cluster: { available: !!(daemon.child && daemon.clusterState && daemon.clusterState.connected && Date.now() - daemon.clusterState.receivedAt < 3000), target: 'map', mode: daemon.displayMode || 'main',
            shown: !!(daemon.child && daemon.clusterState && daemon.clusterState.shown && Date.now() - daemon.clusterState.receivedAt < 3000),
            state: daemon.child ? daemon.clusterState || null : null }
    };
}
module.exports = { errorCode, report };
