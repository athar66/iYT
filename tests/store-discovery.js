'use strict';
// Exercise the actual Store reader and packer, not a parallel schema imitation.
const fs = require('fs');
const path = require('path');
const assert = require('assert');
const root = path.resolve(__dirname, '..');
const store = require('../upstream/mgu-store/native/mgu-updater/js/sources');
async function read(file) {
    try { return fs.readFileSync(path.join(root, file)); }
    catch (e) { if (e.code === 'ENOENT') e.missing = true; throw e; }
}
function walk(dir, prefix = '') {
    let files = [];
    for (const name of fs.readdirSync(dir)) {
        if (name === 'build' || name === 'dist' || name === '__pycache__') continue;
        const full = path.join(dir, name), relative = prefix + name;
        const st = fs.statSync(full);
        if (st.isDirectory()) files = files.concat(walk(full, relative + '/'));
        else files.push({name: relative, data: fs.readFileSync(full), mode: st.mode & 0o777});
    }
    return files;
}
(async () => {
    const catalog = await store.repoCatalog(read, null, null, dir => Promise.resolve(fs.readdirSync(path.join(root, dir))));
    assert.deepStrictEqual(catalog.skipped, []);
    assert.deepStrictEqual(catalog.components.map(c => c.id), ['iyt_app', 'iyt-daemon']);
    const app = catalog.components[0];
    assert.equal(app.title, 'iYT');
    assert.equal(app.script.sdk, 'source/oap-sdk');
    assert.equal(app.requires['iyt-daemon'], '0.5.1');
    const tool = catalog.components[1];
    const packed = store.packComponent(tool, walk(path.join(root, tool.path)));
    assert(packed.length > 1000000);
    fs.mkdirSync(path.join(root, 'dist/release'), {recursive: true});
    fs.writeFileSync(path.join(root, 'dist/release/iyt-daemon@0.5.1.tgz'), packed);
    fs.writeFileSync(path.join(root, 'reports/store-discovery.json'), JSON.stringify({
        parser: 'MGU Store upstream repoCatalog + packComponent',
        components: catalog.components.map(c => ({id: c.id, title: c.title, version: c.version, requires: c.requires})),
        skipped: catalog.skipped, toolBytes: packed.length, result: 'passed'
    }, null, 2) + '\n');
    console.log('Store discovery and service packaging passed: iYT + iYT playback service.');
})().catch(e => { console.error(e); process.exitCode = 1; });
