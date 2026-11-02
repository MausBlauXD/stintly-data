# Stintly – Renndaten

Öffentliche Termindaten für die iPhone-App **Stintly** (Rennkalender & Start-Erinnerungen).
Die App lädt `data/races.json` direkt von hier; Updates brauchen deshalb kein App-Update.

- `tools/generate_races.py` – einzige Quelle der Daten (Ortszeit + IANA-Zeitzone → UTC)
- `tools/validate_races.py` – Prüfung (Exit-Code 1 bei Fehlern)
- `tools/weekly_check.py` – Prüfliste fürs wöchentliche Update
- `data/races.json` – erzeugte Datei, nie von Hand ändern
- `docs/` – Support- und Datenschutzseite (GitHub Pages)
- `docs/calendar/*.ics` – Kalender-Abos pro Serie, z. B. `https://mausblauxd.github.io/stintly-data/calendar/f1.ics`
- `tools/i18n.py` – Übersetzungen der Datentexte (Englisch, Französisch, Italienisch, Spanisch, Portugiesisch)

```bash
python3 tools/generate_races.py && python3 tools/validate_races.py
```

Stintly ist eine inoffizielle App und nicht mit Rennserien oder Veranstaltern verbunden.
Alle Angaben ohne Gewähr. Kontakt: support.stintly@calileo.ch
