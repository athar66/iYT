'use strict';
const assert = require('assert');
const {Display} = require('../source/kit/runtime/display');
let searches = 0;
const button = {x:1196, y:46, w:124, h:44, key:'action:search', priority:1, run:()=>{searches++;}};
const d = {own:()=>true, place:{scale:1.18,ox:70,oy:30,w:1920,h:720},
    barH:()=>0, tabs:[], sheet:null, pageTargets:[{x:0,y:0,w:1600,h:700,key:'wake',run:()=>{}},button], _repaint:()=>{},
    tickHandlers:[], log:{error:(e)=>{throw e;}}};
function tap(x,y) {
    // Device coordinates pass through the renderer's inverse placement transform.
    const deviceX = x*d.place.scale+d.place.ox, deviceY = y*d.place.scale+d.place.oy;
    const logicalX = (deviceX-d.place.ox)/d.place.scale, logicalY = (deviceY-d.place.oy)/d.place.scale;
    Display.prototype._touch.call(d,1,logicalX,logicalY);
    Display.prototype._touch.call(d,3,logicalX,logicalY);
}
tap(button.x+button.w/2,button.y+button.h/2);
assert.strictEqual(searches,1);
tap(button.x-20,button.y+button.h/2);
tap(button.x+button.w+20,button.y+button.h/2);
assert.strictEqual(searches,1);
let rows=0;
d.pageTargets=[{x:0,y:0,w:1000,h:400,hitRect:{x:0,y:150,w:1000,h:50},key:'row',run:()=>{rows++;}}];
tap(500,75);assert.strictEqual(rows,0,'clipped row cannot intercept header');
tap(500,170);assert.strictEqual(rows,1);
d.pageTargets.unshift({x:0,y:0,w:1600,h:700,hitRect:false,priority:100,key:'offscreen',run:()=>assert.fail('offscreen row received touch')});
tap(500,170);assert.strictEqual(rows,2);
console.log('touch layout: visible Search target matches scaled placement; adjacent blank space does not activate it');
