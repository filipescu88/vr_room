# Komnata — pokój VR dla Meta Quest 3

Technologia: Blender 5.1 → glTF/GLB → A-Frame 1.8.0 / WebXR. Pokój 5 × 4 × 2,7 m, skala 1:1. Model stylizowany, z prostymi materiałami, bez zewnętrznych tekstur.

## Uruchomienie na Quest 3

Po pomyślnej publikacji przez GitHub Pages pokój jest dostępny pod **https://filipescu88.github.io/vr_room/**. Otwórz adres w Meta Quest Browser. Wybierz „Wejdź do VR” i zezwól na sesję VR. Lewy drążek porusza w kierunku patrzenia, prawy obraca widok o 30°. Kolizje nie pozwalają przejść przez meble ani ściany. Możesz też wskazać kontrolerem jasny krąg i nacisnąć spust, aby teleportować się. Fizyczne przemieszczanie jest ograniczone Twoją rzeczywistą granicą przestrzeni Questa.

Strona jest publiczna i działa przez internet bez uruchamiania lokalnego komputera. W przeglądarce komputera działa podgląd 3D; pełny VR wymaga zgodnych gogli i przeglądarki.

## Publikacja zmian

GitHub Pages publikuje zawartość gałęzi `gh-pages` z katalogu głównego. Gałąź zawiera wyłącznie folder `dist` wyodrębniony poleceniem `git subtree split`. Źródłem w Settings → Pages jest **Deploy from a branch → gh-pages → / (root)**. Nie jest wymagany własny workflow GitHub Actions.

Po edycji wyeksportuj model do `dist/pokoj.glb`, zapisz zmiany w Git (commit), a następnie uruchom `pwsh -File scripts/Publish-Pages.ps1`. Skrypt sprawdza JavaScript i czysty stan repozytorium, wysyła źródła na `main`, a podgląd na `gh-pages`. Wymaga Git, Node.js i zalogowanego GitHub CLI (`gh`). GitHub automatycznie opublikuje nową zawartość tej gałęzi. Sam push na `main` ani zmiana pliku `.blend` nie aktualizują podglądu.

## Lokalny HTTPS w Windows

Wymagane: Node.js oraz PowerShell 7. Uruchom `Uruchom-VR.cmd` i wpisz w Queście adres HTTPS pokazany w oknie. Oba urządzenia muszą być w tej samej sieci. Zaakceptuj ostrzeżenie lokalnego certyfikatu. Ctrl+C zatrzymuje serwer. Skrypt automatycznie wykrywa adres komputera; można też podać go ręcznie: `pwsh -File scripts/Start-VR.ps1 -Address ADRES_IP`.

Jeśli zapora blokuje połączenie, `scripts/Allow-LAN.ps1` uruchomiony jako administrator dodaje ograniczoną regułę TCP 8443 dla lokalnej podsieci w profilu prywatnym. Sam serwer nie wymaga administratora. Po zmianie adresu IP istniejąca reguła może wymagać aktualizacji. Certyfikat i klucz powstają lokalnie w `.local-vr/` i nie trafiają do repozytorium. Konfiguracja lokalnego HTTPS nie jest potrzebna do korzystania z GitHub Pages.

Na komputerze poruszaj się klawiszami W/A/S/D lub strzałkami, przeciągaj widok myszą i korzystaj z punktów widokowych. Ruch działa w kierunku patrzenia i zatrzymuje się na meblach oraz ścianach (kolizje liczone z brył otaczających modelu, promień ciała 0,26 m). Dostępne są też trzy miejsca teleportacji. Meble są statyczne; drzwi są dekoracyjne. To samodzielna scena WebXR, nie środowisko domowe systemu Meta Horizon.

## Edycja

Otwórz `Pokoj_VR.blend` w Blenderze. Obiekty mają polskie nazwy i oddzielne materiały. Eksportuj do `dist/pokoj.glb` przez File → Export → glTF 2.0, format GLB, bez kamer i świateł. Po zmianach ustawienia punktów teleportacji są w `dist/room.js` oraz znacznikach pierścieni w `dist/index.html`. Blender używa Z w górę; eksport GLB konwertuje do Y w górę.

`scripts/build_room.py` odtwarza model i podgląd; ponowne uruchomienie nadpisuje pliki wygenerowane. `podglad.png` to render Blendera — światło w przeglądarce jest uproszczone. `model-info.json` zawiera statystyki modelu.

Podgląd lokalny: `python -m http.server 8080 --directory dist`, następnie http://localhost:8080 na komputerze. Do VR na osobnym Queście używaj opublikowanego HTTPS; zwykły adres HTTP komputera w sieci lokalnej nie wystarcza.

Nie przeprowadzono fizycznego testu na goglach. Płynność, obsługę kontrolerów i skalę odczuwaną należy potwierdzić na urządzeniu.

Dokumentacja: https://aframe.io/docs/1.8.0/ oraz https://developers.meta.com/horizon/documentation/web/port-vr-xr/
