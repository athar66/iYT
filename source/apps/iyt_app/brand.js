'use strict';
const color = '#1688ef';
const polygons = [
    [[42,12],[61,12],[55,28],[36,28]],
    [[34,35],[53,35],[32,88],[13,88]],
    [[30,67],[63,46],[87,46],[32,88]],
];
function draw(cv, cx, cy, size) {
    polygons.forEach((p) => cv.quad(p.map((q) => [cx + (q[0]-50)*size/100, cy + (q[1]-50)*size/100]), color));
}
module.exports = {color, polygons, draw};
