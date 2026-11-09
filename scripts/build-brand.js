'use strict';
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '..');
const brand = require('../source/apps/iyt_app/brand');
const {Canvas} = require('../source/kit/runtime/canvas');
const svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><rect width="100" height="100" rx="22" fill="#10151b"/>' +
    brand.polygons.map((p) => '<polygon points="' + p.map((q) => q.join(',')).join(' ') + '" fill="' + brand.color + '"/>').join('') + '</svg>\n';
const dir = path.join(root, 'source/apps/iyt_app');
fs.writeFileSync(path.join(dir, 'icon.svg'), svg);
const cv = new Canvas(512,512).clear([0,0,0,0]);
cv.roundRect(0,0,512,512,112,'#10151b');
brand.draw(cv,256,256,512);
fs.writeFileSync(path.join(dir,'icon.png'),cv.png());

// iDrive 7 app-drawer launcher icon: 140x140, transparent, the same blue logo with the same proportions,
// scaled uniformly and centred so the logo leaves LAUNCHER_MARGIN of the tile free on its wider axis
// (the shorter axis ends up slightly larger, still inside 25-30 %). icon.png stays the Store catalogue graphic.
const LAUNCHER = 140, LAUNCHER_MARGIN = 0.26;
const pts = [].concat(...brand.polygons);
const xs = pts.map((q) => q[0]), ys = pts.map((q) => q[1]);
const minX = Math.min(...xs), maxX = Math.max(...xs), minY = Math.min(...ys), maxY = Math.max(...ys);
const box = LAUNCHER * (1 - 2 * LAUNCHER_MARGIN);                          // largest logo extent, px
const size = box / Math.max(maxX - minX, maxY - minY) * 100;              // brand.draw size (100 = unit square)
const lc = new Canvas(LAUNCHER, LAUNCHER).clear([0, 0, 0, 0]);
brand.draw(lc,
    LAUNCHER / 2 - ((minX + maxX) / 2 - 50) * size / 100,
    LAUNCHER / 2 - ((minY + maxY) / 2 - 50) * size / 100, size);
fs.writeFileSync(path.join(dir, 'launcher_icon.png'), lc.png(9));
console.log('Built original Slate logo from shared vector geometry');
