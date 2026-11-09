# Installation compatibility release 0.5.2

The user confirmed that version 0.5.2 installs and runs successfully. Its
notification-only gear permissions are retained in 0.5.3. Earlier packages
remain available for rollback.

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

Refresh the iYT repository source in MGU Store using Releases, then update both
iYT and its playback service to 0.5.2. Record the installation details if BMW's
app manager still rejects the package. Actual vehicle installation is still
unverified; promotion does not establish that BMW's reported failure is resolved.
