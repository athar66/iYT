// Modified 2026-11-07 for iYT; see licenses/NOTICE.md and docs/audit.md.
'use strict';

// RideTube (apps/iyt_app): the control-socket client and the playback state against a fake iyt-daemon daemon on a
// temporary Unix socket; then, when dist/iyt_app is built, one results and one player frame through the stubbed
// head unit into a renderer stream (pictures as message 10, the video as 13 + op 19), the feed tabs, the sign-in
// page and signing out; where the kit runs the screen: the rail and the bar, Home's shelves (arrows, the controller
// bringing any tile into view, thumbs asked for the drawn tiles only, the picture pool). No SDK or car needed:
//   node kit/tools/test_ridetube.js

const assert = require('assert');
const fs = require('fs');
const net = require('net');
const os = require('os');
const path = require('path');
const { Ctl, Model, clock } = require('../../apps/iyt_app/yt');

const quiet = { info() {}, warn() {}, error(m, e) { throw e || new Error(m); } };
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function until(fn, ms, what) {
    const end = Date.now() + (ms || 3000);
    while (!fn()) { if (Date.now() > end) throw new Error('timed out: ' + what); await sleep(10); }
}

// the daemon got obj as its last command (the socket delivers a moment later)
async function lastIs(d, obj, msg) {
    try { await until(() => JSON.stringify(d.got.filter((m) => m.cmd === obj.cmd).slice(-1)[0]) === JSON.stringify(obj), 2000, msg); } catch (e) {
        assert.deepStrictEqual(d.got.filter((m) => m.cmd === obj.cmd).slice(-1)[0], obj, msg);
    }
}

function fakeDaemon(sock) {
    const d = { got: [], conn: null, conns: 0 };
    d.server = net.createServer((c) => {
        d.conn = c; d.conns++;
        let buf = '';
        c.setEncoding('utf8');
        c.on('data', (x) => {
            buf += x;
            let i;
            while ((i = buf.indexOf('\n')) >= 0) { d.got.push(JSON.parse(buf.slice(0, i))); buf = buf.slice(i + 1); }
        });
        c.on('error', () => {});
    });
    d.send = (o) => d.conn.write(JSON.stringify(o) + '\n');
    d.cmds = (cmd) => d.got.filter((m) => m.cmd === cmd);
    return new Promise((r) => d.server.listen(sock, () => r(d)));
}

