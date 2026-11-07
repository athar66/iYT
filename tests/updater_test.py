from pathlib import Path
import hashlib
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
class Updater(unittest.TestCase):
    def test_verified_staging_and_rollback_without_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            candidate = root/'candidate.zip'
            stage = root/'stage'
            def create(version):
                with zipfile.ZipFile(candidate, 'w') as z:
                    z.writestr('yt_dlp/version.py', f'__version__ = "{version}"\n')
                    z.writestr('yt_dlp/__init__.py', 'raise RuntimeError("must not execute")')
                    z.writestr('__main__.py', 'raise RuntimeError("must not execute")')
                return hashlib.sha256(candidate.read_bytes()).hexdigest()
            def run(digest):
                return subprocess.run([sys.executable, str(ROOT/'scripts/extractor-update.py'), '--candidate', str(candidate), '--sha256', digest, '--stage', str(stage)], capture_output=True, text=True)
            digest = create('2026.10.26')
            self.assertNotEqual(run('0'*64).returncode, 0)
            self.assertFalse(stage.exists())
            self.assertEqual(run(digest).returncode, 0)
            old = (stage/'yt-dlp.zipapp').read_bytes()
            digest = create('2026.11.01')
            self.assertEqual(run(digest).returncode, 0)
            self.assertEqual((stage/'yt-dlp.previous.zipapp').read_bytes(), old)
            self.assertNotEqual((stage/'yt-dlp.zipapp').read_bytes(), old)

if __name__ == '__main__':
    unittest.main()
