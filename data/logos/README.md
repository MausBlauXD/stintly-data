# Logos

Die App lädt Serien-Logos von `<Ordner von races.json>/logos/<id>.png` und speichert sie lokal.
Fehlt ein Logo, zeichnet die App ein Abzeichen in der Serienfarbe.

| Datei | Serie |
|---|---|
| `f1.png` | Formel 1 |
| `motogp.png` | MotoGP |
| `dtm.png` | DTM |
| `nls.png` | Nürburgring Langstrecken-Serie |
| `n24.png` | 24h Nürburgring |
| `wec.png` | Langstrecken-WM (WEC) |
| `fe.png` | Formel E |

- PNG, quadratisch oder breit, transparenter Hintergrund, mind. 256 px. Die App zeigt es auf weissem, abgerundetem Grund.
- Logos sind Markenzeichen: für den privaten Gebrauch okay, für den App Store braucht es eine Erlaubnis der Rechteinhaber.
- Alternativ ein Bild `logo-<id>` in `Stintly/Resources/Assets.xcassets` – das hat Vorrang.
