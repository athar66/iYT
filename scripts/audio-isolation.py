from pathlib import Path
r = Path(__file__).resolve().parents[1] / 'source/native/iyt-daemon'
p = r / 'ytd.js'
t = p.read_text()
start = t.index('// At start: a connection')
end = t.index('// release() waits', start)
t = t[:start] + '''// BMW exposes the same generic media source to both RideTube installations.
// A connection cannot be proven ours after a crash. Never sweep another app's audio.
Audio.prototype.dropLeftovers = async function () {
    await this.waitAvailable();
    return 0;
};
''' + t[end:]
t = t.replace("    const r = await this.cc.callMethod('connect', { sourceID: SOURCE_ID, sinkID: SINK_ID }, 5000);", "    const active = await this.cc.getValue('listOfMainConnections');\n    if ((Array.isArray(active) ? active : []).some(c => c && c.sourceID === SOURCE_ID))\n        throw new Error('E_AUDIO_BUSY: generic media source is already in use; stop the other player first');\n    const r = await this.cc.callMethod('connect', { sourceID: SOURCE_ID, sinkID: SINK_ID }, 5000);")
t = t.replace("(r.amError !== 'E_OK' && r.amError !== 'E_ALREADY_EXISTS')", "r.amError !== 'E_OK'")
t = t.replace("        await this.dropLeftovers().catch((e2) => this.opts.log('sweep failed: ' + e2));", "        this.opts.log('E_AUDIO_OWNERSHIP: no source-wide sweep; explicit connection cleanup needs hardware inspection');")
p.write_text(t)
p = r / 'test/test_ytd.js'
t = p.read_text().replace("'leftover 1046 connection removed at start, others kept'", "'startup preserves all shared generic-media connections'")
t = t.replace("assert.deepStrictEqual(called('disconnect').map((x) => x.a.mainConnectionID), [7]);", "assert.deepStrictEqual(called('disconnect').map((x) => x.a.mainConnectionID), []);\n        assert.ok(conns.some((x) => x.mainConnectionID === 7));\n        // Simulate the original player releasing its own connection.\n        conns = conns.filter(x => x.mainConnectionID !== 7);")
p.write_text(t)
print('Shared audio source no longer swept at startup or cleanup.')
