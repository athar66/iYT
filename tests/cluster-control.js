'use strict';
const assert = require('assert');
const { Daemon } = require('../source/native/iyt-daemon/ytd');
const lines = [], errors = [];
const d = { toYtdec: (s) => lines.push(s), emit: (e) => errors.push(e) };
const realNow = Date.now;
const realHrtime = process.hrtime;
Date.now = () => 10000;
process.hrtime = () => [20, 0];
try {
    Daemon.prototype.setDisplayMode.call(d, 'dual');
    assert.strictEqual(lines.pop(), 'output dual');
    Daemon.prototype.updateClusterVehicle.call(d, { park: true, speed: 0, expiresAt: 11000 });
    assert.strictEqual(lines.pop(), 'vehicle 1 0 20750');
    Daemon.prototype.updateClusterVehicle.call(d, { park: true, speed: 0, expiresAt: 10100 });
    assert.strictEqual(lines.pop(), 'vehicle 1 0 20100');
    for (const m of [{park:false,speed:0,expiresAt:11000}, {park:true,speed:1,expiresAt:11000},
        {park:true,speed:0,expiresAt:10000}, {park:true,speed:0,expiresAt:13000},
        {park:true,speed:0,expiresAt:'11000'}, {park:true,speed:0,expiresAt:Infinity}]) {
        Daemon.prototype.updateClusterVehicle.call(d, m);
        assert.strictEqual(lines.pop(), 'vehicle lost');
    }
    Daemon.prototype.setDisplayMode.call(d, 'main');
    assert.strictEqual(lines.pop(), 'vehicle lost');
    Daemon.prototype.setDisplayMode.call(d, 'panel');
    assert.strictEqual(errors.pop().code, 'E_DISPLAY_MODE');
} finally { Date.now = realNow; process.hrtime = realHrtime; }
console.log('cluster control: modes, bounded lease, stale/future/replayed data and invalid state passed');
