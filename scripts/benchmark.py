"""Host-only comparison. Reports measurements, never estimates vehicle performance."""
from pathlib import Path
import json
import statistics
import subprocess
import time
r = Path(__file__).resolve().parents[1]
report = {'environment': 'WSL Ubuntu x86_64; fake decoder, synthetic frames; NOT vehicle playback', 'results': []}
for label, tree in [('baseline', r/'.tools/baseline'), ('enhanced', r/'source')]:
    exe = tree/'native/ytdec/build/host/player_test'
    samples = []
    for _ in range(5):
        start = time.perf_counter()
        p = subprocess.run([str(exe)], capture_output=True, text=True, check=True)
        samples.append((time.perf_counter()-start)*1000)
    report['results'].append({'variant': label, 'wall_ms': samples, 'median_ms': statistics.median(samples), 'output': p.stdout})
(r/'reports/benchmark.json').write_text(json.dumps(report, indent=2)+'\n')
print(json.dumps(report, indent=2))
