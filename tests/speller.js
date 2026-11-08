'use strict';
const assert = require('assert');
const {spell, cancel} = require('../source/apps/iyt_app/speller');
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
function fixture() {
    let cb;
    const f = {starts: 0, unsubscribed: 0};
    f.emit = (state, pairs) => cb({interactionState: state, interactionParameters: new Map(pairs || [])});
    f.proxy = {init: () => Promise.resolve(), waitUntilAvailable: () => Promise.resolve(),
        notify: {subscribe: (fn) => { cb = fn; f.emit('COMPLETED', [[105, true]]); return Promise.resolve(7); },
            unsubscribe: () => { f.unsubscribed++; return Promise.resolve(); }},
        interactionState: {getValue: () => Promise.resolve('READY')},
        start: () => {f.starts++; return Promise.resolve();}};
    f.app = {getUseCaseFactory: () => Promise.resolve({create: () => Promise.resolve({proxy: f.proxy, token: 'test'})})};
    return f;
}
async function run() {
    const f = fixture(), p = spell(f.app, 'Search');
    assert.strictEqual(spell(f.app, 'Search'), p);
    await sleep(5);
    assert.strictEqual(f.starts, 1);
    let done = false; p.then(() => {done = true;});
    f.emit('AWAITING_RESPONSE', [[105, false]]);
    await sleep(1); assert.strictEqual(done, false);
    f.emit('COMPLETED', [[102, 'bmw video'], [105, true]]);
    assert.strictEqual(await p, 'bmw video');
    await sleep(1); assert.strictEqual(f.unsubscribed, 1);
    const next = spell(f.app, 'Search'); await sleep(2); cancel(f.app);
    assert.strictEqual(await next, null);
    const g = fixture(); g.proxy.waitUntilAvailable = () => new Promise(() => {});
    let timedOut = false;
    try { await spell(g.app, 'Search', {setupMs: 15}); } catch (e) { timedOut = /timed out/.test(e.message); }
    assert(timedOut);
    const h = fixture(); h.proxy.notify.unsubscribe = () => new Promise(() => {});
    const hungCleanup = spell(h.app, 'Search'); await sleep(2); h.emit('ABORTED');
    assert.strictEqual(await hungCleanup, null);
    console.log('speller: duplicate opens, initial completion, confirmation, cancellation, setup timeout and cleanup passed');
}
run().catch((e) => {console.error(e); process.exitCode = 1;});
