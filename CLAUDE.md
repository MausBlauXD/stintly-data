# stintly-data – Hinweise für Claude

Öffentliches Daten-Repo der iPhone-App Stintly. Die App lädt `data/races.json` über
`https://raw.githubusercontent.com/MausBlauXD/stintly-data/main/data/races.json`.
Jeder Push auf `main` ist sofort bei allen Nutzern – nur geprüfte Daten pushen.

## Wöchentliches Update (sparsam mit Tokens)

1. `python3 tools/weekly_check.py` – die Ausgabe ist die einzige Prüfliste (provisorische Zeiten der nächsten
   14 Tage, Serien mit bald auslaufendem Kalender). Steht überall „keine“: fertig, nichts committen.
2. Recherche nur mit Websuche (Standardmodus), höchstens 8 Suchen, bevorzugt offizielle Quellen. Nichts erfinden.
3. Nur `tools/generate_races.py` ändern (Stelle per `grep -n` finden). Zeiten als Ortszeit der Strecke,
   bestätigte Zeiten `confirmed=True`, unsichere `False` mit note „Startzeiten provisorisch“, Quelle in `sources`.
   Deutsch, Schweizer Schreibweise (ss statt ß).
4. `python3 tools/generate_races.py && python3 tools/validate_races.py` – muss „OK“ melden.
5. Hat sich ausser `updatedAt` nichts geändert: verwerfen, nicht committen.
6. Sonst committen und auf `main` pushen.

## Regeln

- Keine Logos ohne Lizenz, keine Tipps zum Umgehen von Geosperren.
- `docs/datenschutz.html` beschreibt, welche Daten anfallen – bei Änderungen an der App mitpflegen.