async function clientAndModel() {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-'));
    const sock = path.join(dir, 'ctl.sock');
    const d = await fakeDaemon(sock);
    const ctl = new Ctl(sock, quiet);
    const m = new Model((o) => ctl.send(o));
    ctl.on('up', () => m.setConnected(true)).on('down', () => m.setConnected(false)).on('msg', (x) => m.onMsg(x));
    ctl.connect();
    await until(() => d.cmds('status').length, 2000, 'status on connect');
    assert.ok(m.connected, 'connected');
    await until(() => d.cmds('auth_status').length, 2000, 'auth_status on connect');
    assert.deepStrictEqual(d.got.slice(0, 2), [{ cmd: 'status' }, { cmd: 'auth_status' }], 'on connect: status, then the account (no library: nothing is kept on the car)');

    // first results: no thumb asked on its own (the screens ask for the tiles they draw: wantThumb), each asked once
    assert.ok(m.search('first'));
    d.send({ ev: 'results', q: 'first', items: [{ id: 'lib1', title: 'First' }, { bad: 1 }] });
    await until(() => m.results.length === 1, 2000, 'first results (the bad item dropped)');
    await sleep(50);
    assert.strictEqual(d.cmds('thumb').length, 0, 'no thumb asked before a screen draws one');
    assert.ok(m.wantThumb('lib1') && !m.wantThumb('lib1') && !m.wantThumb('nope'), 'asked once; an unknown id never');
    await lastIs(d, { cmd: 'thumb', id: 'lib1' });
    d.send({ ev: 'thumb', id: 'lib1', w: 160, h: 90, rgba: Buffer.alloc(57600, 9).toString('base64') });
    await until(() => m.thumbs.lib1, 2000, 'thumb stored');
    assert.deepStrictEqual([m.thumbs.lib1.w, m.thumbs.lib1.h, m.thumbs.lib1.buf.length, m.pending.size], [160, 90, 57600, 0], '160x90 kept, no longer pending');
    assert.ok(!m.wantThumb('lib1'), 'held: not asked again');
    d.got.length = 0;

    // proxy offline: the daemon's error ends the search
    assert.ok(m.search('offline test'));
    d.send({ ev: 'error', msg: 'search offline' });
    await until(() => !m.searching, 2000, 'offline error');
    assert.strictEqual(m.searchError, 'search offline', 'the daemon text shown on the search screen');
    // no answer at all: the app gives up on its own
    m.search('silent');
    assert.ok(m.searching && !m.checkSearch(Date.now(), 8000), 'still waiting at first');
    assert.ok(m.checkSearch(Date.now() + 9000, 8000) && !m.searching && /No answer/.test(m.searchError), 'no answer in 8 s: an error');
    d.got.length = 0;

    // search -> results (thumbs asked by the screen, see wantThumb)
    assert.ok(m.search('  cats  '));
    await lastIs(d, { cmd: 'search', q: 'cats' }, 'trimmed query');
    assert.ok(m.searching);
    d.send({ ev: 'results', q: 'dogs', items: [{ id: 'zzz' }] });
    await sleep(50);
    assert.ok(!m.results.some((r) => r.id === 'zzz'), "an older search's results are ignored");
    const items = [{ id: 'aaa', title: 'Cat video', channel: 'Cats', duration_s: 83 }, { id: 'bbb', title: 'More cats', channel: 'C', duration_s: 3723 }, { title: 'no id' }];
    d.send({ ev: 'results', q: 'cats', items });
    await until(() => m.results.length === 2, 2000, 'results');
    assert.strictEqual(m.searchError, null, 'results clear the last search error');
    assert.ok(!m.searching && m.results.length === 2);
    assert.ok(m.wantThumb('aaa') && m.wantThumb('bbb'));
    await until(() => d.cmds('thumb').length === 2, 2000, 'thumb requests');
    // a thumb: 160x90 (0.1.5 daemon, a line of 76.8 kB) or 320x180 (0.1.6, 307 kB) RGBA base64; anything else dropped
    d.send({ ev: 'thumb', id: 'aaa', w: 160, h: 90, rgba: Buffer.alloc(160 * 90 * 4, 200).toString('base64') });
    d.send({ ev: 'thumb', id: 'bbb', w: 160, h: 90, rgba: Buffer.alloc(10).toString('base64') });
    d.send({ ev: 'thumb', id: 'bbb', w: 200, h: 72, rgba: Buffer.alloc(57600).toString('base64') });
    d.send({ ev: 'thumb', id: 'nope', w: 160, h: 90, rgba: Buffer.alloc(160 * 90 * 4).toString('base64') });
    await until(() => m.thumbs.aaa, 2000, 'thumb');
    await sleep(30);
    assert.strictEqual(m.thumbs.aaa.buf.length, 57600);
    assert.ok(!m.thumbs.bbb && !m.thumbs.nope, 'wrong size or unknown id dropped');
    assert.ok(!m.wantThumb('bbb'), 'a bad thumb is not asked again in a loop');
    d.send({ ev: 'thumb', id: 'bbb', w: 320, h: 180, rgba: Buffer.alloc(320 * 180 * 4, 7).toString('base64') });
    await until(() => m.thumbs.bbb, 2000, '320x180 thumb');
    assert.deepStrictEqual([m.thumbs.bbb.w, m.thumbs.bbb.h, m.pending.size], [320, 180, 0], '320x180 kept');

    // play -> preparing -> playing; buttons
    m.play('aaa', '1836x504', false);
    await lastIs(d, { cmd: 'play', id: 'aaa', rect: '1836x504', fill: false });
    assert.strictEqual(m.state, 'preparing');
    assert.ok(m.active(), 'preparing holds the app active');
    assert.strictEqual(m.toggle(), false, 'no pause while preparing');
    d.send({ ev: 'state', state: 'preparing', pct: 42, id: 'aaa', title: 'Cat video' });
    await until(() => m.pct === 42, 2000, 'pct');
    m.setWantVideo(true);
    await lastIs(d, { cmd: 'video', on: true }, 'player shown, parked: video on');
    const nVideo = d.cmds('video').length;
    d.send({ ev: 'state', state: 'playing', pct: 100, id: 'aaa', title: 'Cat video' });
    d.send({ ev: 'time', elapsed: 5000, total: 60000 });
    await until(() => m.elapsed === 5000, 2000, 'time');
    await until(() => d.cmds('video').length > nVideo, 2000, 'video again');
    assert.deepStrictEqual(d.cmds('video').slice(nVideo), [{ cmd: 'video', on: true }], 'playback start: video state told again');
    m.toggle();
    await lastIs(d, { cmd: 'pause' });
    d.send({ ev: 'state', state: 'paused', id: 'aaa', title: 'Cat video' });
    await until(() => m.state === 'paused', 2000, 'paused');
    m.toggle();
    await lastIs(d, { cmd: 'resume' });
    m.skip(-10000);
    await lastIs(d, { cmd: 'seek', ms: 0 }, '-10 s clamps at 0');
    m.elapsed = 55000; m.skip(10000);
    await lastIs(d, { cmd: 'seek', ms: 59000 }, '+10 s clamps 1 s before the end');
    m.setWantVideo(false);
    await lastIs(d, { cmd: 'video', on: false }, 'driving or hidden: video off');
    await sleep(50);
    const n = d.got.length;
    m.setWantVideo(false);
    await sleep(50);
    assert.strictEqual(d.got.length, n, 'no repeat while unchanged');
    d.send({ ev: 'error', msg: 'proxy down' });
    await until(() => m.error === 'proxy down', 2000, 'error');
    d.send({ ev: 'state', state: 'idle' });
    await until(() => m.state === 'idle', 2000, 'idle');
    assert.ok(!m.active() && m.error === null && m.elapsed === 0);
    assert.strictEqual(m.stop(), false, 'nothing to stop');

    // the account: a code asked once, signed in, a feed (at most 20, thumbs asked), no answer, signed out
    d.got.length = 0;
    assert.strictEqual(m.authStart(), false, 'no code asked before the daemon said signed out');
    d.send({ ev: 'auth', state: 'signed_out' });
    await until(() => m.auth.state === 'signed_out', 2000, 'signed out');
    assert.ok(m.authStart() && m.auth.state === 'asking' && !m.authStart(), 'asked once');
    await lastIs(d, { cmd: 'auth' });
    d.send({ ev: 'auth', state: 'code', code: 'ABC-DEF-GHIJ', url: 'https://www.google.com/device', expires: 1800 });
    await until(() => m.auth.code === 'ABC-DEF-GHIJ', 2000, 'code');
    assert.strictEqual(m.feed('home'), false, 'no feed while signed out');
    d.send({ ev: 'auth', state: 'error', msg: 'timeout' });
    await until(() => m.auth.state === 'error', 2000, 'auth error');
    assert.ok(!m.authStart() && m.authStart(true), 'after an error only a retry asks again');
    d.send({ ev: 'auth', state: 'signed_in' });
    await until(() => m.auth.state === 'signed_in', 2000, 'signed in');
    d.got.length = 0;
    assert.ok(m.feed('subs') && !m.feed('subs') && m.feeds.subs.loading, 'one feed request at a time');
    await lastIs(d, { cmd: 'feed', which: 'subs' });
    const many = Array.from({ length: 25 }, (_, i) => ({ id: 'sub' + i, title: 'Sub ' + i, channel: 'C', duration_s: 60, meta: ['1K views', '2 days ago'] }));
    d.send({ ev: 'feed', which: 'subs', items: many.concat([{ bad: 1 }]) });
    await until(() => m.feeds.subs.items.length, 2000, 'feed');
    assert.ok(m.feeds.subs.items.length === 20 && !m.feeds.subs.loading && m.feeds.subs.error === null, 'at most 20');
    assert.strictEqual(m.feeds.subs.shelves, null, 'no shelves (an older daemon): none');
    assert.deepStrictEqual(m.feeds.subs.items[0].meta, ['1K views', '2 days ago'], 'meta kept');
    await sleep(30);
    assert.strictEqual(d.cmds('thumb').length, 0, 'a feed asks no thumbs on its own');
    // shelves: at most 8 of at most 12 videos, empty ones dropped, [] = none; their videos are known (thumbs, titles)
    const shelf = (k, n) => ({ title: 'Shelf ' + k, items: Array.from({ length: n }, (_, i) => ({ id: 's' + k + '_' + i, title: 'T' + k + '.' + i })) });
    d.send({ ev: 'feed', which: 'subs', items: many, shelves: [shelf(0, 15), { title: 'empty', items: [] }, 'bad'].concat(Array.from({ length: 9 }, (_, k) => shelf(k + 1, 3))) });
    await until(() => m.feeds.subs.shelves, 2000, 'shelves');
    assert.deepStrictEqual(m.feeds.subs.shelves.map((x) => x.items.length), [12, 3, 3, 3, 3, 3, 3, 3], 'shelves capped');
    assert.strictEqual(m.feeds.subs.shelves[0].title, 'Shelf 0');
    assert.ok(m.item('s1_2') && m.item('s1_2').title === 'T1.2' && m.wantThumb('s1_2'), 'a shelf video is known');
    d.send({ ev: 'feed', which: 'subs', items: many, shelves: [] });
    await until(() => m.feeds.subs.shelves === null, 2000, 'shelves [] = none');
    assert.ok(!m.pending.has('s1_2'), 'its video gone: no longer pending');
    d.send({ ev: 'thumb', id: 'sub3', w: 160, h: 90, rgba: Buffer.alloc(57600, 1).toString('base64') });
    await until(() => m.thumbs.sub3, 2000, 'feed thumb kept');
    m.play('sub3', '1280x720', false);
    assert.strictEqual(m.title, 'Sub 3', 'a feed item plays with its title');
    // the tile tapped: its title and channel, kept while the daemon says only the id; its own title then wins
    m.play('zzz', '1280x720', false, { id: 'zzz', title: 'Tapped tile', channel: 'Its channel' });
    d.send({ ev: 'state', state: 'preparing', pct: 5, id: 'zzz', title: 'zzz' });
    await until(() => m.pct === 5, 2000, 'preparing zzz');
    assert.deepStrictEqual([m.title, m.channel], ['Tapped tile', 'Its channel'], 'the id is not shown as the title');
    d.send({ ev: 'state', state: 'playing', id: 'zzz', title: 'Real title' });
    await until(() => m.state === 'playing', 2000, 'playing zzz');
    assert.strictEqual(m.title, 'Real title', "the daemon's own title");
    d.send({ ev: 'state', state: 'playing', id: 'sub4', title: 'sub4' });
    await until(() => m.id === 'sub4', 2000, 'another video');
    assert.deepStrictEqual([m.title, m.channel], ['Sub 4', 'C'], "another video (the daemon's, only its id said): title and channel from the list");
    d.send({ ev: 'state', state: 'idle' });
    m.feed('wl');
    assert.ok(!m.checkFeeds(Date.now(), 15000) && m.checkFeeds(Date.now() + 16000, 15000) && /No answer/.test(m.feeds.wl.error), 'no answer in 15 s: an error');
    m.feeds.wl.loading = false;
    m.feed('wl');
    d.send({ ev: 'feed', which: 'wl', error: 'feed offline' });
    await until(() => m.feeds.wl.error === 'feed offline', 2000, 'feed error');
    assert.strictEqual(m.error, null, 'a feed error is not a playback error');
    d.got.length = 0;
    assert.ok(m.signOut());
    await lastIs(d, { cmd: 'sign_out' });
    d.send({ ev: 'auth', state: 'signed_out' });
    await until(() => m.auth.state === 'signed_out', 2000, 'signed out again');
    assert.deepStrictEqual(m.feeds, {}, 'signed out: the feeds are gone');
    assert.ok(!m.thumbs.sub3, 'and their thumbs');
    // an older daemon: no sign-in, and nothing shown as an error
    d.send({ ev: 'error', msg: 'unknown cmd auth_status' });
    await until(() => m.auth.state === 'unsupported', 2000, 'unsupported');
    assert.strictEqual(m.error, null);

    // a bad line is skipped, the next one read
    d.conn.write('not json\n{"ev":"time","elapsed":1,"total":2}\n');
    await until(() => m.total === 2, 2000, 'line after a bad one');

    // the daemon goes away and comes back: reconnect within 2 s, status asked again
    const statuses = d.cmds('status').length;
    m.onMsg({ ev: 'results', q: m.q, items: [{ id: 'lib2', title: 'Second' }] });
    assert.ok(m.wantThumb('lib2'), 'lib2 asked');
    d.conn.destroy();
    await until(() => !m.connected, 2000, 'down');
    assert.strictEqual(m.send({ cmd: 'status' }), false, 'commands dropped while down');
    assert.strictEqual(m.pending.size, 0, 'down: what was asked is asked again once back');
    await until(() => d.conns === 2, 3500, 'reconnect');
    await until(() => d.cmds('status').length === statuses + 1, 2000, 'status after reconnect');
    ctl.close();
    d.server.close();
    assert.strictEqual(clock(83000), '1:23');
    assert.strictEqual(clock(3723000), '1:02:03');
    console.log('ok   ctl client + state machine');
}

