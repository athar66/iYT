# Installation compatibility candidate 0.5.2

The stable Store catalog and main branch remain at the user-confirmed working
0.4.2. This branch is a separate source-install candidate, not a promoted release.

The new VehicleInformation permissions in 0.5.0 and 0.5.1 requested `rs` for
`statusGearboxDrive` and `DataPowerTrain2`. The gear-cluster reference declares
both fields as subscription-only (`s`). This candidate matches that declaration
and no longer asks BMW's app manager for unverified getter permissions.

The user identified `GenerateSomeipInterface` as the failing installation stage.
The full exception and target interface catalog have not been provided, so the
unsupported getter request remains the strongest compatibility hypothesis,
not a confirmed reproduction of BMW's failure. Host packaging and synthetic
SDK-donor tests do not execute BMW's app manager.

Search, Settings, Exit and controller fixes from 0.5.1 are retained. Cluster
video still requires explicit Park, zero speed and fresh data. Removing getter
permissions does not relax that requirement: if the firmware only notifies gear
changes and supplies no fresh Park samples, cluster video remains blocked.

To test without changing the stable release, select the
`codex/install-compatibility` branch for the iYT repository source in MGU Store.
Update both iYT and its playback service to the candidate 0.5.2. Record the
installation details if BMW's app manager still rejects the package. Return
the source to Releases for the stable 0.4.2 packages.
