# stintly-data – Hinweise für Claude

Öffentliches Daten-Repo der iPhone-App Stintly. Die App lädt `data/races.json` über
`https://raw.githubusercontent.com/MausBlauXD/stintly-data/main/data/races.json`.
Jeder Push auf `main` ist sofort bei allen Nutzern – nur geprüfte Daten pushen.

## Wöchentliches Update (sparsam mit Tokens)

1. `python3 tools/weekly_check.py` – die Ausgabe ist die einzige Prüfliste (provisorische Zeiten der nächsten
   14 Tage, Serien mit bald auslaufendem Kalender, am ersten Montag im Monat zusätzlich `tools/watchlist.md`:
   Grello, Rexy, Kevin Estre und noch unveröffentlichte Kalender). Steht überall „keine“: fertig, nichts committen.
   Erledigte Punkte der Beobachtungsliste dort löschen.
2. Recherche nur mit Websuche (Standardmodus), höchstens 8 Suchen, bevorzugt offizielle Quellen. Nichts erfinden.
3. Nur `tools/generate_races.py` ändern (Stelle per `grep -n` finden). Zeiten als Ortszeit der Strecke,
   bestätigte Zeiten `confirmed=True`, unsichere `False` mit note „Startzeiten provisorisch“, Quelle in `sources`.
   Deutsch, Schweizer Schreibweise (ss statt ß).
4. `python3 tools/generate_races.py && python3 tools/validate_races.py` – muss „OK“ melden.
5. Hat sich ausser `updatedAt` nichts geändert: verwerfen, nicht committen.
6. Sonst committen und auf `main` pushen.

## Favoriten, Übersetzungen, Links, Kalender

- Favoriten (`ENTRANTS`): Grello, Rexy (AO Racing), Kévin Estre. In `EVENT_ENTRANTS` nur **bestätigte** Starts
  eintragen (Quelle als Kommentar); unbestätigte Pläne bleiben in `tools/watchlist.md`.
- Übersetzungen (en/fr/it) in `tools/i18n.py`. Neue Taglines, Sender-Hinweise, Notiz-Bausteine oder
  Session-Namen dort ergänzen – der Generator meldet fehlende als „Hinweis“ (App zeigt dann Deutsch).
- `LIVE_TIMING` nur mit geprüften Links (HTTP 200).
- Der Generator schreibt auch die Kalender-Abos `docs/calendar/<serie>.ics` – mitcommitten.

## Regeln

- Keine Logos ohne Lizenz, keine Tipps zum Umgehen von Geosperren.
- `docs/datenschutz.html` beschreibt, welche Daten anfallen – bei Änderungen an der App mitpflegen.
