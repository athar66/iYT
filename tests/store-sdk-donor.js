'use strict';
// The actual SDK-free iYT package is prepared by the real Store linker using
// Store's synthetic donor. The generated test SDK is never published.
const fs = require('fs'), path = require('path'), cp = require('child_process'), assert = require('assert');
const root = path.resolve(__dirname, '..');
const link = require('../upstream/mgu-store/tools/oap_link');
const donor = require('../upstream/mgu-store/tools/test/synthetic_donor');
const tmp = fs.mkdtempSync(path.join(root, '.tools/iyt-donor-test-'));
const pkg = path.join(tmp, 'package');
fs.mkdirSync(pkg);
cp.execFileSync('tar', ['-xzf', path.join(root, 'dist/release/iyt_app@0.4.2.tgz'), '-C', tmp]);
assert(link.needsSdk(pkg));
const fixture = donor.tgz(path.join(tmp, 'synthetic-donor.tgz'));
const result = link.preparePackage(pkg, path.join(tmp, 'prepared.tgz'), {donors: [fixture]});
assert(result.sdk && result.sdk.api.includes('OnlineApp') && result.sdk.api.includes('logging'));
assert(!link.needsSdk(pkg));
assert(!fs.existsSync(path.join(root, 'source/oap-sdk/index.js')));
fs.writeFileSync(path.join(root, 'reports/store-sdk-link.json'), JSON.stringify({
    result: 'passed', input: 'actual SDK-free iYT release package',
    api: result.sdk.api, donor: 'upstream synthetic fixture; NOT real BMW firmware',
    generatedSdkPublished: false
}, null, 2)+'\n');
console.log('Actual iYT package: Store supplies SDK from donor successfully (synthetic donor test).');
