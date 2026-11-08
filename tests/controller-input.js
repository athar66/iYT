'use strict';
const assert = require('assert');
const {decode} = require('../source/kit/runtime/controller-input');
const {Display} = require('../source/kit/runtime/display');
const raw = (k, pb, df) => ({frontRotaryEncoderOperation:k, frontRotaryEncoderPushButton:pb, frontRotaryEncoderDeflection:df});
const calls = [];
const d = {own:()=>true, active:()=>true, _ccu:(v)=>calls.push(v), lastRendererCcuAt:0,
    controllerInput:Display.prototype.controllerInput};
assert.strictEqual(decode(raw(NaN,0,0)), null);
assert.strictEqual(decode(raw(3,15,15)), null);
d.controllerInput(raw(3,'KEINE_BETAETIGUNG','MITTELSTELLUNG'), 'BMW signal');
d.controllerInput(raw(3,0,0), 'renderer');
assert.strictEqual(calls.length, 1);
d.controllerInput(raw(4,1,10), 'renderer');
assert.strictEqual(calls.length, 2);
d.active = () => false;
d.controllerInput(raw(5,0,0), 'BMW signal');
assert.strictEqual(calls.length, 2);
d.active = () => true;
Display.prototype.controllerFallback.call(d, raw(5,0,0));
setTimeout(() => {
    assert.strictEqual(calls.length, 3);
    d.lastRendererCcuAt = Date.now();
    Display.prototype.controllerFallback.call(d, raw(6,0,0));
    setTimeout(() => {
        assert.strictEqual(calls.length, 3);
        console.log('controller: BMW enum decoding, duplicate suppression, hidden guard and fallback arbitration passed');
    }, 60);
}, 60);
