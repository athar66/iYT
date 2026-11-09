from pathlib import Path
import os
import subprocess
import json
r=Path(__file__).resolve().parents[1]
node=Path('/home/athar/.cache/iyt-host-tools/node8')
if not node.exists(): node=r/'.tools/node-v8.16.2-linux-x64/bin/node'
env=dict(os.environ,PATH=str(node.parent/'node8-bin')+':/usr/bin:/bin')
checks=[('network-contract',r/'tests/network-regression.js'),
        ('bridge-daemon',r/'source/native/iyt-daemon/test/test_ytd.js'),
        ('bridge-thumbnails',r/'source/native/iyt-daemon/test/test_thumb.js'),
        ('signin-tv-network',r/'tests/signin-network-smoke.js')]
results=[]
for name,test in checks:
    p=subprocess.run([str(node),'--max-http-header-size=65536',str(test)],env=env,text=True,capture_output=True,timeout=120)
    (r/'reports'/f'0.5.3-{name}.log').write_text(p.stdout+p.stderr)
    results.append({'test':name,'runtime':'Node8.16.2 platform compatibility','code':p.returncode})
    print(name+': '+str(p.returncode),flush=True)
(r/'reports/0.5.3-bridge-checks.json').write_text(json.dumps(results,indent=2)+'\n')
raise SystemExit(any(c['code'] for c in results))
