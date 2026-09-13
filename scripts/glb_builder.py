"""Wspólny zapis i geometria GLB dla generatorów projektu vr_room.

Tylko biblioteka standardowa — żadnych pakietów ani Blendera.
Układ docelowy plików to glTF: Y w górę, Z w stronę nowego pokoju.
Funkcje geometrii budują w układzie glTF, a `z_blendera` konwertuje
geometrię zbudowaną w układzie Blendera (Z w górę), czym można przenieść
skrypt pisany pod bpy bez instalowania Blendera.
"""
import json
import math
import os
import struct

FALLBACK_MATERIALS = {
    'Dąb': ((0.43, 0.24, 0.11, 1), 0.65, 0.0),
    'Ciepła biel': ((0.77, 0.76, 0.70, 1), 0.65, 0.0),
    'Grafit': ((0.035, 0.045, 0.052, 1), 0.65, 0.0),
    'Mosiądz': ((0.46, 0.31, 0.10, 1), 0.30, 0.65),
    'Ceramika': ((0.88, 0.85, 0.76, 1), 0.65, 0.0),
    'Coyote': ((0.55, 0.40, 0.20, 1), 0.60, 0.10),
    'GunBlack': ((0.02, 0.02, 0.02, 1), 0.45, 0.40),
}


def wczytaj_scene_gltf(sciezka):
    """Zwraca (dokument JSON, dane binarne) z pliku GLB."""
    dane = open(sciezka, 'rb').read()
    off, dokument, binarnie = 12, None, b''
    while off < len(dane):
        dlugosc, typ = struct.unpack('<I4s', dane[off:off + 8])
        if typ == b'JSON':
            dokument = json.loads(dane[off + 8:off + 8 + dlugosc])
        elif typ.startswith(b'BIN'):
            binarnie = dane[off + 8:off + 8 + dlugosc]
        off += 8 + dlugosc
    return dokument, binarnie


def materialy_z_pokoju(katalog_korzenia):
    """Kolory i parametry materiałów z dist/pokoj.glb, żeby nic się nie odróżniało."""
    sciezka = os.path.join(katalog_korzenia, 'dist', 'pokoj.glb')
    wynik = dict(FALLBACK_MATERIALS)
    try:
        dokument, _ = wczytaj_scene_gltf(sciezka)
        for mat in dokument.get('materials', []):
            pbr = mat.get('pbrMetallicRoughness', {})
            if mat.get('name') in wynik and 'baseColorFactor' in pbr:
                wynik[mat['name']] = (tuple(pbr['baseColorFactor']),
                                      pbr.get('roughnessFactor', 0.65),
                                      pbr.get('metallicFactor', 0.0))
    except Exception as blad:                                          # pragma: no cover
        print('uwaga: nie odczytano pokoj.glb (%s), używam wartości domyślnych' % blad)
    return wynik


