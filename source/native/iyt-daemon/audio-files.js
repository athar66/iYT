'use strict';
// SPDX-License-Identifier: GPL-3.0-or-later
// Publish only completed audio files; keep download folders and metadata private.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ALLOWED = ['audio.m4a', 'audio.head.m4a'];
class AudioFiles {
    constructor(opts) {
        this.cache = path.resolve(opts.cacheDir);
        this.root = path.resolve(opts.audioDir || path.join(path.dirname(this.cache), 'audio'));
        this.log = opts.log || function () {};
        this.session = null;
        this.entries = [];
        this.ready = false;
    }
    removeSession(dir, entries) {
        let complete = true;
        entries.forEach(function (entry) {
            if (!entry || ALLOWED.indexOf(entry.name) < 0) { complete = false; return; }
            const file = path.join(dir, entry.name);
            try {
                const st = fs.lstatSync(file);
                if (!st.isFile() || st.isSymbolicLink() || st.dev !== entry.dev || st.ino !== entry.ino) { complete = false; return; }
                fs.unlinkSync(file);
            } catch (e) { if (e.code !== 'ENOENT') complete = false; }
        });
        if (complete) {
            try { fs.unlinkSync(path.join(dir, 'manifest.json')); fs.rmdirSync(dir); }
            catch (e) { if (e.code !== 'ENOENT') this.log('audio export cleanup: ' + e.message); }
        }
    }
    init() {
        if (this.ready) return;
        if (!fs.existsSync(this.root)) fs.mkdirSync(this.root, 0o711);
        const st = fs.lstatSync(this.root);
        if (!st.isDirectory() || st.isSymbolicLink() || (process.getuid && st.uid !== process.getuid()))
            throw new Error('E_AUDIO_EXPORT: invalid audio publication directory');
        fs.chmodSync(this.root, 0o711);
        fs.readdirSync(this.root).filter(n => /^session-[a-f0-9]{32}$/.test(n)).forEach(name => {
            const dir = path.join(this.root, name);
            try {
                const ds = fs.lstatSync(dir), ms = fs.lstatSync(path.join(dir, 'manifest.json'));
                if (!ds.isDirectory() || ds.isSymbolicLink() || ms.isSymbolicLink() || !ms.isFile() || (ms.mode & 0o077) ||
                    (process.getuid && (ds.uid !== process.getuid() || ms.uid !== process.getuid()))) return;
                const entries = JSON.parse(fs.readFileSync(path.join(dir, 'manifest.json'), 'utf8'));
                if (Array.isArray(entries) && entries.length <= 2) this.removeSession(dir, entries);
            } catch (e) { this.log('audio export recovery: ' + e.message); }
        });
        this.ready = true;
    }
    record() {
        const file = path.join(this.session, 'manifest.json');
        const temporary = path.join(this.session, '.manifest-' + crypto.randomBytes(8).toString('hex') + '.tmp');
        const fd = fs.openSync(temporary, fs.constants.O_WRONLY | fs.constants.O_CREAT | fs.constants.O_EXCL | fs.constants.O_NOFOLLOW, 0o600);
        try { fs.writeSync(fd, JSON.stringify(this.entries)); fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
        fs.renameSync(temporary, file);
    }
    publish(source) {
        this.init();
        const absolute = fs.realpathSync(source), base = fs.realpathSync(this.cache);
        const name = path.basename(source), st = fs.lstatSync(source);
        if (absolute.indexOf(base + path.sep) !== 0 || ALLOWED.indexOf(name) < 0 || !st.isFile() || st.isSymbolicLink() || !st.size)
            throw new Error('E_AUDIO_EXPORT: invalid completed audio file');
        if (!this.session) {
            this.session = path.join(this.root, 'session-' + crypto.randomBytes(16).toString('hex'));
            fs.mkdirSync(this.session, 0o711);
            fs.chmodSync(this.session, 0o711);
        }
        const dest = path.join(this.session, name);
        const existing = this.entries.filter(e => e.name === name)[0];
        if (existing) {
            if (existing.dev !== st.dev || existing.ino !== st.ino) throw new Error('E_AUDIO_EXPORT: audio changed during playback');
            return dest;
        }
        if (this.entries.length >= 2) throw new Error('E_AUDIO_EXPORT: publication limit exceeded');
        this.entries.push({name: name, dev: st.dev, ino: st.ino});
        this.record(); // Journal ownership before linking, for crash cleanup.
        fs.linkSync(source, dest); // Same filesystem; no duplicate media download or copy.
        fs.chmodSync(dest, 0o644);
        return dest;
    }
    clear() {
        if (this.session) this.removeSession(this.session, this.entries);
        this.session = null;
        this.entries = [];
    }
}
module.exports = AudioFiles;
