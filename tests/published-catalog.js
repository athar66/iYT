'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert');
const root = path.resolve(__dirname, '..');
const storeCatalog = require('../upstream/mgu-store/native/mgu-updater/js/catalog');
const catalog = storeCatalog.parse(fs.readFileSync(path.join(root, 'reports/published-catalog.json'), 'utf8'));
assert.deepStrictEqual(catalog.components.map(c => c.id), ['iyt_app', 'iyt-daemon']);
for (const component of catalog.components) {
    assert(component.artifact.url.startsWith('https://api.github.com/repos/athar66/iYT/releases/assets/'));
}
console.log('Published private catalog accepted by the actual Store parser; both artifacts use authenticated asset URLs.');
