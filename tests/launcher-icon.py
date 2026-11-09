#!/usr/bin/env python3
"""iDrive app-drawer icon check (standard library only).

    python3 -I tests/launcher-icon.py --build        # rebuild iyt_app, then check source and package
    python3 -I tests/launcher-icon.py                # check source and the already built package
    python3 -I tests/launcher-icon.py --source-only  # check source/apps/iyt_app/launcher_icon.png only

Source icon: 140x140 8-bit RGBA PNG, transparent, only the brand colour, logo centred with 25-30 % free
space on every side and the proportions of the vector geometry in brand.js.
Package: every RHMI layout (package format and installed format, inside the .mgu and the .tgz) holds the
same bytes as the source icon and its application.json names that icon.
The Store catalogue graphic (apps/iyt_app/icon.png, iyt_app.png) is deliberately not looked at.
"""
import argparse
import hashlib
import json
import struct
import subprocess
import sys
import tarfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'source/apps/iyt_app'
DIST = ROOT / 'source/dist'
APP_ID = 'iyt_app'
ICON_NAME = APP_ID + '_icon.png'

SIZE = 140
MIN_MARGIN, MAX_MARGIN = 0.25, 0.30   # free space per side, fraction of the tile
CENTRE_TOLERANCE = 1                  # px, between opposite margins
ASPECT_TOLERANCE = 0.04               # relative, pixel rounding of a ~65 px logo
COLOUR_TOLERANCE = 2                  # per channel (encoder truncation)


def decode_png(data):
    """-> (width, height, rows of RGBA bytes). Accepts only 8-bit RGBA, non-interlaced PNG."""
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('not a PNG')
    pos, ihdr, idat = 8, None, []
    while pos < len(data):
        length, kind = struct.unpack('>I4s', data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + length]
        if zlib.crc32(kind + body) != struct.unpack('>I', data[pos + 8 + length:pos + 12 + length])[0]:
            raise ValueError('bad CRC in %s chunk' % kind.decode('ascii', 'replace'))
        if kind == b'IHDR':
            ihdr = struct.unpack('>IIBBBBB', body)
        elif kind == b'IDAT':
            idat.append(body)
        pos += 12 + length
    if ihdr is None:
        raise ValueError('no IHDR')
    width, height, depth, colour, _, _, interlace = ihdr
    if (depth, colour, interlace) != (8, 6, 0):
        raise ValueError('need 8-bit RGBA, not interlaced (bit depth %d, colour type %d, interlace %d)' % (depth, colour, interlace))
    raw = zlib.decompress(b''.join(idat))
    stride, rows, prev = width * 4, [], bytearray(width * 4)
    for y in range(height):
        kind, line = raw[y * (stride + 1)], bytearray(raw[y * (stride + 1) + 1:(y + 1) * (stride + 1)])
        for i in range(stride):
            a = line[i - 4] if i >= 4 else 0
            b = prev[i]
            c = prev[i - 4] if i >= 4 else 0
            if kind == 1:
                line[i] = (line[i] + a) & 255
            elif kind == 2:
                line[i] = (line[i] + b) & 255
            elif kind == 3:
                line[i] = (line[i] + (a + b) // 2) & 255
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
            elif kind != 0:
                raise ValueError('bad PNG filter %d' % kind)
        rows.append(line)
        prev = line
    return width, height, rows


def brand_geometry():
    """(colour, polygons) from the app's own brand.js, the single source of the logo."""
    script = 'const b=require(process.argv[1]);process.stdout.write(JSON.stringify({color:b.color,polygons:b.polygons}))'
    out = subprocess.run(['node', '-e', script, str(APP / 'brand.js')], stdout=subprocess.PIPE, check=True).stdout
    data = json.loads(out)
    colour = data['color'].lstrip('#')
    return tuple(int(colour[i:i + 2], 16) for i in (0, 2, 4)), data['polygons']


def check_icon(data, geometry):
    """List of problems with one icon file (empty when it is fine) and a one-line measurement."""
    colour, polygons = geometry
    try:
        width, height, rows = decode_png(data)
    except (ValueError, zlib.error) as error:
        return ['unreadable PNG: %s' % error], 'unreadable'
    if (width, height) != (SIZE, SIZE):
        return ['size is %dx%d, expected %dx%d' % (width, height, SIZE, SIZE)], '%dx%d' % (width, height)
    problems = []
    any_box = [width, height, -1, -1]      # any non-zero alpha, as [x0, y0, x1, y1]
    solid_box = [width, height, -1, -1]    # alpha >= 128: the geometric edge of the logo
    worst_colour = 0
    for y, row in enumerate(rows):
        for x in range(width):
            r, g, b, a = row[x * 4:x * 4 + 4]
            if a == 0:
                continue
            for box, hit in ((any_box, True), (solid_box, a >= 128)):
                if hit:
                    box[0], box[1], box[2], box[3] = min(box[0], x), min(box[1], y), max(box[2], x), max(box[3], y)
            worst_colour = max(worst_colour, abs(r - colour[0]), abs(g - colour[1]), abs(b - colour[2]))
    if solid_box[2] < 0:
        return ['icon is empty'], 'empty'
    for x, y in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1)):
        if rows[y][x * 4 + 3] != 0:
            problems.append('corner pixel (%d,%d) is not transparent' % (x, y))
    margins = {'left': solid_box[0], 'top': solid_box[1], 'right': width - 1 - solid_box[2], 'bottom': height - 1 - solid_box[3]}
    low, high = MIN_MARGIN * SIZE, MAX_MARGIN * SIZE
    for side, value in margins.items():
        if not low <= value <= high:
            problems.append('%s margin %d px (%.1f %%) is outside %d-%d %%' % (side, value, 100 * value / SIZE, MIN_MARGIN * 100, MAX_MARGIN * 100))
    if abs(margins['left'] - margins['right']) > CENTRE_TOLERANCE or abs(margins['top'] - margins['bottom']) > CENTRE_TOLERANCE:
        problems.append('logo is not centred (margins %s)' % margins)
    # soft edge pixels may sit one pixel beyond the geometric edge, nothing further out
    for index, side in enumerate(('left', 'top')):
        if solid_box[index] - any_box[index] > 1:
            problems.append('stray pixels beyond the %s edge of the logo' % side)
    for index, side in ((2, 'right'), (3, 'bottom')):
        if any_box[index] - solid_box[index] > 1:
            problems.append('stray pixels beyond the %s edge of the logo' % side)
    if worst_colour > COLOUR_TOLERANCE:
        problems.append('a pixel differs from the brand colour #%02x%02x%02x by %d' % (*colour, worst_colour))
    points = [q for polygon in polygons for q in polygon]
    expected = (max(q[0] for q in points) - min(q[0] for q in points)) / (max(q[1] for q in points) - min(q[1] for q in points))
    seen = (solid_box[2] - solid_box[0] + 1) / (solid_box[3] - solid_box[1] + 1)
    if abs(seen / expected - 1) > ASPECT_TOLERANCE:
        problems.append('logo aspect ratio %.3f differs from brand geometry %.3f' % (seen, expected))
    summary = '%dx%d, margins L%d T%d R%d B%d px (%.1f-%.1f %%), aspect %.3f (brand %.3f)' % (
        width, height, margins['left'], margins['top'], margins['right'], margins['bottom'],
        100 * min(margins.values()) / SIZE, 100 * max(margins.values()) / SIZE, seen, expected)
    return problems, summary


