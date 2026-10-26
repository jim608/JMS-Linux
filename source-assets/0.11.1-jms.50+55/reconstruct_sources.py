"""Offline reconstruction of locally downloaded exact corresponding source parts."""
import hashlib
import json
from pathlib import Path
import re

base = Path(__file__).resolve().parent
record = json.loads((base / 'sources.json').read_text(encoding='utf-8'))
for asset in record['assets']:
    name = asset['name']
    if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._+-]{0,179}', name):
        raise SystemExit('Unsafe source name')
    if len(asset['parts']) == 1 and asset['parts'][0]['name'] == name:
        path = base / name
        with path.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if path.stat().st_size != asset['size'] or digest != asset['sha256']:
            raise SystemExit('Whole source SHA/size differs')
        continue
    destination = base / name
    if destination.exists():
        raise SystemExit('Output exists; refusing overwrite')
    full = hashlib.sha256()
    with destination.open('xb') as output:
        for part in asset['parts']:
            if not re.fullmatch('[A-Za-z0-9][A-Za-z0-9._+-]{0,191}', part['name']):
                raise SystemExit('Unsafe part name')
            path = base / part['name']
            if path.is_symlink() or path.stat().st_size != part['size']:
                raise SystemExit('Source part size/type differs')
            with path.open('rb') as stream:
                if hashlib.file_digest(stream, 'sha256').hexdigest() != part['sha256']:
                    raise SystemExit('Source part SHA differs')
            with path.open('rb') as stream:
                while block := stream.read(1024**2):
                    full.update(block)
                    output.write(block)
    if destination.stat().st_size != asset['size'] or full.hexdigest() != asset['sha256']:
        raise SystemExit('Reconstructed source SHA/size differs; output is incomplete')
print('Exact source SHA256 and byte counts verified.')
