'use strict';
const PUSH = { KEINE_BETAETIGUNG: 0, DREHGEBER_KURZ_GEDRUECKT: 1, DREHGEBER_LANG_GEDRUECKT: 2 };
const TILT = { MITTELSTELLUNG: 0, NORD_KURZ_GEDRUECKT: 1, NORD_LANG_GEDRUECKT: 2,
    OST_KURZ_GEDRUECKT: 4, OST_LANG_GEDRUECKT: 5, SUED_KURZ_GEDRUECKT: 7,
    SUED_LANG_GEDRUECKT: 8, WEST_KURZ_GEDRUECKT: 10, WEST_LANG_GEDRUECKT: 11 };
function decode(v) {
    if (!v) return null;
    const k = v.frontRotaryEncoderOperation;
    const pb = typeof v.frontRotaryEncoderPushButton === 'number' ? v.frontRotaryEncoderPushButton : PUSH[v.frontRotaryEncoderPushButton];
    const df = typeof v.frontRotaryEncoderDeflection === 'number' ? v.frontRotaryEncoderDeflection : TILT[v.frontRotaryEncoderDeflection];
    if (!Number.isInteger(k) || k < 0 || k > 65535 || ![0, 1, 2].includes(pb) || ![0, 1, 2, 4, 5, 7, 8, 10, 11].includes(df)) return null;
    return { frontRotaryEncoderOperation: k, frontRotaryEncoderPushButton: pb, frontRotaryEncoderDeflection: df };
}
module.exports = { decode };
