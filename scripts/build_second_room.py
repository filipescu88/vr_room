"""Generuje nowe assety bez Blendera: pokój za drzwiami, drzwi i skrzynkę.

Skrypt pisze pliki GLB bezpośrednio (tylko biblioteka standardowa), dzięki czemu
nie wymaga Blendera ani żadnych pakietów. Kolory materiałów są odczytywane
z dist/pokoj.glb, żeby nowe elementy wyglądały identycznie jak istniejące.

Wynik:
  dist/models/za-drzwiami.glb  ściana przednia z otworem, nowy pokój 4 x 4 x 2,7 m
  dist/models/drzwi.glb        skrzydło z klamką, oś obrotu w zawiasie
  dist/models/skrzynka.glb     skrzynka do chwytania, oś w środku podstawy

Uruchomienie: python3 scripts/build_second_room.py
"""
import json
import math
import os
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'models')

# --- układ sceny (Metry, glTF: Y w górę, Z w stronę nowego pokoju) -----------
POKOJ_A = {'x': (-2.5, 2.5), 'z': (-2.0, 2.0), 'y': (0.0, 2.7)}
SCIANA_Z = (2.00, 2.16)             # grubość ściany przedniej z drzwiami
DRZWI_X = (-2.16, -1.34)            # otwór: 0,82 m
DRZWI_Y = (0.0, 2.05)               # otwór: 2,05 m
POKOJ_B = {'x': (-3.75, 0.25), 'z': (2.16, 6.16), 'y': (0.0, 2.7)}   # 4 x 4 x 2,7 m
GRUBOSC = 0.16
NADPROZE = 0.12                     # grubość sufitu i płyty podłogowej
SLAT_W, SLAT_L, SLAT_PITCH = 0.245, 0.995, 0.25

FALLBACK = {
    'Dąb': ((0.43, 0.24, 0.11, 1), 0.65, 0.0),
    'Ciepła biel': ((0.77, 0.76, 0.70, 1), 0.65, 0.0),
    'Grafit': ((0.035, 0.045, 0.052, 1), 0.65, 0.0),
    'Mosiądz': ((0.46, 0.31, 0.10, 1), 0.30, 0.65),
    'Ceramika': ((0.88, 0.85, 0.76, 1), 0.65, 0.0),
}


def materialy_z_pokoju():
    """Odczytuje kolory i parametry materiałów z istniejącego pokoj.glb."""
    sciezka = os.path.join(ROOT, 'dist', 'pokoj.glb')
    wynik = dict(FALLBACK)
    try:
        dane = open(sciezka, 'rb').read()
        off, dokument = 12, None
        while off < len(dane):
            dlugosc, typ = struct.unpack('<I4s', dane[off:off + 8])
            if typ == b'JSON':
                dokument = json.loads(dane[off + 8:off + 8 + dlugosc])
            off += 8 + dlugosc
        for mat in dokument.get('materials', []):
            pbr = mat.get('pbrMetallicRoughness', {})
            if mat.get('name') in wynik and 'baseColorFactor' in pbr:
                wynik[mat['name']] = (tuple(pbr['baseColorFactor']),
                                      pbr.get('roughnessFactor', 0.65),
                                      pbr.get('metallicFactor', 0.0))
        print('materiały odczytane z dist/pokoj.glb')
    except Exception as blad:                                  # pragma: no cover
        print('uwaga: nie odczytano pokoj.glb (%s), używam wartości domyślnych' % blad)
    return wynik


# --- geometria --------------------------------------------------------------
def prostopadloscian(lo, hi):
    """Zwraca (positions, normals, indices) pudełka od lo do hi (CCW na zewnątrz)."""
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


def walec(srodek, promien, wysokosc, os='y', segments=24):
    """Walec o zadanej osi, wygładzone boki i płaskie podstawy."""
    cx, cy, cz = srodek
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
            kol = [srodek_indeks, b, a] if znak > 0 else [srodek_indeks, a, b]
            indices.extend(kol)
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
    return positions, normals, indices


