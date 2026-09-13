"""Model karabinka (Huglu Mohac 8" styl) — port skryptu bpy bez Blendera.

Źródło geometrii: repo filipescu88/blender, plik mohac_model.py (skrypt dla Blendera).
Ten skrypt odtwarza tę samą bryłę (prostopadłościany i walce, te same PARAMS)
i zapisuje dist/models/karabin.glb. Nie wymaga Blendera ani modułu bpy.

Różnice wobec oryginału:
- brak fazowania krawędzi (bevel) — bryły mają ostre krawędzie,
- geometria jest scalona w dwa meshe (coyote i czarny), żeby ograniczyć wywołania rysowania,
- początek układu modelu leży w środku podstawy, więc y = 0 stawia karabinek na blacie.

Uruchomienie: python3 scripts/build_carbine.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from glb_builder import (buduj_glb, materialy_z_pokoju, prostopadloscian, przeksztalc,
                         scal, walec, z_blendera, zakres)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dist', 'models')

# --- parametry przeniesione z mohac_model.py --------------------------------
PARAMS = {
    "total_length": 0.72,       # m, orientacyjna dlugosc calkowita
    "receiver_l": 0.26,
    "receiver_h": 0.075,
    "receiver_w": 0.042,
    "handguard_l": 0.24,
    "handguard_h": 0.058,
    "handguard_w": 0.045,
    "barrel_l": 0.10,
    "barrel_d": 0.018,
    "suppressor_l": 0.19,
    "suppressor_d": 0.036,
    "stock_l": 0.22,
    "grip_h": 0.11,
    "mag_h": 0.16,
    "mag_angle": 12,            # stopnie, pochylenie magazynka
    "color_coyote": (0.55, 0.40, 0.20, 1.0),
    "color_black": (0.02, 0.02, 0.02, 1.0),
}
SCALE = PARAMS["total_length"] / 0.72
COYOTE, BLACK = 'Coyote', 'GunBlack'
OBROT_LEZENIA = (math.radians(-90), 0, 0)   # karabinek leży na boku (boki na boki)
CZASTKI = []                     # (materiał, geometria w układzie Blendera)


def pudelko(size, loc, rot=(0, 0, 0), material=BLACK):
    """Odpowiednik box() z mohac_model.py: rozmiar, położenie i obrót Eulera XYZ."""
    sx, sy, sz = size
    geometria = prostopadloscian((-sx / 2, -sy / 2, -sz / 2), (sx / 2, sy / 2, sz / 2))
    CZASTKI.append((material, przeksztalc(geometria, rot, loc)))


def walec_b(promien, dlugosc, loc, rot=(0, 0, 0), verts=32, material=BLACK):
    """Odpowiednik cylinder() z mohac_model.py (walec wzdłuż osi Z)."""
    geometria = walec(promien, dlugosc, os='z', segments=verts)
    CZASTKI.append((material, przeksztalc(geometria, rot, loc)))


def buduj():
    P = PARAMS
    s = SCALE
    x_handguard_c = 0.155 * s
    x_receiver_c = -0.09 * s
    x_stock_c = -0.28 * s

    # HANDGUARD + sloty M-LOK (góra i dół)
    pudelko((P["handguard_l"], P["handguard_w"], P["handguard_h"]),
            (x_handguard_c, 0, 0.005), material=COYOTE)
    for i in range(6):
        x = x_handguard_c - P["handguard_l"] / 2 + 0.035 + i * 0.028
        pudelko((0.014, P["handguard_w"] + 0.004, 0.012), (x, 0, 0.005 + 0.014))
        pudelko((0.014, 0.016, P["handguard_h"] + 0.004), (x, 0, 0.005 - P["handguard_h"] / 2))

    # szyna picatinny z zębami
    pudelko((P["handguard_l"] + P["receiver_l"], 0.022, 0.008),
            ((x_handguard_c + x_receiver_c) / 2, 0, 0.005 + P["handguard_h"] / 2 + 0.006),
            material=COYOTE)
    for i in range(18):
        x = x_receiver_c - 0.10 + i * 0.021
        pudelko((0.010, 0.022, 0.004), (x, 0, 0.005 + P["handguard_h"] / 2 + 0.012),
                material=COYOTE)

    # komora zamkowa, okno wyrzutowe, gniazdo magazynka
    pudelko((P["receiver_l"], P["receiver_w"], P["receiver_h"]), (x_receiver_c, 0, -0.01),
            material=COYOTE)
    pudelko((0.05, P["receiver_w"] + 0.004, 0.028), (x_receiver_c + 0.06, 0, -0.004))
    pudelko((0.05, 0.036, 0.03), (x_receiver_c - 0.02, 0, -0.05))

    # magazynek pochylony i jego podstawa
    a = math.radians(P["mag_angle"])
    pudelko((0.028, 0.03, P["mag_h"]),
            (x_receiver_c - 0.045, 0, -0.05 - P["mag_h"] / 2 + 0.02), rot=(a, 0, 0))
    pudelko((0.034, 0.036, 0.014),
            (x_receiver_c - 0.045 - math.sin(a) * P["mag_h"] / 2, 0,
             -0.05 - P["mag_h"] + 0.015 + math.cos(a) * 0.007), rot=(a, 0, 0))

    # chwyt pistoletowy, spust i kabłąk
    grip_a = math.radians(20)
    pudelko((0.034, 0.03, P["grip_h"]),
            (x_receiver_c - 0.085, 0, -0.045 - P["grip_h"] / 2 + 0.02), rot=(-grip_a, 0, 0))
    pudelko((0.06, 0.024, 0.006), (x_receiver_c - 0.03, 0, -0.062))
    pudelko((0.008, 0.010, 0.026), (x_receiver_c - 0.028, 0, -0.05))

    # przyrządy celownicze
    pudelko((0.030, 0.026, 0.024),
            (x_receiver_c + 0.02, 0, 0.005 + P["handguard_h"] / 2 + 0.024))
    pudelko((0.016, 0.020, 0.030),
            (x_handguard_c + P["handguard_l"] / 2 - 0.03, 0,
             0.005 + P["handguard_h"] / 2 + 0.026))

    # lufa i tłumik z pierścieniami
    barrel_x = x_handguard_c + P["handguard_l"] / 2 + P["barrel_l"] / 2
    walec_b(P["barrel_d"] / 2, P["barrel_l"], (barrel_x, 0, 0.0), rot=(0, math.pi / 2, 0))
    sup_c = barrel_x + P["barrel_l"] / 2 + P["suppressor_l"] / 2 - 0.01
    walec_b(P["suppressor_d"] / 2, P["suppressor_l"], (sup_c, 0, 0.0),
            rot=(0, math.pi / 2, 0), verts=48)
    for i in range(9):
        x = sup_c - P["suppressor_l"] / 2 + 0.018 + i * (P["suppressor_l"] - 0.036) / 8
        walec_b(P["suppressor_d"] / 2 + 0.0016, 0.006, (x, 0, 0),
                rot=(0, math.pi / 2, 0), verts=24)

    # kolba teleskopowa: rura, ramię, stopka, elementy szkieletu
    walec_b(0.014, 0.10, (x_receiver_c - P["receiver_l"] / 2 - 0.05, 0, -0.008),
            rot=(0, math.pi / 2, 0))
    pudelko((0.13, 0.014, 0.05), (x_stock_c + 0.02, 0, -0.028))
    pudelko((0.020, 0.030, 0.095), (x_stock_c - 0.05, 0, -0.035),
            rot=(0, 0, math.radians(-6)))
    pudelko((0.05, 0.020, 0.018), (x_stock_c - 0.03, 0, -0.075))
    pudelko((0.05, 0.020, 0.016), (x_stock_c - 0.03, 0, 0.002))
    for i in range(3):
        pudelko((0.030, 0.016, 0.020), (x_stock_c + 0.01 + i * 0.035, 0, -0.055))


def main():
    buduj()
    grupy = {}
    for material, geometria in CZASTKI:
        grupy.setdefault(material, []).append(geometria)
    # układ Blendera (Z w górę) -> glTF (Y w górę)
    scalone = {material: z_blendera(scal(*czastki)) for material, czastki in grupy.items()}
    # karabinek ma leżeć na boku (boki na boki), więc obracamy go o -90° wokół osi lufy
    scalone = {material: przeksztalc(g, OBROT_LEZENIA) for material, g in scalone.items()}
    lo = [min(zakres(g)[0][i] for g in scalone.values()) for i in range(3)]
    hi = [max(zakres(g)[1][i] for g in scalone.values()) for i in range(3)]
    przesuniecie = (-(lo[0] + hi[0]) / 2.0, -lo[1], -(lo[2] + hi[2]) / 2.0)
    finalne = {material: przeksztalc(g, (0, 0, 0), przesuniecie)
               for material, g in scalone.items()}
    lo2 = [min(zakres(g)[0][i] for g in finalne.values()) for i in range(3)]
    hi2 = [max(zakres(g)[1][i] for g in finalne.values()) for i in range(3)]
    print('karabinek: dlugosc %.3f m, wysokosc %.3f m, szerokosc %.3f m'
          % (hi2[0] - lo2[0], hi2[1] - lo2[1], hi2[2] - lo2[2]))
    print('podstawa w y = %.3f, srodek w x = %.3f, z = %.3f'
          % (lo2[1], (lo2[0] + hi2[0]) / 2, (lo2[2] + hi2[2]) / 2))
    materialy = materialy_z_pokoju(ROOT)
    uzywane = {k: materialy[k] for k in (COYOTE, BLACK)}
    obiekty = [{'name': 'Karabin',
                'primitives': [(material, finalne[material]) for material in (COYOTE, BLACK)]}]
    buduj_glb(os.path.join(OUT, 'karabin.glb'), obiekty, uzywane,
              'Hermes build_carbine.py (port mohac_model.py, bez Blendera)')


if __name__ == '__main__':
    main()