// renderer stream: message types, picture ids drawn (op 18, native form: id in word 6), whether video 1 is drawn (op 19)
function scan(s) {
    const r = { types: [], pics: [], all: [], frames: [], op19: false, vrect: null, xf: false };
    for (let o = 0; o + 8 <= s.length;) {
        const t = s.readUInt32LE(o), len = s.readUInt32LE(o + 4);
        r.types.push(t);
        if (t === 7) { r.pics = []; r.frames.push(r.pics); r.vrect = null; }   // vrect: the last frame's
        if (t === 7) for (let i = o + 8; i + 28 <= o + 8 + len; i += 4) {
            const w = s.readUInt32LE(i);
            if (w === 19 && s.readUInt32LE(i + 24) === 1) { r.op19 = true; r.vrect = [4, 8, 12, 16].map((k) => s.readFloatLE(i + k)); }
            if (w === 18 && s.readUInt32LE(i + 24) > 0 && s.readUInt32LE(i + 24) < 4096) { r.pics.push(s.readUInt32LE(i + 24)); r.all.push(s.readUInt32LE(i + 24)); }
        }
        o += 8 + len;
    }
    return r;
}

// the app itself, drawn into a renderer stream (preview path of kit/tools/hu-stub.js)
async function appFrames() {
    const stage = path.join(__dirname, '..', '..', 'dist', 'iyt_app');
    if (!fs.existsSync(path.join(stage, 'source', 'javascript', 'app.js'))) { console.log('skip app frames (python3 kit/tools/build.py iyt_app first)'); return; }
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'yt-app-'));
    const sock = path.join(dir, 'ctl.sock'), file = path.join(dir, 'stream.bin');
    const d = await fakeDaemon(sock);
    process.env.MGU_YT_SOCKET = sock;
    process.env.MGU_RENDERD_FILE = file;
    const vfile = process.env.MGU_YT_VIDEO = path.join(dir, 'mgu-video-iyt');
    const { headUnit } = require('./hu-stub');
    const hu = headUnit(stage, { dataDir: dir, fresh: true, image: () => Promise.resolve(), log: quiet });
    const EventEmitter = require('events');
    hu.ctx.app = new EventEmitter();
    const visibilityListeners = [];
    const originalOnVisible = hu.ui.onVisible;
    hu.ui.onVisible = (fn) => { visibilityListeners.push(fn); originalOnVisible(fn); };
    const disp = hu.display;
    // parked: the car reads 0 km/h (the video gate counts no speed as moving)
    let speedH = null;
    const speedHandlers = [];
    let gearH = null;
    let batH = null;
    hu.ctx.signals = { watch: async (i, n, h, log, opts) => {
        if (opts && opts.onAvailability) opts.onAvailability(true);
        if (h && h.statusCarSpeed2) {
            speedHandlers.push(h.statusCarSpeed2);
            speedH = (v) => speedHandlers.forEach((fn) => fn(v));
            h.statusCarSpeed2({ speedVehicleCentreOfGravity: 0 });
        }
        if (h && h.statusGearboxDrive) gearH = h.statusGearboxDrive;
        if (h && h.statusBattery2) batH = h.statusBattery2;
        return {};
    } };
    // (the stub's ctx predates these: as kit/mgu.js)
    hu.ctx.hideButton = (id, hide) => disp.hideButton(id, hide);
    hu.ctx.onPageFocus = (fn) => { disp.onPageFocus = fn; };
    hu.ctx.focus = (k) => disp.focusPage(k);
    hu.start();
    await until(() => d.cmds('auth_status').length, 3000, 'app connects and asks for the account');

    disp.gpu.touch = true; disp._place();
    const keys = () => disp.pageTargets.map((t) => t.key);
    await hu.ui.open('VIEW'); await hu.loopFn();
    assert(keys().includes('action:search') && keys().includes('action:settings') && keys().includes('action:exit'));
    assert(keys().includes('nav:home') && keys().includes('nav:subs'));
    hu.handlers.BTN_S1();
    await until(() => d.cmds('search').length,2000,'search');
    const items=Array.from({length:50},(_,i)=>({id:'VID'+String(i).padStart(8,'0'),title:'Video '+i,channel:'Sample channel',duration_s:120+i,meta:['HD']}));
    d.send({ev:'results',q:'Music',items});
    await sleep(100); await hu.loopFn();
    let rows=disp.pageTargets.filter((t)=>/^r:\d+:VID/.test(t.key));
    assert(rows.length>=3 && rows.length<=6,'only visible and neighbouring list rows registered');
    assert(rows.every((t)=>t.w>1400 && t.h>=112 && t.h<=142),'large list targets');
    assert(d.cmds('thumb').length<=5,'only visible thumbnails requested');
    const visible=rows.filter((t)=>t.hitRect);
    assert(visible.every((t,i)=>i===0 || t.y>=visible[i-1].y+visible[i-1].h),'rows do not overlap');
    if(disp.app) {
        const kit=path.join(stage,'source/javascript/kit');
        const {Canvas}=require(path.join(kit,'canvas'));
        const {play}=require(path.join(kit,'record'));
        const preview=new Canvas(1600,Math.ceil(520+(disp.place.extra||0))).clear('#10151b');
        play(disp.app.words,preview);
        fs.writeFileSync(path.join(__dirname,'../../../reports/horizon-home-preview.png'),preview.png());
    }
    const next=rows[rows.length-1]; disp.onPageFocus(next.key); await hu.loopFn();
    const focused=disp.pageTargets.find((t)=>t.key===next.key);
    assert(focused && focused.hitRect,'controller focus scrolls next row into view');
    assert(disp.onScroll(100000)); await hu.loopFn();
    assert(disp.pageTargets.some((t)=>t.key.includes('VID00000009') && t.hitRect),'last accepted result reachable (client caps search at ten)');
    assert(disp.onScroll(-100000)); await hu.loopFn();
    rows=disp.pageTargets.filter((t)=>/^r:\d+:VID/.test(t.key));
    fs.writeFileSync(vfile,'');
    rows.find((t)=>t.hitRect).run();
    await until(()=>d.cmds('play').length,2000,'row plays');
    const id=d.cmds('play').slice(-1)[0].id;
    d.send({ev:'state',state:'playing',id,title:'Video 0'});d.send({ev:'time',elapsed:1000,total:120000});
    speedH({speedVehicleCentreOfGravity:0});
    await sleep(400); await hu.loopFn();
    assert(keys().includes('action:back'));
    assert(!keys().some((k)=>['action:search','action:settings','action:exit'].includes(k)),'main actions hidden in player');
    assert(keys().includes('ov:play'));
    disp.pageTargets.find((t)=>t.key==='ov:play').run();
    await until(()=>d.cmds('pause').length,1000,'pause command');
    speedH({speedVehicleCentreOfGravity:20*64});await sleep(300);await hu.loopFn();
    assert.strictEqual(d.cmds('video').slice(-1)[0].on,false,'moving video remains blocked');
    speedH({speedVehicleCentreOfGravity:0});
    await disp.pageTargets.find((t)=>t.key==='action:back').run();
    await sleep(100); await hu.loopFn();
    assert(d.cmds('stop').length,'Back stops playback');
    assert(keys().includes('action:settings'));
    await disp.pageTargets.find((t)=>t.key==='action:settings').run();
    // The test HMI does not draw menu states; return explicitly to the canvas.
    await hu.ui.open('VIEW');await hu.loopFn();
    let notify,starts=0;
    hu.ctx.app.getUseCaseFactory=async()=>({create:async()=>({token:'test',proxy:{init:async()=>{},waitUntilAvailable:async()=>{},notify:{subscribe:async(cb)=>{notify=cb;return 1;},unsubscribe:async()=>{}},interactionState:{getValue:async()=> 'READY'},start:async()=>{starts++;}}})});
    const request=hu.handlers.BTN_SEARCH();await until(()=>starts===1,1000,'keyboard');
    await hu.handlers.BTN_SEARCH();assert.strictEqual(starts,1);
    assert.strictEqual(disp._shown(),false);assert.strictEqual(disp.gpu.grabbing,false);
    hu.ctx.app.emit('changeVisibility',{visible:false});
    notify({interactionState:'COMPLETED',interactionParameters:new Map([[102,'new query'],[105,true]])});await request;
    await until(()=>d.cmds('search').some((q)=>q.q==='new query'),1000,'confirmed query');
    await hu.loopFn();
    hu.ctx.app.emit('changeVisibility',{visible:false});
    await until(()=>d.conn.destroyed,1000,'hidden playback connection closed');
    const count=d.conns;hu.ctx.app.emit('changeVisibility',{visible:true});
    await until(()=>d.conns>count,1000,'reopen');await hu.loopFn();
    const closed=[];hu.ui.close=async(name)=>closed.push(name);
    await disp.pageTargets.find((t)=>t.key==='action:exit').run();
    await until(()=>d.conn.destroyed,1000,'Exit disconnect');assert(closed.includes('VIEW'));
    d.server.close();
    console.log('ok   large list, bounded thumbnails, rotary scroll, player-only Back, motion gate, Settings, Search handoff and Exit');
}

