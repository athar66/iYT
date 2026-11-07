'use strict';
const assert = require('assert'), fs = require('fs'), os = require('os'), path = require('path'), http = require('http');
const lookup = require('../source/native/iyt-daemon/network').uplinkLookup;
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'iyt-dns-'));
const lease = path.join(tmp, 'lease.json');
fs.writeFileSync(lease, JSON.stringify({dns: ['192.0.2.53', 'undefined', null]}));
let answers = ['127.0.0.1'];
class Resolver {
    setServers(servers) { assert.deepStrictEqual(servers, ['192.0.2.53']); }
    resolve4(host, callback) { callback(null, answers); }
    resolve6(host, callback) { callback(null, ['::1']); }
}
const resolve = lookup(lease, Resolver);
resolve('test.invalid', {all: true}, (e, a) => { assert.ifError(e); assert.deepStrictEqual(a, [{address:'127.0.0.1',family:4}]); });
resolve('test.invalid', {}, (e, a, f) => { assert.ifError(e); assert.equal(a,'127.0.0.1'); assert.equal(f,4); });
resolve('test.invalid', {family:6,all:true}, (e, a) => { assert.ifError(e); assert.deepStrictEqual(a,[{address:'::1',family:6}]); });
answers = [];
resolve('test.invalid', {all:true}, e => assert.equal(e.code, 'ENOTFOUND'));
answers = ['127.0.0.1'];
const server = http.createServer((req, res) => res.end('connected'));
server.listen(0,'127.0.0.1', () => {
    // A real connection invokes Node22's all:true lookup contract.
    const req = http.get({hostname:'test.invalid',port:server.address().port,lookup:resolve,autoSelectFamily:true}, res => {
        let body=''; res.on('data', b => body+=b); res.on('end', () => {
            assert.equal(body,'connected'); server.close();
            console.log('DNS regression: scalar/list/IPv6/empty-answer and actual HTTP connection passed.');
        });
    });
    req.on('error', e => { console.error(e); process.exitCode=1; server.close(); });
});
