"""Local source transformation; never connects to a vehicle."""
from pathlib import Path
import json
import shutil

root = Path(__file__).resolve().parents[1]
src = root / 'source'
# Preserve all copyright and licence headers; change only the fork's identities.
for p in src.rglob('*'):
    if p.is_file() and p.suffix in ('.js', '.py', '.json', '.sh', '.service', '.md'):
        text = p.read_text()
        text = text.replace('jap-ridetube-d', 'iyt-daemon').replace('jap_ridetube', 'iyt_app')
        p.write_text(text)
for old, new in [('apps/jap_ridetube', 'apps/iyt_app'), ('native/jap-ridetube-d', 'native/iyt-daemon')]:
    if (src / old).exists():
        (src / old).rename(src / new)
service = src / 'native/iyt-daemon/systemd'
old = service / 'jap-ridetube-d.service'
if old.exists():
    old.rename(service / 'iyt-daemon.service')
p = src / 'apps/iyt_app/app.json'
app = json.loads(p.read_text())
app.update(title='iYT', version='0.4.0', loggingId='OARE')
app['settings'] = [s for s in app['settings'] if s['key'] != 'video_driving']
for screen in app['screens']:
    screen['title'] = screen['title'].replace('RideTube', 'iYT')
p.write_text(json.dumps(app, indent=2) + '\n')
p = src / 'native/iyt-daemon/component.json'
c = json.loads(p.read_text())
c.update(version='0.4.0', title='iYT service')
p.write_text(json.dumps(c, indent=2) + '\n')
p = service / 'iyt-daemon.service'
t = p.read_text().replace('After=local-fs.target', 'After=local-fs.target\nStartLimitIntervalSec=120\nStartLimitBurst=5')
t = t.replace('ExecStart=/usr/bin/node', 'ExecStart=/var/opt/jap-node22/current/bin/node')
p.write_text(t)
# Also namespace the producer's default SHM path, inspected separately from app IDs.
for p in src.rglob('*'):
    if p.is_file() and p.suffix in ('.js', '.cpp', '.h', '.md'):
        t = p.read_text().replace('/dev/shm/jap-ridetube', '/dev/shm/rte-ridetube')
        p.write_text(t)

p = src / 'native/iyt-daemon/ytfetch.py'
t = p.read_text()
t = t.replace("/ba[ext=m4a]/ba'", "'")
# Do not fall back to >30fps or unknown containers: the demuxer consumes fragmented MP4 only.
t = t.replace("[vcodec^=avc1]", "[vcodec^=avc1][ext=mp4][protocol=https]")
t = t.replace("f'/bv[vcodec^=avc1][ext=mp4][protocol=https][height<={h}][fps<=30]/bv[vcodec^=avc1][ext=mp4][protocol=https][height<={h}]'", "f'/bv[vcodec^=avc1][ext=mp4][protocol=https][height<={h}][fps<=30]'")
t = t.replace("    ranges = [(0, min(first, total))]", "    if total <= 0 or first <= 0 or chunk <= 0 or not 1 <= conns <= 8:\n        raise ValueError('E_RANGE_ARGUMENT: invalid download bounds')\n    ranges = [(0, min(first, total))]")
t = t.replace("                    pos = s\n", "                    expected = f'bytes {s}-{e - 1}/{total}'\n                    if r.headers.get('Content-Range') != expected:\n                        raise OSError('E_RANGE_MISMATCH: unexpected Content-Range')\n                    if r.headers.get('Content-Encoding', 'identity') != 'identity':\n                        raise OSError('E_RANGE_ENCODING: encoded byte range')\n                    length = r.headers.get('Content-Length')\n                    if length is not None and int(length) != e - s:\n                        raise OSError('E_RANGE_LENGTH: incorrect Content-Length')\n                    pos = s\n")
t = t.replace("                        os.pwrite(fd, b, pos)\n                        pos += len(b)", "                        written = 0\n                        while written < len(b):\n                            n = os.pwrite(fd, b[written:], pos + written)\n                            if n <= 0:\n                                raise OSError('E_DISK_WRITE: no write progress')\n                            written += n\n                        pos += len(b)")
t = t.replace("def read_box(f):", "MAX_MEDIA_BOX = 32 << 20  # hard memory bound per fragmented-MP4 box\n\n\ndef read_box(f):")
t = t.replace("        size = struct.unpack('>Q', x)[0]", "        if len(x) != 8:\n            raise ValueError('E_MEDIA_TRUNCATED: extended box header')\n        size = struct.unpack('>Q', x)[0]")
t = t.replace("        body = f.read()", "        body = f.read(MAX_MEDIA_BOX + 1)\n        if len(body) > MAX_MEDIA_BOX:\n            raise ValueError('E_MEDIA_LIMIT: box exceeds 32 MiB')")
t = t.replace("        body = f.read(size - len(h))", "        if size > MAX_MEDIA_BOX:\n            raise ValueError('E_MEDIA_LIMIT: box exceeds 32 MiB')\n        body = f.read(size - len(h))")
t = t.replace("            nal = data[i + ls:i + ls + n]", "            if n > len(data) - i - ls:\n                raise ValueError('E_MEDIA_TRUNCATED: NAL payload')\n            nal = data[i + ls:i + ls + n]")
t = t.replace("        return bytes(out)\n\n\ndef read_box", "        if i != len(data):\n            raise ValueError('E_MEDIA_TRUNCATED: NAL length')\n        return bytes(out)\n\n\ndef read_box")
p.write_text(t)
# Correct the original HTTP test server to emit the required standard response header.
p = src / 'native/iyt-daemon/test/test_ytfetch.py'
t = p.read_text().replace("        self.send_header('Content-Length', str(len(body)))", "        self.send_header('Content-Length', str(len(body)))\n        if code == 206:\n            self.send_header('Content-Range', f'bytes {s}-{e}/{len(data)}')")
p.write_text(t)
# Bound malformed native index allocations; read only records actually present on disk.
p = src / 'native/ytdec/src/index.cpp'
t = p.read_text().replace('#include <unistd.h>', '#include <unistd.h>\n#include <sys/stat.h>\n#include <algorithm>')
t = t.replace('    const uint32_t n = le32(c);', '''    struct stat st;
    if (fstat(fd_, &st) != 0 || st.st_size < (off_t)kHead)
        return false;
    const uint64_t available = ((uint64_t)st.st_size - kHead) / kRec;
    // At 30 fps, 2M records cover over 18 hours; never trust a published count.
    const size_t n = (size_t)std::min<uint64_t>(le32(c), std::min<uint64_t>(available, 2000000));''')
t = t.replace('std::vector<uint8_t> buf((n - recs.size()) * kRec);', 'std::vector<uint8_t> buf(std::min<size_t>(n - recs.size(), 4096) * kRec);')
p.write_text(t)
# Reject oversize access-unit allocations even if a malformed index refers to a large file.
p = src / 'native/ytdec/src/player.cpp'
t = p.read_text().replace('    au_.resize(r.size);', '''    if (r.size > (16u << 20)) {
        emit_("{\\"ev\\":\\"error\\",\\"msg\\":\\"E_MEDIA_LIMIT: access unit exceeds 16 MiB\\"}");
        return false;
    }
    au_.resize(r.size);''')
p.write_text(t)
print('Fork identities and reliability patches applied.')
