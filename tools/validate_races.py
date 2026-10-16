#!/usr/bin/env python3
"""Prüft races.json. Exit-Code 1 bei Fehlern, Warnungen nur als Ausgabe.

    python3 tools/validate_races.py [pfad/zu/races.json]
"""
import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_PATH = ROOT / "data" / "races.json"

CHANNEL_KINDS = {"freeTV", "freeStream", "payTV", "payStream"}
SESSION_KINDS = {"practice", "qualifying", "sprint", "race"}
START_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
CC_RE = re.compile(r"^[A-Z]{2}$")


def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    errors, warnings = [], []

    def err(msg):
        errors.append(msg)

    def need(obj, keys, where):
        for k in keys:
            if k not in obj or obj[k] is None or obj[k] == "":
                err(f"{where}: Pflichtfeld '{k}' fehlt")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        print(f"FEHLER: {path} nicht lesbar: {exc}")
        return 1

    if data.get("schemaVersion") != 1:
        err("schemaVersion muss 1 sein")
    need(data, ["updatedAt", "region", "channels", "series", "events"], "Datei")
    if data.get("updatedAt") and not START_RE.match(data["updatedAt"]):
        err("updatedAt hat falsches Format")

    all_ids = set()

    def unique(i, where):
        if i in all_ids:
            err(f"{where}: ID '{i}' ist doppelt")
        all_ids.add(i)

    channel_ids = set()
    for ch in data.get("channels", []):
        where = f"Sender {ch.get('id')}"
        need(ch, ["id", "name", "kind", "url"], where)
        unique(ch.get("id"), where)
        channel_ids.add(ch.get("id"))
        if ch.get("kind") not in CHANNEL_KINDS:
            err(f"{where}: unbekannte Art '{ch.get('kind')}'")
        if not str(ch.get("url", "")).startswith("https://"):
            err(f"{where}: URL muss mit https:// beginnen")

    series_ids = set()
    for s in data.get("series", []):
        where = f"Serie {s.get('id')}"
        need(s, ["id", "name", "shortName", "category", "tagline", "color", "channelIds"], where)
        unique(s.get("id"), where)
        series_ids.add(s.get("id"))
        if not COLOR_RE.match(str(s.get("color", ""))):
            err(f"{where}: Farbe muss #RRGGBB sein")
        for c in s.get("channelIds") or []:
            if c not in channel_ids:
                err(f"{where}: unbekannter Sender '{c}'")
        if s.get("website") and not str(s["website"]).startswith("https://"):
            err(f"{where}: Website muss mit https:// beginnen")

    now = datetime.now(timezone.utc)
    upcoming = {sid: 0 for sid in series_ids}
    session_count = 0
    for e in data.get("events", []):
        where = f"Event {e.get('id')}"
        need(e, ["id", "seriesId", "name", "circuit", "location", "countryCode", "sessions"], where)
        unique(e.get("id"), where)
        if e.get("seriesId") not in series_ids:
            err(f"{where}: unbekannte Serie '{e.get('seriesId')}'")
        if not CC_RE.match(str(e.get("countryCode", ""))):
            err(f"{where}: countryCode muss aus 2 Grossbuchstaben bestehen")
        for c in e.get("channelIds") or []:
            if c not in channel_ids:
                err(f"{where}: unbekannter Sender '{c}'")
        for src in e.get("sources") or []:
            if not str(src).startswith("http"):
                err(f"{where}: Quelle '{src}' ist keine URL")
        starts = []
        for s in e.get("sessions") or []:
            session_count += 1
            sw = f"{where} / Session {s.get('id')}"
            need(s, ["id", "kind", "name", "start", "durationMinutes"], sw)
            unique(s.get("id"), sw)
            if s.get("kind") not in SESSION_KINDS:
                err(f"{sw}: unbekannte Art '{s.get('kind')}'")
            start = str(s.get("start", ""))
            if not START_RE.match(start):
                err(f"{sw}: start muss YYYY-MM-DDTHH:MM:SSZ sein")
            else:
                dt = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                if not 2000 <= dt.year <= 2100:
                    err(f"{sw}: Jahr {dt.year} ausserhalb 2000–2100")
                starts.append(dt)
                if dt > now and e.get("seriesId") in upcoming:
                    upcoming[e["seriesId"]] += 1
            dur = s.get("durationMinutes")
            if not isinstance(dur, int) or not 10 <= dur <= 1500:
                err(f"{sw}: Dauer muss 10–1500 Minuten sein")
            if not isinstance(s.get("confirmed"), bool):
                err(f"{sw}: confirmed muss Boolean sein")
        if not starts and not errors:
            err(f"{where}: keine Sessions")
        if starts and (max(starts) - min(starts)).total_seconds() > 16 * 86400:
            err(f"{where}: Sessions liegen mehr als 16 Tage auseinander")

    for sid, n in upcoming.items():
        if n == 0:
            warnings.append(f"Serie {sid}: keine kommende Session")

    for w in warnings:
        print(f"WARNUNG: {w}")
    for e in errors:
        print(f"FEHLER: {e}")
    if errors:
        print(f"{len(errors)} Fehler")
        return 1
    print(f"OK: {len(series_ids)} Serien, {len(data.get('events', []))} Events, "
          f"{session_count} Sessions, {len(channel_ids)} Sender")
    return 0


if __name__ == "__main__":
    sys.exit(main())
