"""Generuje nowe assety bez Blendera: pokój za drzwiami, drzwi i skrzynkę.

Skrypt buduje geometrię i zapisuje pliki GLB przez wspólny moduł scripts/glb_builder.py
(tam jest zapis formatu i pomocnicze bryły). Kolory materiałów są odczytywane
z dist/pokoj.glb, żeby nowe elementy wyglądały identycznie jak istniejące.

Wynik:
  dist/models/za-drzwiami.glb  ściana przednia z otworem, nowy pokój 4 x 4 x 2,7 m
  dist/models/drzwi.glb        skrzydło z klamką, oś obrotu w zawiasie
  dist/models/skrzynka.glb     skrzynka do chwytania, oś w środku podstawy

Uruchomienie: python3 scripts/build_second_room.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glb_builder import (buduj_glb, materialy_z_pokoju, prostopadloscian, scal, walec)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'models')

# --- układ sceny (metry, glTF: Y w górę, Z w stronę nowego pokoju) ----------
POKOJ_A = {'x': (-2.5, 2.5), 'z': (-2.0, 2.0), 'y': (0.0, 2.7)}
SCIANA_Z = (2.00, 2.16)             # grubość ściany przedniej z drzwiami
DRZWI_X = (-2.16, -1.34)            # otwór: 0,82 m
DRZWI_Y = (0.0, 2.05)               # otwór: 2,05 m
POKOJ_B = {'x': (-3.75, 0.25), 'z': (2.16, 6.16), 'y': (0.0, 2.7)}   # 4 x 4 x 2,7 m
GRUBOSC = 0.16
NADPROZE = 0.12                     # grubość sufitu i płyty podłogowej
SLAT_W, SLAT_L, SLAT_PITCH = 0.245, 0.995, 0.25


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
    lampa = walec(0.24, 0.07, 'y', 24, (-1.75, 2.62, 4.16))
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
    rosetka = walec(0.035, 0.024, 'z', 20, (0.66, 1.02, -0.031))
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
    materialy = materialy_z_pokoju(ROOT)
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
