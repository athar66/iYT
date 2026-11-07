'use strict';
const fs = require('fs'), path = require('path'), assert = require('assert');
const root = path.resolve(__dirname, '..');
const storeCatalog = require('../upstream/mgu-store/native/mgu-updater/js/catalog');
const catalog = storeCatalog.parse(fs.readFileSync(path.join(root, 'reports/published-catalog.json'), 'utf8'));
assert.deepStrictEqual(catalog.components.map(c => c.id), ['iyt_app', 'iyt-daemon']);
const published=JSON.parse(fs.readFileSync(path.join(root,'reports/published-release.json'),'utf8'));
for (const component of catalog.components) {
    const prefix=published.private ? 'https://api.github.com/repos/athar66/iYT/releases/assets/' : 'https://github.com/athar66/iYT/releases/download/';
    assert(component.artifact.url.startsWith(prefix));
}
console.log('Published catalog accepted by the actual Store parser; artifact URLs match repository visibility.');
