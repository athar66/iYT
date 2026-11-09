'use strict';

const STALE_MS = 2000;
const IFACE = 'de.bmw.infrastructure.VehicleInformation';

function stageOf(value) {
    if (value === 'P' || value === 1) return 'P';
    if (value === 'R' || value === 2) return 'R';
    if (value === 'N' || value === 3) return 'N';
    if (value === 'D' || value === 4) return 'D';
    return null;
}

function selectionOf(value) {
    if (value === 'P' || value === 3) return 'P';
    if (value === 'R' || value === 2) return 'R';
    if (value === 'N' || value === 1) return 'N';
    if (typeof value === 'number' && Number.isInteger(value) && value >= 5 && value <= 13) return 'D';
    if (typeof value === 'string' && /^_[1-9]$/.test(value)) return 'D';
    return null;
}

function create(now) {
    now = now || Date.now;
    const gears = {};
    let speed = null, speedAt = null;
    const fresh = (at, t) => at !== null && t >= at && t - at <= STALE_MS;
    return {
        gearbox: (v) => { gears.gearbox = { stage: stageOf(v && v.statusActualStageDrive), at: now() }; },
        powertrain: (v) => { gears.powertrain = { stage: selectionOf(v && v.statusGearSelectionDrive), at: now() }; },
        speed: (v) => {
            const raw = v && v.speedVehicleCentreOfGravity;
            speed = typeof raw === 'number' && Number.isInteger(raw) && raw >= 0 && raw < 65535 ? raw / 64 : null;
            speedAt = now();
        },
        snapshot: () => {
            const t = now(), samples = Object.keys(gears).map((k) => gears[k]);
            const live = samples.filter((g) => fresh(g.at, t));
            const known = live.length > 0 && live.every((g) => g.stage !== null);
            const conflict = known && live.some((g) => g.stage !== live[0].stage);
            const stage = known && !conflict ? live[0].stage : null;
            const speedFresh = speed !== null && fresh(speedAt, t);
            const allowed = stage === 'P' && speedFresh && speed === 0;
            const expiresAt = allowed ? Math.min(speedAt + STALE_MS, ...live.map((g) => g.at + STALE_MS)) : t;
            return { allowed: allowed, stage: stage, speed: speedFresh ? speed : null, expiresAt: expiresAt,
                reason: conflict ? 'gear signals disagree' : !known ? 'gear missing, invalid or stale' :
                    stage !== 'P' ? 'not in Park' : !speedFresh ? 'speed missing, invalid or stale' :
                        speed !== 0 ? 'vehicle moving' : 'Park and zero speed confirmed' };
        },
        lost: () => { Object.keys(gears).forEach((k) => { delete gears[k]; }); speed = null; speedAt = null; },
    };
}

function watch(ctx, log, opts) {
    const state = create(opts && opts.now);
    const providers = { gear: false, speed: false };
    const options = (name) => ({ pollMs: 500, onAvailability: (available) => {
        providers[name] = available === true;
        if (!available) state.lost();
    } });
    const receive = (name, fn) => (v) => { if (providers[name]) fn(v); };
    ctx.signals.watch(IFACE, '1', {
        statusGearboxDrive: receive('gear', state.gearbox),
        DataPowerTrain2: receive('gear', state.powertrain),
    }, log, options('gear')).catch(() => state.lost());
    ctx.signals.watch('de.bmw.infotainment.vehicle.Vehicle2', '1', {
        statusCarSpeed2: receive('speed', state.speed),
    }, log, options('speed')).catch(() => state.lost());
    return state;
}

module.exports = { create, watch, stageOf, selectionOf, STALE_MS };
