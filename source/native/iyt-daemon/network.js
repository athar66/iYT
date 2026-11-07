'use strict';
// SPDX-License-Identifier: GPL-3.0-or-later
const fs = require('fs');
const net = require('net');
const dns = require('dns');
function uplinkLookup(leaseFile, Resolver) {
    let lease;
    try { lease = JSON.parse(fs.readFileSync(leaseFile || '/run/mgu-uplink/lease.json', 'utf8')); }
    catch (e) { return undefined; }
    const servers = (Array.isArray(lease.dns) ? lease.dns : []).filter(function (s) { return typeof s === 'string' && net.isIP(s) !== 0; });
    if (!servers.length) return undefined;
    const resolver = new (Resolver || dns.Resolver)();
    resolver.setServers(servers);
    return function (host, options, callback) {
        if (typeof options === 'function') { callback = options; options = {}; }
        if (typeof options === 'number') options = {family: options};
        options = options || {};
        const family = options.family === 6 ? 6 : 4;
        const finish = function (error, addresses) {
            if (error) return callback(error);
            addresses = (addresses || []).filter(function (address) { return net.isIP(address) === family; });
            if (!addresses.length) {
                const missing = new Error('No IPv' + family + ' address found for ' + host);
                missing.code = 'ENOTFOUND';
                return callback(missing);
            }
            if (options.all) return callback(null, addresses.map(function (address) { return {address: address, family: family}; }));
            return callback(null, addresses[0], family);
        };
        if (family === 6) resolver.resolve6(host, finish);
        else resolver.resolve4(host, finish);
    };
}
module.exports = {uplinkLookup: uplinkLookup};
