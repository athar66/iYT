'use strict';
const color = '#0095ff';
const polygons = [
    [[42,17],[59,17],[54,31],[37,31]],
    [[34,37],[51,37],[33,80],[16,80]],
    [[38,65],[61,49],[62,61],[31,80]],
    [[61,49],[86,49],[77,61],[45,61]],
];
function draw(cv, cx, cy, size) {
    polygons.forEach((p) => cv.quad(p.map((q) => [cx + (q[0]-50)*size/100, cy + (q[1]-50)*size/100]), color));
}
module.exports = {color, polygons, draw};