function extrasModel() {
    const m = new Model(() => true);
    m.onMsg({ ev: 'positions', items: [{ id: 'AAAAAAAAAAA', ms: 60000, total: 600000, done: false, title: 'Half' }, { id: 'BBBBBBBBBBB', ms: 590000, total: 600000, done: true, title: 'Seen' },
        { id: 'CCCCCCCCCCC', ms: 5000, total: 600000, done: false, title: 'Barely' }, { id: 'bad' }] });
    assert.deepStrictEqual(m.resume.map((r) => r.id), ['AAAAAAAAAAA'], 'Continue watching: started, not finished');
    assert.deepStrictEqual(Object.keys(m.pos).sort(), ['AAAAAAAAAAA', 'BBBBBBBBBBB', 'CCCCCCCCCCC'], 'every position for the bars');
    assert.ok(m._known('AAAAAAAAAAA'), 'its thumb can be asked');
    m.onMsg({ ev: 'state', state: 'playing', id: 'AAAAAAAAAAA', title: 'Half' });
    m.onMsg({ ev: 'extras', id: 'AAAAAAAAAAA', chapters: [[0, 'Intro'], [30000, 'Main'], 'x'], segments: [[10000, 20000, 'sponsor'], [5, 1]] });
    assert.strictEqual(m.extras.chapters.length, 2); assert.strictEqual(m.extras.segments.length, 1);
    m.onMsg({ ev: 'time', elapsed: 31000, total: 600000 });
    assert.strictEqual(m.chapter(), 'Main');
    m.onMsg({ ev: 'skipped', category: 'sponsor', ms: 10000 });
    assert.strictEqual(m.toast.text, 'Skipped sponsor · 0:10');
    m.onMsg({ ev: 'state', state: 'preparing', id: 'DDDDDDDDDDD' });
    m.onMsg({ ev: 'retry', id: 'DDDDDDDDDDD', n: 2, msg: 'boom' });
    assert.strictEqual(m.retry, 2, 'the network lost: trying again (2)');
    m.onMsg({ ev: 'state', state: 'playing', id: 'DDDDDDDDDDD' });
    assert.strictEqual(m.retry, 0, 'playing: no more retry note');
    console.log('ok   extras: Continue watching, positions, chapters, the skipped toast');
}

