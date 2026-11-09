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
console.log('Built original Slate logo from shared vector geometry');
