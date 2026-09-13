# Komnata — pokój VR dla Meta Quest 3

Technologia: Blender 5.1 → glTF/GLB → A-Frame 1.8.0 / WebXR. Pokój 5 × 4 × 2,7 m, skala 1:1. Model stylizowany, z prostymi materiałami, bez zewnętrznych tekstur.

## Uruchomienie na Quest 3

Po pomyślnej publikacji przez GitHub Pages pokój jest dostępny pod **https://filipescu88.github.io/vr_room/**. Otwórz adres w Meta Quest Browser. Wybierz „Wejdź do VR” i zezwól na sesję VR. Lewy drążek porusza w kierunku patrzenia, prawy obraca widok o 30°. Wskaż drzwi laserem i naciśnij spust, aby je otworzyć — za nimi jest drugi, pusty pokój 4 × 4 m. Chwyt (grip) podnosi przedmiot i trzyma go w dłoni; puszczenie kładzie go na najbliższej powierzchni pod nim: blacie, siedzisku kanapy, półce, parapecie albo podłodze. Na stoliku kawowym leży karabinek — można go podnieść tak samo jak skrzynkę. Wysokość oczu jest kalibrowana przy wejściu do VR (domyślnie 1,8 m), a jeśli podłoga nie zgadza się z Twoją, wciśnij lewy drążek i wychyl go w górę lub w dół — wartość zostanie zapamiętana. Kolizje nie pozwalają przejść przez meble ani ściany. Teleportacji nie ma: poruszasz się drążkiem. Fizyczne przemieszczanie jest ograniczone Twoją rzeczywistą granicą przestrzeni Questa.

Strona jest publiczna i działa przez internet bez uruchamiania lokalnego komputera. W przeglądarce komputera działa podgląd 3D; pełny VR wymaga zgodnych gogli i przeglądarki.

## Publikacja zmian

GitHub Pages publikuje zawartość gałęzi `gh-pages` z katalogu głównego. Gałąź zawiera wyłącznie folder `dist` wyodrębniony poleceniem `git subtree split`. Źródłem w Settings → Pages jest **Deploy from a branch → gh-pages → / (root)**. Nie jest wymagany własny workflow GitHub Actions.

Po edycji wyeksportuj model do `dist/pokoj.glb`, zapisz zmiany w Git (commit), a następnie uruchom `pwsh -File scripts/Publish-Pages.ps1`. Skrypt sprawdza JavaScript i czysty stan repozytorium, wysyła źródła na `main`, a podgląd na `gh-pages`. Wymaga Git, Node.js i zalogowanego GitHub CLI (`gh`). GitHub automatycznie opublikuje nową zawartość tej gałęzi. Sam push na `main` ani zmiana pliku `.blend` nie aktualizują podglądu.

Z systemu bez PowerShella ten sam efekt dają trzy polecenia: `git push origin main`, `git subtree split --prefix=dist HEAD`, a potem `git push origin <wynik-splitu>:refs/heads/gh-pages`. Publikację z tego komputera wykonuje się kluczem SSH (push), a odczyt zostaje po HTTPS.

## Lokalny HTTPS w Windows

Wymagane: Node.js oraz PowerShell 7. Uruchom `Uruchom-VR.cmd` i wpisz w Queście adres HTTPS pokazany w oknie. Oba urządzenia muszą być w tej samej sieci. Zaakceptuj ostrzeżenie lokalnego certyfikatu. Ctrl+C zatrzymuje serwer. Skrypt automatycznie wykrywa adres komputera; można też podać go ręcznie: `pwsh -File scripts/Start-VR.ps1 -Address ADRES_IP`.

Jeśli zapora blokuje połączenie, `scripts/Allow-LAN.ps1` uruchomiony jako administrator dodaje ograniczoną regułę TCP 8443 dla lokalnej podsieci w profilu prywatnym. Sam serwer nie wymaga administratora. Po zmianie adresu IP istniejąca reguła może wymagać aktualizacji. Certyfikat i klucz powstają lokalnie w `.local-vr/` i nie trafiają do repozytorium. Konfiguracja lokalnego HTTPS nie jest potrzebna do korzystania z GitHub Pages.

