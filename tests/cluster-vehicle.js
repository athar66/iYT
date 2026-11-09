'use strict';
const assert = require('assert');
const vehicle = require('../source/kit/runtime/cluster-vehicle');
let t = 100;
const s = vehicle.create(() => t);
assert.strictEqual(s.snapshot().allowed, false);
s.gearbox({ statusActualStageDrive: 1 });
s.speed({ speedVehicleCentreOfGravity: 0 });
assert.strictEqual(s.snapshot().allowed, true);
for (const value of ['R', 'N', 'D', 2, 3, 4, 'NP', undefined, null, 0, 255, 'toString', true]) {
    s.gearbox({ statusActualStageDrive: value });
    assert.strictEqual(s.snapshot().allowed, false);
}
s.gearbox({ statusActualStageDrive: 'P' });
for (const value of [1, -1, 65535, NaN, Infinity, '0', null, 0.5]) {
    s.speed({ speedVehicleCentreOfGravity: value });
    assert.strictEqual(s.snapshot().allowed, false);
}
s.speed({ speedVehicleCentreOfGravity: 0 });
s.powertrain({ statusGearSelectionDrive: 3 });
assert.strictEqual(s.snapshot().allowed, true);
s.powertrain({ statusGearSelectionDrive: 1 });
assert.strictEqual(s.snapshot().allowed, false);
s.powertrain({ statusGearSelectionDrive: 'NP' });
assert.strictEqual(s.snapshot().allowed, false);
s.powertrain({ statusGearSelectionDrive: 'P' });
t += 2001;
assert.strictEqual(s.snapshot().allowed, false);
s.gearbox({ statusActualStageDrive: 'P' });
s.speed({ speedVehicleCentreOfGravity: 0 });
assert.strictEqual(s.snapshot().allowed, true); // a fresh explicit Park source can replace an expired alternative
s.powertrain({ statusGearSelectionDrive: 'P' });
assert.strictEqual(s.snapshot().allowed, true);
t -= 1;
assert.strictEqual(s.snapshot().allowed, false);
s.lost();
assert.strictEqual(s.snapshot().allowed, false);
for (const value of ['P', 3]) assert.strictEqual(vehicle.selectionOf(value), 'P');
for (const value of ['NP', 4, undefined, 'toString', 255]) assert.strictEqual(vehicle.selectionOf(value), null);
console.log('cluster vehicle: explicit Park, exact zero speed, invalid data, conflicts and freshness passed');
const subscriptions = [];
const watched = vehicle.watch({ signals: { watch: (iface, instance, handlers, log, options) => {
    subscriptions.push({ iface, instance, handlers, options });
    return Promise.resolve({ available: true });
} } }, null, { now: () => t });
assert.strictEqual(subscriptions.length, 2);
subscriptions[0].options.onAvailability(true);
subscriptions[1].options.onAvailability(true);
subscriptions[0].handlers.statusGearboxDrive({ statusActualStageDrive: 'P' });
subscriptions[1].handlers.statusCarSpeed2({ speedVehicleCentreOfGravity: 0 });
assert.strictEqual(watched.snapshot().allowed, true);
subscriptions[0].options.onAvailability(false);
assert.strictEqual(watched.snapshot().allowed, false);
subscriptions[0].handlers.statusGearboxDrive({ statusActualStageDrive: 'P' });
subscriptions[1].handlers.statusCarSpeed2({ speedVehicleCentreOfGravity: 0 });
assert.strictEqual(watched.snapshot().allowed, false); // late reply after provider loss
console.log('cluster vehicle: subscriptions and immediate provider-loss invalidation passed');
