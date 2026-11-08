'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const d = require('../source/native/iyt-daemon/diagnostics');
test('errors retain distinct actionable categories', () => {
    assert.equal(d.errorCode('HTTP 403 expired'), 'E_URL_EXPIRED');
    assert.equal(d.errorCode('no avc1 video'), 'E_FORMAT_UNSUPPORTED');
    assert.equal(d.errorCode('confirm your age'), 'E_ACCESS_RESTRICTED');
    assert.equal(d.errorCode('MFX surface allocation'), 'E_DECODER');
    assert.equal(d.errorCode('BMW MediaPlayer rejected audio: video not playable'), 'E_AUDIO_MEDIA');
});
test('diagnostics never infer working acceleration from device access', () => {
    const r = d.report({state: 'idle'});
    assert.equal(r.hardwareAcceleration, 'unverified');
    assert.equal(r.audioPosition_ms, null);
    assert.equal(r.cluster.available, false);
    assert(r.memory.rss > 0);
});