# --- geometria (układ glTF) -------------------------------------------------
def prostopadloscian(lo, hi):
    """Pudełko od lo do hi; trójkąty zwrócone na zewnątrz (CCW)."""
    x0, y0, z0 = lo
    x1, y1, z1 = hi
    sciany = [
        ((1, 0, 0), [(x1, y0, z1), (x1, y0, z0), (x1, y1, z0), (x1, y1, z1)]),
        ((-1, 0, 0), [(x0, y0, z0), (x0, y0, z1), (x0, y1, z1), (x0, y1, z0)]),
        ((0, 1, 0), [(x0, y1, z1), (x1, y1, z1), (x1, y1, z0), (x0, y1, z0)]),
        ((0, -1, 0), [(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)]),
        ((0, 0, 1), [(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]),
        ((0, 0, -1), [(x1, y0, z0), (x0, y0, z0), (x0, y1, z0), (x1, y1, z0)]),
    ]
    positions, normals, indices = [], [], []
    for normal, punkty in sciany:
        baza = len(positions) // 3
        for punkt in punkty:
            positions.extend(punkt)
            normals.extend(normal)
        indices.extend([baza, baza + 1, baza + 2, baza, baza + 2, baza + 3])
    return positions, normals, indices


def walec(promien, wysokosc, os='y', segments=24, srodek=(0.0, 0.0, 0.0)):
    """Walec o zadanej osi: wygładzone boki, płaskie podstawy."""
    positions, normals, indices = [], [], []
    polowa = wysokosc / 2.0
    pierscienie = []
    for i in range(segments + 1):
        kat = 2.0 * math.pi * i / segments
        px, pz = math.cos(kat), math.sin(kat)
        for t in (-polowa, polowa):
            positions.extend((px * promien, t, pz * promien))
            normals.extend((px, 0.0, pz))
        pierscienie.append((i * 2, i * 2 + 1))
    for i in range(segments):
        a, b = pierscienie[i], pierscienie[i + 1]
        indices.extend([a[0], a[1], b[1], a[0], b[1], b[0]])
    for znak, t in ((1, polowa), (-1, -polowa)):
        srodek_indeks = len(positions) // 3
        positions.extend((0.0, t, 0.0))
        normals.extend((0.0, znak, 0.0))
        pierwszy = len(positions) // 3
        for i in range(segments + 1):
            kat = 2.0 * math.pi * i / segments
            positions.extend((math.cos(kat) * promien, t, math.sin(kat) * promien))
            normals.extend((0.0, znak, 0.0))
        for i in range(segments):
            a, b = pierwszy + i, pierwszy + i + 1
            indices.extend([srodek_indeks, b, a] if znak > 0 else [srodek_indeks, a, b])
    if os != 'y':
        obrocone_p, obrocone_n = [], []
        for i in range(0, len(positions), 3):
            px, py, pz = positions[i:i + 3]
            nx, ny, nz = normals[i:i + 3]
            if os == 'z':                      # obrót +90° wokół X
                obrocone_p.extend((px, -pz, py))
                obrocone_n.extend((nx, -nz, ny))
            elif os == 'x':                    # obrót +90° wokół Z
                obrocone_p.extend((-py, px, pz))
                obrocone_n.extend((-ny, nx, nz))
        positions, normals = obrocone_p, obrocone_n
    cx, cy, cz = srodek
    for i in range(0, len(positions), 3):
        positions[i] += cx
        positions[i + 1] += cy
        positions[i + 2] += cz
    return positions, normals, indices


def scal(*czastki):
    """Skleja geometrie w jedną (przesuwając indeksy)."""
    positions, normals, indices = [], [], []
    for p, n, idx in czastki:
        przesuniecie = len(positions) // 3
        positions.extend(p)
        normals.extend(n)
        indices.extend(i + przesuniecie for i in idx)
    return positions, normals, indices


def przeksztalc(geometria, obrot=(0.0, 0.0, 0.0), przesuniecie=(0.0, 0.0, 0.0)):
    """Obrót Eulera XYZ (radiany, jak w Blenderze: X, potem Y, potem Z) i przesunięcie."""
    positions, normals, indices = geometria
    rx, ry, rz = obrot
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    macierz = [
        [cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx],
        [sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx],
        [-sy, cy * sx, cy * cx],
    ]
    tx, ty, tz = przesuniecie
    nowe_p, nowe_n = [], []
    for i in range(0, len(positions), 3):
        px, py, pz = positions[i], positions[i + 1], positions[i + 2]
        nowe_p.extend((macierz[0][0] * px + macierz[0][1] * py + macierz[0][2] * pz + tx,
                       macierz[1][0] * px + macierz[1][1] * py + macierz[1][2] * pz + ty,
                       macierz[2][0] * px + macierz[2][1] * py + macierz[2][2] * pz + tz))
    for i in range(0, len(normals), 3):
        nx, ny, nz = normals[i], normals[i + 1], normals[i + 2]
        nowe_n.extend((macierz[0][0] * nx + macierz[0][1] * ny + macierz[0][2] * nz,
                       macierz[1][0] * nx + macierz[1][1] * ny + macierz[1][2] * nz,
                       macierz[2][0] * nx + macierz[2][1] * ny + macierz[2][2] * nz))
    return nowe_p, nowe_n, list(indices)


def z_blendera(geometria):
    """Układ Blendera (Z w górę) -> glTF (Y w górę): (x, y, z) -> (x, z, -y)."""
    positions, normals, indices = geometria
    nowe_p, nowe_n = [], []
    for i in range(0, len(positions), 3):
        nowe_p.extend((positions[i], positions[i + 2], -positions[i + 1]))
    for i in range(0, len(normals), 3):
        nowe_n.extend((normals[i], normals[i + 2], -normals[i + 1]))
    return nowe_p, nowe_n, list(indices)


def zakres(geometria):
    """(min, max) współrzędnych geometrii."""
    positions = geometria[0]
    lo = [min(positions[i::3]) for i in range(3)]
    hi = [max(positions[i::3]) for i in range(3)]
    return lo, hi


def przesun_do_podstawy(geometria, wysrodkuj=True):
    """Przesuwa geometrię tak, by środek podstawy był w początku układu (y = 0)."""
    lo, hi = zakres(geometria)
    dx = -(lo[0] + hi[0]) / 2.0 if wysrodkuj else 0.0
    dz = -(lo[2] + hi[2]) / 2.0 if wysrodkuj else 0.0
    return przeksztalc(geometria, (0.0, 0.0, 0.0), (dx, -lo[1], dz))


# --- zapis GLB --------------------------------------------------------------
def buduj_glb(sciezka, obiekty, materialy, generator):
    """obiekty: [{'name':..., 'przesuniecie': (x,y,z)?, 'primitives': [(mat, geom)]?,
                  'dzieci': [...]?}]"""
    binarnie = bytearray()
    bufor_views, accessors = [], []

    def dodaj_dane(dane, typ, komponent, ile, minmax=False):
        while len(binarnie) % 4:
            binarnie.append(0)
        offset = len(binarnie)
        binarnie.extend(dane)
        bufor_views.append({'buffer': 0, 'byteOffset': offset, 'byteLength': len(dane)})
        opis = {'bufferView': len(bufor_views) - 1, 'componentType': komponent,
                'count': ile, 'type': typ}
        if minmax:
            opis['min'], opis['max'] = minmax
        accessors.append(opis)
        return len(accessors) - 1

    dokument = {'asset': {'generator': generator, 'version': '2.0'},
                'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [],
                'materials': []}
    kolejnosc = []
    for nazwa, (kolor, chropowatosc, metalicznosc) in materialy.items():
        kolejnosc.append(nazwa)
        dokument['materials'].append({
            'name': nazwa, 'doubleSided': True,
            'pbrMetallicRoughness': {'baseColorFactor': list(kolor),
                                     'roughnessFactor': round(chropowatosc, 4),
                                     'metallicFactor': round(metalicznosc, 4)},
        })
    indeks_materialu = {nazwa: i for i, nazwa in enumerate(kolejnosc)}

    def dodaj_mesh(nazwa, primitives_def):
        primitives = []
        for material, geometria in primitives_def:
            positions, normals, indices = geometria
            szerokosc = 2 if len(positions) // 3 < 65536 else 4
            fmt = '<%dH' % len(indices) if szerokosc == 2 else '<%dI' % len(indices)
            idx = dodaj_dane(struct.pack(fmt, *indices), 'SCALAR',
                             5123 if szerokosc == 2 else 5125, len(indices))
            lo, hi = zakres(geometria)
            pos = dodaj_dane(struct.pack('<%df' % len(positions), *positions), 'VEC3',
                             5126, len(positions) // 3, (lo, hi))
            nor = dodaj_dane(struct.pack('<%df' % len(normals), *normals), 'VEC3',
                             5126, len(normals) // 3)
            primitives.append({'attributes': {'POSITION': pos, 'NORMAL': nor}, 'indices': idx,
                               'material': indeks_materialu[material], 'mode': 4})
            print('   %-24s %6d trójkątów, materiał %s'
                  % (nazwa, len(indices) // 3, material))
        dokument['meshes'].append({'name': nazwa, 'primitives': primitives})
        return len(dokument['meshes']) - 1

    def dodaj_wezel(obiekt):
        wezel = {'name': obiekt['name']}
        if obiekt.get('przesuniecie'):
            wezel['translation'] = list(obiekt['przesuniecie'])
        if obiekt.get('primitives'):
            wezel['mesh'] = dodaj_mesh(obiekt['name'], obiekt['primitives'])
        if obiekt.get('dzieci'):
            wezel['children'] = [dodaj_wezel(dziecko) for dziecko in obiekt['dzieci']]
        dokument['nodes'].append(wezel)
        return len(dokument['nodes']) - 1

    for obiekt in obiekty:
        dokument['scenes'][0]['nodes'].append(dodaj_wezel(obiekt))

    while len(binarnie) % 4:
        binarnie.append(0)
    dokument['buffers'] = [{'byteLength': len(binarnie)}]
    dokument['bufferViews'] = bufor_views
    dokument['accessors'] = accessors
    tekst = json.dumps(dokument, ensure_ascii=False, separators=(',', ':')).encode('utf8')
    tekst += b' ' * ((4 - len(tekst) % 4) % 4)
    glb = struct.pack('<4sII', b'glTF', 2, 12 + 8 + len(tekst) + 8 + len(binarnie))
    glb += struct.pack('<I4s', len(tekst), b'JSON') + tekst
    glb += struct.pack('<I4s', len(binarnie), b'BIN\x00') + bytes(binarnie)
    os.makedirs(os.path.dirname(sciezka), exist_ok=True)
    open(sciezka, 'wb').write(glb)
    print('zapisano %s (%.1f kB)' % (os.path.relpath(sciezka, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), len(glb) / 1024.0))
