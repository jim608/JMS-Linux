"""Offline packaging contracts. Optionally stage a verified real portable archive."""
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import shutil
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / 'packaging/aur/jms-bin'


def values(name):
    return subprocess.check_output([
        'bash', '-c', 'source "$1"; name=$2; declare -n value="$name"; printf "%s\\n" "${value[@]}"',
        'bash', str(RECIPE / 'PKGBUILD'), name], text=True).splitlines()


class PackagingTests(unittest.TestCase):
    def test_release_pin(self):
        metadata = json.loads((ROOT / 'releases/0.11.1-jms.25.json').read_text())
        asset = next(a for a in metadata['assets'] if a['name'].endswith('-x64.tar.gz'))
        self.assertEqual(values('sha256sums')[0], asset['sha256'])
        self.assertTrue(values('source')[0].endswith('/' + asset['name']))
        self.assertNotIn('/latest/', values('source')[0])
        self.assertEqual(values('pkgver')[0], metadata['versionName'].replace('-', '_', 1))
        self.assertEqual(values('pkgrel')[0], str(metadata['versionCode']))

    def test_desktop_checksum(self):
        self.assertEqual(values('sha256sums')[1], hashlib.sha256((RECIPE / values('source')[1]).read_bytes()).hexdigest())
        subprocess.run(['desktop-file-validate', str(RECIPE / 'com.jim608.jms.desktop')], check=True)

    def test_metadata_and_dependencies(self):
        metadata = json.loads((ROOT / 'releases/0.11.1-jms.25.json').read_text())
        self.assertTrue(set(metadata['nativeReview']['systemDependencies']) <= set(values('depends')))
        self.assertEqual(values('pkgname'), ['jms-bin'])
        self.assertEqual(values('arch'), ['x86_64'])
        self.assertEqual(values('conflicts'), ['jms'])
        self.assertEqual(values('provides'), ['jms=' + values('pkgver')[0]])
        self.assertFalse((RECIPE / 'jms-bin.install').exists())
        actual = {}
        for line in (RECIPE / '.SRCINFO').read_text().splitlines():
            if ' = ' in line:
                k, v = line.strip().split(' = ', 1)
                actual.setdefault(k, []).append(v)
        for field in ('pkgname', 'pkgver', 'pkgrel', 'pkgdesc', 'url', 'license', 'options', 'depends', 'provides', 'conflicts', 'arch', 'source', 'sha256sums'):
            self.assertEqual(actual[field], values(field), field)

    def test_repo_rejects_bad_inputs(self):
        script = ROOT / 'scripts/stage-arch-repo.sh'
        result = subprocess.run([str(script)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp) / 'JMS-Linux-0.11.1-jms.25-x86_64.pkg.tar.xz'
            package.write_bytes(b'tampered')
            output = Path(tmp) / 'repository'
            result = subprocess.run([str(script), str(package), 'A' * 40, str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b'checksum', result.stderr)
            self.assertFalse(output.exists())
            result = subprocess.run([str(script), str(package), 'short-key-id', str(output)], capture_output=True)
            self.assertEqual(result.returncode, 2)

    def test_repo_rejects_wrong_package_identity(self):
        # Exercise metadata checks with checksum-valid fixture archives, before signing.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'scripts').mkdir()
            (root / 'releases').mkdir()
            script = root / 'scripts/stage-arch-repo.sh'
            shutil.copy2(ROOT / 'scripts/stage-arch-repo.sh', script)
            package = root / 'fixture.pkg.tar.xz'
            for identity in ('pkgname = other\narch = x86_64\n',
                             'pkgname = jms\narch = aarch64\n',
                             'pkgname = jms\npkgname = other\narch = x86_64\n'):
                with tarfile.open(package, 'w:xz') as archive:
                    data = identity.encode()
                    info = tarfile.TarInfo('.PKGINFO')
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
                (root / 'releases/fixture.json').write_text(json.dumps({'assets': [{
                    'name': package.name,
                    'sha256': hashlib.sha256(package.read_bytes()).hexdigest()}]}))
                output = root / 'output'
                result = subprocess.run([str(script), str(package), 'A' * 40, str(output)], capture_output=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(b'Expected official jms x86_64', result.stderr)
                self.assertFalse(output.exists())

    @unittest.skipUnless(os.environ.get('JMS_PORTABLE_ARCHIVE'), 'set JMS_PORTABLE_ARCHIVE for real-payload staging')
    def test_real_package_layout(self):
        archive = Path(os.environ['JMS_PORTABLE_ARCHIVE'])
        self.assertEqual(hashlib.sha256(archive.read_bytes()).hexdigest(), values('sha256sums')[0])
        with tempfile.TemporaryDirectory() as tmp:
            src, pkg = Path(tmp) / 'src', Path(tmp) / 'pkg'
            src.mkdir()
            with tarfile.open(archive) as tar:
                tar.extractall(src, filter='data')
            (src / 'com.jim608.jms.desktop').write_bytes((RECIPE / 'com.jim608.jms.desktop').read_bytes())
            subprocess.run(['bash', '-euc', 'source "$1"; srcdir=$2; pkgdir=$3; package', 'bash', str(RECIPE / 'PKGBUILD'), str(src), str(pkg)], check=True)
            self.assertEqual(os.readlink(pkg / 'usr/bin/jms'), '/opt/jms/jms')
            for original in (src / 'JMS').rglob('*'):
                if original.is_file():
                    self.assertEqual(original.read_bytes(), (pkg / 'opt/jms' / original.relative_to(src / 'JMS')).read_bytes())
            self.assertTrue(os.access(pkg / 'opt/jms/jms', os.X_OK))
            self.assertTrue((pkg / 'usr/share/icons/hicolor/512x512/apps/com.jim608.jms.png').is_file())
            self.assertTrue((pkg / 'usr/share/licenses/jms-bin/JMS_NATIVE_NOTICES.txt').is_file())
            self.assertFalse((pkg / 'etc').exists())
            self.assertFalse((pkg / 'home').exists())


if __name__ == '__main__':
    unittest.main()