def package_icons(ver):
    """{label: bytes} for every icon copy in the built packages, and a list of structural problems."""
    found, problems = {}, []
    wanted = {
        '%s@%s.mgu' % (APP_ID, ver): {
            'package layout': 'source/rhmiData/variantGroups/Common/images/' + ICON_NAME,
            'installed layout': 'rhmiData/resources/' + ICON_NAME},
        '%s@%s.tgz' % (APP_ID, ver): {
            'package layout': 'package/rhmiData/variantGroups/Common/images/' + ICON_NAME},
    }
    manifests = {'.mgu': ('source/rhmiData/application.json', 'rhmiData/application.json'), '.tgz': ('package/rhmiData/application.json',)}
    for archive, members in wanted.items():
        path = DIST / archive
        if not path.is_file():
            problems.append('%s is missing (build it, or pass --build)' % path.relative_to(ROOT))
            continue
        with tarfile.open(path, 'r:gz') as tar:
            names = set(tar.getnames())
            for label, name in members.items():
                if name in names:
                    found['%s %s' % (archive, label)] = tar.extractfile(name).read()
                else:
                    problems.append('%s has no %s' % (archive, name))
            for name in names:   # a widget copy, when the app declares a start widget
                if name.endswith('_widget_icon.png'):
                    found['%s %s' % (archive, name)] = tar.extractfile(name).read()
            for name in manifests[path.suffix]:
                if name not in names:
                    problems.append('%s has no %s' % (archive, name))
                    continue
                entry = json.loads(tar.extractfile(name).read())['application']['entryPoints'][0]['icon']
                if entry != ICON_NAME:
                    problems.append('%s: %s names icon %r, expected %r' % (archive, name, entry, ICON_NAME))
    return found, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--build', action='store_true', help='rebuild the app package first')
    parser.add_argument('--source-only', action='store_true', help='skip the built package')
    args = parser.parse_args()

    failures = []

    def report(label, problems, detail=''):
        print('%s  %s%s' % ('FAIL' if problems else 'ok  ', label, ('  ' + detail) if detail else ''))
        for problem in problems:
            print('      - ' + problem)
        failures.extend('%s: %s' % (label, p) for p in problems)

    geometry = brand_geometry()
    source_path = APP / 'launcher_icon.png'
    if not source_path.is_file():
        report('source launcher_icon.png', ['file is missing'])
        return 1
    source = source_path.read_bytes()
    problems, summary = check_icon(source, geometry)
    report('source launcher_icon.png', problems, summary)
    if args.source_only:
        return 1 if failures else 0

    if args.build:
        subprocess.run([sys.executable, str(ROOT / 'source/kit/tools/build.py'), APP_ID], check=True, stdout=subprocess.DEVNULL)
    ver = json.loads((APP / 'app.json').read_text(encoding='utf-8'))['version']
    found, structure = package_icons(ver)
    report('package structure', structure)
    digest = hashlib.sha256(source).hexdigest()
    for label, data in sorted(found.items()):
        problems, summary = check_icon(data, geometry)
        if hashlib.sha256(data).hexdigest() != digest:
            problems.append('bytes differ from source launcher_icon.png')
        report(label, problems, summary)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
