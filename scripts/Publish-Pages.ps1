$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $PSScriptRoot)
try {
 & node --check dist/room.js
 if ($LASTEXITCODE -ne 0) { throw 'Błąd JavaScript.' }
 $changes = & git status --porcelain
 if ($LASTEXITCODE -ne 0) { throw 'Nie można odczytać repozytorium.' }
 if ($changes) { throw 'Najpierw zapisz zmiany poleceniem git commit.' }
 $remote = & git remote get-url origin
 if ($remote -ne 'https://github.com/filipescu88/vr_room.git') { throw 'Nieoczekiwany adres origin. Sprawdź repozytorium docelowe.' }
 & git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin HEAD:main
 if ($LASTEXITCODE -ne 0) { throw 'Nie udało się wysłać źródeł.' }
 $pagesCommit = & git subtree split --prefix=dist HEAD
 if ($LASTEXITCODE -ne 0) { throw 'Nie udało się przygotować strony.' }
 & git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin "${pagesCommit}:refs/heads/gh-pages"
 if ($LASTEXITCODE -ne 0) { throw 'Nie udało się wysłać strony.' }
 Write-Host 'Pliki wysłane. Po ukończeniu publikacji: https://filipescu88.github.io/vr_room/'
} finally { Pop-Location }