function channelSearch() {
    const m = new Model(() => true);
    m.auth.state = 'signed_in';
    m.loadChannels();
    m.onMsg({ ev: 'channels', items: [{ id: 'UCdemo000000000000000001', title: 'Demo Detailing', handle: '@demo_detailing' },
        { id: 'UCdemo000000000000000002', title: 'Élise Atelier', handle: '@eliseatelier' }, { id: 'UCdemo000000000000000003', title: 'Arcadia', handle: '@arcadia' }, { id: 'bad', title: 'x' }] });
    const ids = (q) => m.findChannels(q).map((c) => c.title);
    assert.deepStrictEqual(ids(''), ['Demo Detailing', 'Élise Atelier', 'Arcadia'], 'all, a bad id dropped');
    assert.deepStrictEqual(ids('e'), ['Élise Atelier'], 'one letter: names starting with it, accents aside');
    assert.deepStrictEqual(ids('A'), ['Arcadia'], 'case aside');
    assert.deepStrictEqual(ids('atelier'), ['Élise Atelier'], 'a word: names holding it');
    assert.deepStrictEqual(ids('ar'), ['Arcadia'], 'two letters: held, not only at the start');
    assert.deepStrictEqual(ids('demo_d'), ['Demo Detailing'], 'the @handle too');
    console.log('ok   channel search: a letter = the names starting with it, a word = the names (or handles) holding it');
}

clientAndModel().then(appFrames).then(channelSearch).then(extrasModel).then(() => process.exit(0), (e) => { console.error('FAIL', e); process.exit(1); });