def cylinder_axis(srodek, promien, wysokosc, os, segments=24):
    """Walec w układzie osi, z przesunięciem środka."""
    positions, normals, indices = walec((0.0, 0.0, 0.0), promien, wysokosc, os, segments)
    cx, cy, cz = srodek
    for i in range(0, len(positions), 3):
        positions[i] += cx
        positions[i + 1] += cy
        positions[i + 2] += cz
    return positions, normals, indices


def scal(*czastki):
    """Skleja kilka geometrii w jedną (przesuwając indeksy)."""
    positions, normals, indices = [], [], []
    for p, n, idx in czastki:
        przesuniecie = len(positions) // 3
        positions.extend(p)
        normals.extend(n)
        indices.extend(i + przesuniecie for i in idx)
    return positions, normals, indices


# --- zapis GLB --------------------------------------------------------------
def buduj_glb(sciezka, obiekty, materialy, generator):
    """obiekty: [{'name': ..., 'nodes': [{'name':..., 'primitives': [(mat, geom)]}]}]"""
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

    dokument = {
        'asset': {'generator': generator, 'version': '2.0'},
        'scene': 0, 'scenes': [{'nodes': []}], 'nodes': [], 'meshes': [], 'materials': [],
    }
    kolejnosc_materialow = []
    for nazwa, (kolor, chropowatosc, metalicznosc) in materialy.items():
        kolejnosc_materialow.append(nazwa)
        dokument['materials'].append({
            'name': nazwa, 'doubleSided': True,
            'pbrMetallicRoughness': {'baseColorFactor': list(kolor),
                                     'roughnessFactor': round(chropowatosc, 4),
                                     'metallicFactor': round(metalicznosc, 4)},
        })
    indeks_materialu = {nazwa: i for i, nazwa in enumerate(kolejnosc_materialow)}

    def dodaj_mesh(nazwa, primitives_def):
        primitives = []
        for material, geometria in primitives_def:
            positions, normals, indices = geometria
            szerokosc = 2 if len(positions) // 3 < 65536 else 4
            fmt = '<%dH' % len(indices) if szerokosc == 2 else '<%dI' % len(indices)
            idx = dodaj_dane(struct.pack(fmt, *indices), 'SCALAR',
                             5123 if szerokosc == 2 else 5125, len(indices))
            lo = [min(positions[i::3]) for i in range(3)]
            hi = [max(positions[i::3]) for i in range(3)]
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
        """Węzeł z meshem i/lub dziećmi; dzieci dziedziczą jego układ (oś zawiasu)."""
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
    print('zapisano %s (%.1f kB)' % (os.path.relpath(sciezka, ROOT), len(glb) / 1024.0))


# --- sceny ------------------------------------------------------------------
def pokoj_za_drzwiami(materialy):
    """Ściany są osobnymi obiektami: kolizje liczą bryłę otaczającą, więc scalona
    geometria rozciągnięta nad przejściem zamurowałaby otwór i wnętrze pokoju."""
    biel, dab = 'Ciepła biel', 'Dąb'
    sciany_przednie = [
        ('Sciana_przednia_lewa', prostopadloscian((-3.91, POKOJ_B['y'][0], SCIANA_Z[0]), (DRZWI_X[0], POKOJ_B['y'][1], SCIANA_Z[1]))),
        ('Sciana_przednia_prawa', prostopadloscian((DRZWI_X[1], POKOJ_B['y'][0], SCIANA_Z[0]), (2.60, POKOJ_B['y'][1], SCIANA_Z[1]))),
        ('Nadproze', prostopadloscian((DRZWI_X[0], DRZWI_Y[1], SCIANA_Z[0]), (DRZWI_X[1], POKOJ_B['y'][1], SCIANA_Z[1]))),
    ]
    podloga = prostopadloscian((-3.91, -0.14, 2.10), (0.41, 0.0, 6.32))
    sufit = prostopadloscian((-3.91, POKOJ_B['y'][1], 2.10), (0.41, POKOJ_B['y'][1] + NADPROZE, 6.32))
    boki = [
        ('Sciana_nowa_lewa', prostopadloscian((-3.91, 0.0, POKOJ_B['z'][0]), (-3.75, 2.7, 6.32))),
        ('Sciana_nowa_prawa', prostopadloscian((0.25, 0.0, POKOJ_B['z'][0]), (0.41, 2.7, 6.32))),
        ('Sciana_nowa_tylna', prostopadloscian((-3.91, 0.0, 6.16), (0.41, 2.7, 6.32))),
    ]
    deski = []
    for i in range(16):
        x = -3.75 + 0.125 + i * SLAT_PITCH
        for j in range(4):
            z = POKOJ_B['z'][0] + 0.5 + j
            deski.append(prostopadloscian((x - SLAT_W / 2, -0.014, z - SLAT_L / 2),
                                          (x + SLAT_W / 2, 0.002, z + SLAT_L / 2)))
    lampa = scal(cylinder_axis((-1.75, 2.62, 4.16), 0.24, 0.07, 'y'))
    obiekty = [{'name': nazwa, 'primitives': [(biel, geometria)]}
               for nazwa, geometria in sciany_przednie + boki]
    obiekty += [
        {'name': 'Podloga_nowa', 'primitives': [(dab, podloga)]},
        {'name': 'Deski_nowe', 'primitives': [(dab, scal(*deski))]},   # poniżej progu kolizji
        {'name': 'Sufit_nowy', 'primitives': [(biel, sufit)]},
        {'name': 'Lampa_sufitowa', 'primitives': [('Ceramika', lampa)]},
    ]
    return obiekty


