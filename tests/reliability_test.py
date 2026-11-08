"""Offline regressions for confirmed media corruption and allocation risks."""
from pathlib import Path
import importlib.util
import io
import struct
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('ytfetch', ROOT / 'source/native/iyt-daemon/ytfetch.py')
y = importlib.util.module_from_spec(spec)
spec.loader.exec_module(y)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        start, end = map(int, self.headers['Range'][6:].split('-'))
        data = b'abcdefghijklmnopqrstuvwxyz'
        self.send_response(206)
        self.send_header('Content-Range', f'bytes {start if self.server.valid else 0}-{end}/{len(data)}')
        self.send_header('Content-Length', str(end - start + 1))
        self.end_headers()
        self.wfile.write(data[start:end + 1])
    def log_message(self, *args):
        pass

class Reliability(unittest.TestCase):
    def test_format_diagnostics_do_not_expose_signed_urls(self):
        result = y.media_format({'format_id': '136', 'vcodec': 'avc1.64001f', 'height': 720, 'fps': 30,
                                 'url': 'https://example.invalid/private?signature=secret', 'http_headers': {'Authorization': 'secret'}})
        self.assertEqual(result, {'format_id': '136', 'vcodec': 'avc1.64001f', 'height': 720, 'fps': 30})

    def test_oversized_box(self):
        with self.assertRaisesRegex(ValueError, 'E_MEDIA_LIMIT'):
            y.read_box(io.BytesIO(struct.pack('>I4s', 0x7fffffff, b'mdat')))

    def test_truncated_extended_header(self):
        with self.assertRaisesRegex(ValueError, 'E_MEDIA_TRUNCATED'):
            y.read_box(io.BytesIO(struct.pack('>I4s', 1, b'mdat') + b'12'))

    def test_range_validation_and_short_writes(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            with tempfile.TemporaryDirectory() as d:
                out = str(Path(d) / 'part')
                server.valid = True
                original = y.os.pwrite
                y.os.pwrite = lambda fd, b, offset: original(fd, b[:2], offset)
                try:
                    y.ranged_get(f'http://127.0.0.1:{server.server_port}', {}, out, 26, conns=2, first=5, chunk=7)
                    self.assertEqual(Path(out).read_bytes(), b'abcdefghijklmnopqrstuvwxyz')
                finally:
                    y.os.pwrite = original
                server.valid = False
                with self.assertRaisesRegex(OSError, 'E_RANGE_MISMATCH'):
                    y.ranged_get(f'http://127.0.0.1:{server.server_port}', {}, out, 26, conns=2, first=5, chunk=7)
        finally:
            server.shutdown()
            thread.join()
            server.server_close()

    def test_invalid_download_bounds(self):
        for args in ({'total': 0}, {'total': 1, 'chunk': 0}, {'total': 1, 'conns': 0}):
            with self.assertRaisesRegex(ValueError, 'E_RANGE_ARGUMENT'):
                y.ranged_get('', {}, '', **args)

    def test_format_policy(self):
        self.assertNotIn('/ba', y.AUDIO_FMT.replace('/ba[ext=m4a][acodec=mp4a.40.2]', ''))
        for candidate in y.video_fmt(720).split('/'):
            self.assertIn('[fps<=30]', candidate)
            self.assertIn('[ext=mp4]', candidate)

if __name__ == '__main__':
    unittest.main()
