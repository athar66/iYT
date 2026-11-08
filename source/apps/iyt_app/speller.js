'use strict';
/**
 * The HMI's own full-screen free-text speller, opened as the Store app opens it: the use case
 * 02076b22-d19b-4aef-9e8c-0d7305d8b88c through the SDK's use case factory (needs the
 * usecasemanagement proxies, which build.py gives every app).
 *
 *   spell(ctx.app, 'Search videos').then((text) => ...)   // text, or null when left without OK
 *
 * Interaction parameters: 4 the title (22 characters show), 102 the text so far (each keystroke),
 * 105 present once the driver pressed OK. Written for this kit (the Store's speller.js is GPL).
 */
const USE_CASE = '02076b22-d19b-4aef-9e8c-0d7305d8b88c';
const P_TITLE = 4, P_INPUT = 102, P_OK = 105;
const FINAL = ['ABORTED', 'FAILED', 'COMPLETED'];
const pending = new WeakMap();
const cancellations = new WeakMap();

function spell(app, title, opts) {
    if (!app || typeof app.getUseCaseFactory !== 'function') return Promise.reject(new Error('BMW keyboard is unavailable'));
    if (pending.has(app)) return pending.get(app);
    const request = new Promise((resolve, reject) => {
        let inst = null, sub = null, text = '', done = false, started = false, idleTimer = null;
        const setupTimer = setTimeout(() => finish(new Error('Keyboard setup timed out')), (opts && opts.setupMs) || 10000);
        const unsubscribe = () => Promise.resolve().then(() => (inst && sub !== null ? inst.proxy.notify.unsubscribe(sub) : null)).catch(() => {});
        const finish = (err, v) => {
            if (done) return;
            done = true;
            clearTimeout(setupTimer);
            clearTimeout(idleTimer);
            unsubscribe();
            if (err) reject(err); else resolve(v);
        };
        cancellations.set(app, () => finish(null, null));
        const resetIdle = () => { clearTimeout(idleTimer); idleTimer = setTimeout(() => finish(null, null), 180000); };
        Promise.resolve().then(() => app.getUseCaseFactory())
            .then((f) => done ? null : f.create(USE_CASE))
            .then((i) => { if (done) return null; inst = i; return inst.proxy.init(); })
            .then(() => done ? null : inst.proxy.waitUntilAvailable())
            .then(() => done ? null : inst.proxy.notify.subscribe((n) => {
                if (!started || done) return;
                resetIdle();
                const p = n && n.interactionParameters;     // Map-like, not always this realm's Map
                const has = (k) => !!p && typeof p.has === 'function' && p.has(k);
                if (has(P_INPUT)) text = String(p.get(P_INPUT));
                if (has(P_OK) && p.get(P_OK) !== false && p.get(P_OK) !== 0 && p.get(P_OK) !== null) finish(null, text);
                else if (n && FINAL.indexOf(n.interactionState) >= 0) finish(null, null);
            }))
            .then((id) => {
                sub = id === undefined ? null : id;
                if (done) { unsubscribe(); return null; }
                return Promise.resolve(inst.proxy.interactionState.getValue()).then((st) => {
                    if (st !== 'READY') throw new Error('speller is ' + st + ', not READY');
                    if (done) return null;
                    started = true;
                    return inst.proxy.start({ token: inst.token, startParameters: new Map([[P_TITLE, String(title).slice(0, 22)]]) });
                }).then(() => { clearTimeout(setupTimer); if (!done) resetIdle(); });
            })
            .catch((e) => finish(e));
    });
    const result = request.then((v) => { pending.delete(app); cancellations.delete(app); return v; }, (e) => { pending.delete(app); cancellations.delete(app); throw e; });
    pending.set(app, result);
    return result;
}

function cancel(app) { if (app && cancellations.has(app)) cancellations.get(app)(); }
module.exports = { spell, cancel };