def drzwi(materialy):
    """Skrzydło i klamka w lokalnym układzie zawiasu — pozycję zawiasu ustawia
    atrybut position encji w dist/index.html (-2.16 0 2.08)."""
    skrzydlo = prostopadloscian((0.01, 0.0, -0.019), (0.81, 2.02, 0.019))
    rosetka = cylinder_axis((0.66, 1.02, -0.031), 0.035, 0.024, 'z', 20)
    dzwignia = prostopadloscian((0.66, 1.009, -0.043), (0.78, 1.031, -0.021))
    return [{'name': 'Drzwi', 'dzieci': [
        {'name': 'Skrzydlo', 'primitives': [('Dąb', skrzydlo)]},
        {'name': 'Klamka', 'primitives': [('Mosiądz', scal(rosetka, dzwignia))]},
    ]}]


def skrzynka(materialy):
    pudelko = prostopadloscian((-0.20, 0.0, -0.16), (0.20, 0.30, 0.16))
    okucia = []
    for y in (0.06, 0.24):
        okucia.append(prostopadloscian((-0.205, y - 0.012, -0.165), (0.205, y + 0.012, 0.165)))
        okucia.append(prostopadloscian((-0.165, y - 0.012, -0.165), (0.165, y + 0.012, 0.165)))
        okucia.append(prostopadloscian((-0.205, y - 0.012, -0.165), (0.205, y + 0.012, -0.135)))
        okucia.append(prostopadloscian((-0.205, y - 0.012, 0.135), (0.205, y + 0.012, 0.165)))
    return [{'name': 'Skrzynka', 'primitives': [('Dąb', pudelko), ('Grafit', scal(*okucia))]}]


def main():
    materialy = materialy_z_pokoju()
    uzywane = {k: v for k, v in materialy.items()
               if k in ('Ciepła biel', 'Dąb', 'Grafit', 'Mosiądz', 'Ceramika')}
    print('=== dist/models/za-drzwiami.glb ===')
    buduj_glb(os.path.join(OUT, 'za-drzwiami.glb'), pokoj_za_drzwiami(uzywane), uzywane,
              'Hermes build_second_room.py (bez Blendera)')
    print('=== dist/models/drzwi.glb ===')
    buduj_glb(os.path.join(OUT, 'drzwi.glb'), drzwi(uzywane), uzywane,
              'Hermes build_second_room.py (bez Blendera)')
    print('=== dist/models/skrzynka.glb ===')
    buduj_glb(os.path.join(OUT, 'skrzynka.glb'), skrzynka(uzywane), uzywane,
              'Hermes build_second_room.py (bez Blendera)')


if __name__ == '__main__':
    main()
