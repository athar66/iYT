'use strict';
const fs=require('fs'),path=require('path'),os=require('os');
const service=require('../source/native/iyt-daemon/ytd');
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'iyt-signin-network-'));
const lease=path.join(tmp,'lease.json');
fs.writeFileSync(lease,JSON.stringify({dns:['1.1.1.1']}));
service.ytRequest('GET','https://www.youtube.com/tv',null,null,15000,service.uplinkLookup(lease)).then(function(response){
    if(response.status!==200)throw Error('TV page returned HTTP '+response.status);
    console.log('Sign-in TV page: HTTP 200 through uplink DNS on '+process.version+'; no account flow started.');
},function(error){ console.error(error.message);process.exitCode=1; });