Na komputerze poruszaj się klawiszami W/A/S/D lub strzałkami, przeciągaj widok myszą i korzystaj z czterech punktów widokowych („Za drzwiami" pokazuje nowy pokój). Kamera podglądu jest na wysokości 1,8 m. Ruch działa w kierunku patrzenia i zatrzymuje się na meblach oraz ścianach (kolizje liczone z brył otaczających modelu, promień ciała 0,26 m). Meble są statyczne; drzwi otwierają się na komendę, a skrzynka jest przenośna — odkładasz ją na blat albo siedzisko. To samodzielna scena WebXR, nie środowisko domowe systemu Meta Horizon.

## Edycja

Otwórz `Pokoj_VR.blend` w Blenderze. Obiekty mają polskie nazwy i oddzielne materiały. Eksportuj do `dist/pokoj.glb` przez File → Export → glTF 2.0, format GLB, bez kamer i świateł. Po zmianach ustawienia punktów teleportacji są w `dist/room.js` oraz znacznikach pierścieni w `dist/index.html`. Blender używa Z w górę; eksport GLB konwertuje do Y w górę.

`scripts/build_room.py` odtwarza model i podgląd; ponowne uruchomienie nadpisuje pliki wygenerowane. `podglad.png` to render Blendera — światło w przeglądarce jest uproszczone. `model-info.json` zawiera statystyki modelu.

Pokój za drzwiami, drzwi i skrzynka powstają bez Blendera: `python3 scripts/build_second_room.py` zapisuje `dist/models/za-drzwiami.glb`, `dist/models/drzwi.glb` i `dist/models/skrzynka.glb`. Skrypt używa wyłącznie biblioteki standardowej (wspólny zapis GLB jest w `scripts/glb_builder.py`), a kolory materiałów czyta z `dist/pokoj.glb`, żeby nowe elementy nie odróżniały się od reszty. Ściany są w nim osobnymi obiektami, bo kolizje liczą bryłę otaczającą każdy mesh — scalona geometria rozciągnięta nad przejściem zamurowałaby otwór i wnętrze pokoju. Oś obrotu drzwi to początek układu encji `#door` w `dist/index.html`, czyli zawias; skrzynka ma początek w środku podstawy, więc `y = 0` stawia ją na podłodze.

Karabinek pochodzi z osobnego repozytorium `filipescu88/blender` (skrypt dla Blendera `mohac_model.py`, wersja low-poly). `python3 scripts/build_carbine.py` odtwarza jego geometrię bez Blendera — te same bryły i parametry, bez fazowania krawędzi, scalone w dwa meshe (coyote i czarny). Model jest obrócony w pliku tak, że leży na boku, a jego początek układu leży w środku podstawy, dzięki czemu `y = 0,49` kładzie go na blacie stolika. Wersja „realistic” z tamtego repozytorium nie jest przenoszona: ma materiały proceduralne i wymagałaby Blendera.

Lita ściana przednia i dekoracyjne drzwi z `pokoj.glb` są ukrywane w czasie działania przez komponent `legacy-front-wall` (`dist/room.js`), a ich rolę przejmują nowe modele. To obejście braku Blendera: docelowo otwór drzwiowy powinien być wycięty w `Pokoj_VR.blend` i wyeksportowany do `pokoj.glb`, a ukrywanie usunięte. Komponent `player-body` buduje kolizje z modeli podanych w atrybucie `sources`, a bryły drzwi i skrzynki dolicza co klatkę (atrybut `dynamic`), bo te obiekty się przemieszczają. Wysokość oczu ustawia atrybut `eyeHeight` (domyślnie 1,8 m) — przy wejściu do VR jest kalibrowana do rzeczywistej pozycji głowy, a wciśnięty lewy drążek z wychyleniem pozwala ją poprawić i zapamiętuje wynik. Najmniejszą powierzchnię, na której wolno coś położyć (żeby filiżanka ani książka nie udawały blatu), określa `minSupport`.

Podgląd lokalny: `python -m http.server 8080 --directory dist`, następnie http://localhost:8080 na komputerze. Do VR na osobnym Queście używaj opublikowanego HTTPS; zwykły adres HTTP komputera w sieci lokalnej nie wystarcza.

Nie przeprowadzono fizycznego testu na goglach. Płynność, obsługę kontrolerów i skalę odczuwaną należy potwierdzić na urządzeniu.

Dokumentacja: https://aframe.io/docs/1.8.0/ oraz https://developers.meta.com/horizon/documentation/web/port-vr-xr/
