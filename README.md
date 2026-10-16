# Stintly – Renndaten

Öffentliche Termin- und Senderdaten für die iPhone-App **Stintly** (Rennkalender & Start-Erinnerungen).
Die App lädt `data/races.json` direkt von hier; Updates brauchen deshalb kein App-Update.

- `tools/generate_races.py` – einzige Quelle der Daten (Ortszeit + IANA-Zeitzone → UTC)
- `tools/validate_races.py` – Prüfung (Exit-Code 1 bei Fehlern)
- `tools/weekly_check.py` – Prüfliste fürs wöchentliche Update
- `data/races.json` – erzeugte Datei, nie von Hand ändern
- `data/logos/` – optionale Serienlogos (nur mit Lizenz)
- `docs/` – Support- und Datenschutzseite (GitHub Pages)

```bash
python3 tools/generate_races.py && python3 tools/validate_races.py
```

Stintly ist eine inoffizielle App und nicht mit Rennserien, Veranstaltern oder Sendern verbunden.
Alle Angaben ohne Gewähr. Kontakt: support.stintly@calileo.ch
