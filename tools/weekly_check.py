#!/usr/bin/env python3
"""Kurzliste für das wöchentliche Datenupdate (spart Recherche):

1. Provisorische Sessions (confirmed=false) der nächsten 14 Tage → offizielle Startzeit suchen.
2. Serien, deren letztes Event in weniger als 60 Tagen endet → neuen Kalender suchen.
3. Am ersten Montag im Monat (Tag 1–7): Beobachtungsliste tools/watchlist.md (Fahrer, offene Kalender).

    python3 tools/weekly_check.py
"""
import json
import pathlib
from datetime import datetime, timedelta, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data" / "races.json").read_text(encoding="utf-8"))
now = datetime.now(timezone.utc)
series = {s["id"]: s for s in data["series"]}


def parse(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


print("PROVISORISCH IN DEN NÄCHSTEN 14 TAGEN:")
found = False
for e in data["events"]:
    open_sessions = [s for s in e["sessions"]
                     if not s["confirmed"] and now < parse(s["start"]) < now + timedelta(days=14)]
    if open_sessions:
        found = True
        names = ", ".join(f"{s['name']} {s['start']}" for s in open_sessions)
        print(f"- {series[e['seriesId']]['shortName']} | {e['id']} | {e['name']} ({e['location']}) | {names}")
if not found:
    print("- keine")

print("\nKALENDER LÄUFT BALD AUS (letztes Event < 60 Tage):")
found = False
for sid, s in series.items():
    ends = [parse(x["start"]) for e in data["events"] if e["seriesId"] == sid for x in e["sessions"]]
    last = max(ends) if ends else None
    if last is None or last < now + timedelta(days=60):
        found = True
        print(f"- {s['shortName']} ({sid}): letztes Event {last:%Y-%m-%d}" if last else f"- {s['shortName']} ({sid}): keine Events")
if not found:
    print("- keine")

if now.day <= 7:
    print("\nBEOBACHTUNGSLISTE (erster Montag im Monat):")
    print((ROOT / "tools" / "watchlist.md").read_text(encoding="utf-8").strip())
