# Cluster vehicle signals

The local app now subscribes to explicit selector state on
`de.bmw.infrastructure.VehicleInformation`, instance `1`:

- `statusGearboxDrive.statusActualStageDrive`: `P` or numeric `1` means Park.
- `DataPowerTrain2.statusGearSelectionDrive`: `P` or numeric `3` means Park.
  Numeric `4` / `NP` does not distinguish Neutral from Park and is rejected.

These mappings are documented in
[mgu-gear-cluster's car.js](https://github.com/sergshamiryan/mgu-gear-cluster/blob/089f4bb0cb7e09afc210e7d9ec4dcec89f725209/kit/runtime/car.js).
The implementation here does not use its demo or learned-gear fallback.
Vehicle speed comes from the existing Vehicle2 speed signal, scaled by 1/64 km/h.
Only exact zero speed qualifies.

The guard rejects missing, invalid, conflicting, future-dated or older-than-two-second
samples. At least one explicit selector must remain fresh; conflicting fresh selector readings block output. An expired alternative does not invalidate a newer explicit Park reading.
Provider loss clears the samples. Polling requests fresh values only where the
installed BMW interface exposes a getter; polling cannot make a subscription-only
field fresh. The actual target interface still needs to demonstrate fresh Park and
speed readings while stationary.

Diagnostics appends the guard's current reason to the existing status row.
Version 0.5.0 connects this provider to the production decoder's map-only route.
The native HMI setting is off by default. See [hardware test instructions](cluster-hardware-test.md).
The app sends original source expiry rather than retimestamping cached state; the
native decoder uses short monotonic leases. Target signal freshness and firmware
navigation/restoration behavior still require real-unit testing.

[waze-hud](https://github.com/JustAnotherPU/waze-hud) supplies a separate useful
cluster-render integration reference; it has not been used as evidence for the
selector enum mapping above.
