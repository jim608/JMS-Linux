#!/usr/bin/env bash
# Stage a signed local repository; does not upload, enroll keys, or change pacman.conf.
set -euo pipefail
if (( $# != 3 )); then
    echo "Usage: $0 RELEASE.pkg.tar.xz FULL_SIGNING_FINGERPRINT NEW_OUTPUT_DIRECTORY" >&2
    exit 2
fi
root=$(cd "$(dirname "$0")/.." && pwd)
package=$(realpath "$1")
key=$2
out=$3
[[ $key =~ ^[A-Fa-f0-9]{40}$ || $key =~ ^[A-Fa-f0-9]{64}$ ]] || { echo 'Use a full signing fingerprint' >&2; exit 2; }
[[ ! -e $out ]] || { echo 'Output must not exist; stage an atomic snapshot' >&2; exit 2; }
# Only published, checksum-pinned packages recorded in this checkout may be staged.
python3 - "$root/releases" "$package" <<'PYVERIFY'
import hashlib, json, sys, tarfile
from pathlib import Path
package = Path(sys.argv[2])
expected = {a['sha256'] for f in Path(sys.argv[1]).glob('*.json')
            for a in json.loads(f.read_text()).get('assets', [])
            if a['name'] == package.name and a['name'].endswith('.pkg.tar.xz')}
with package.open('rb') as stream:
    digest = hashlib.file_digest(stream, 'sha256').hexdigest()
if digest not in expected:
    raise SystemExit('Package name/checksum not found in reviewed release manifests')
# Read metadata directly: pacman -Qp does not support --print-format.
# Never source .PKGINFO as shell code or extract an archive into the host.
with tarfile.open(package) as archive:
    member = archive.getmember('.PKGINFO')
    if not member.isfile() or member.size > 1024 * 1024:
        raise SystemExit('Invalid package metadata')
    info = archive.extractfile(member).read().decode('utf-8')
fields = {}
for line in info.splitlines():
    if ' = ' in line:
        name, value = line.split(' = ', 1)
        fields.setdefault(name, []).append(value)
if fields.get('pkgname') != ['jms'] or fields.get('arch') != ['x86_64']:
    raise SystemExit('Expected official jms x86_64 package')
PYVERIFY
for command in repo-add gpg; do command -v "$command" >/dev/null; done
mkdir -p "$out/x86_64"
cp -- "$package" "$out/x86_64/"
cd "$out/x86_64"
file=$(basename "$package")
gpg --local-user "$key" --detach-sign "$file"
gpg --verify "$file.sig" "$file"
repo-add --sign --key "$key" jms.db.tar.gz "$file"
# Static web hosts may not preserve symlinks. Materialize both aliases and signatures.
for name in jms.db jms.db.sig jms.files jms.files.sig; do
    if [[ -L $name ]]; then
        cp --dereference "$name" "$name.tmp"
        mv -f "$name.tmp" "$name"
    fi
done
test -f jms.db.sig
gpg --verify jms.db.sig jms.db
printf 'Staged %s. Review and publish this snapshot only after authorization.\n' "$file"
