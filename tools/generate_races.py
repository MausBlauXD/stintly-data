#!/usr/bin/env python3
"""Erzeugt data/races.json (wird von der Stintly-App geladen).

Alle Termine werden hier als Ortszeit der Strecke + IANA-Zeitzone eingetragen
und beim Schreiben in UTC umgerechnet (Sommer-/Winterzeit stimmt automatisch).

Ablauf beim Datenupdate: Termine unten anpassen, dann
    python3 tools/generate_races.py && python3 tools/validate_races.py
"""
import json
import pathlib
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from i18n import translate_data  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUTS = [ROOT / "data" / "races.json"]
CALENDAR_DIR = ROOT / "docs" / "calendar"
SITE = "https://mausblauxd.github.io/stintly-data"

DEFAULT_DURATION = {"practice": 60, "qualifying": 60, "sprint": 45, "race": 120}

# ---------------------------------------------------------------------------
# Sender
# ---------------------------------------------------------------------------
CHANNELS = [
    ("srf2", "SRF zwei", "freeTV", "https://www.srf.ch/play/tv/live", "Teils auch auf SRF info oder SRF 1"),
    ("playsrf", "Play SRF / SRF Sport App", "freeStream", "https://www.srf.ch/sport", "Livestream gratis in der Schweiz"),
    ("sky", "Sky Sport", "payStream", "https://sky.ch/de/sport", "Alle Sessions, Abo nötig"),
    ("prosieben", "ProSieben", "freeTV", "https://www.prosieben.ch", "Empfang in der Schweiz je nach TV-Anbieter"),
    ("joyn", "Joyn", "freeStream", "https://www.joyn.de", "Gratis-Livestream; aus der Schweiz evtl. gesperrt"),
    ("yt-vln", "YouTube · VLNOFFICIAL", "freeStream", "https://www.youtube.com/results?search_query=VLNOFFICIAL+live", "Offizieller Gratis-Livestream der NLS"),
    ("nls-web", "NLS-Website", "freeStream", "https://www.nuerburgring-langstrecken-serie.de", "Livestream & Live-Timing"),
    ("yt-24h", "YouTube · 24h Nürburgring", "freeStream", "https://www.youtube.com/results?search_query=24h+N%C3%BCrburgring+live", "Gratis-Livestream"),
    ("n24-web", "24h-rennen.de", "freeStream", "https://www.24h-rennen.de", "Livestream & Live-Timing"),
    ("eurosport", "Eurosport", "payTV", "https://www.eurosport.de", "Meist Eurosport 2, Schlussphase oft Eurosport 1"),
    ("hbomax", "HBO Max", "payStream", "https://www.hbomax.com", None),
    ("fiawecplus", "FIAWEC+", "payStream", "https://www.fiawec.com", "Offizieller Stream der WEC"),
    ("bluetv", "blue TV", "payTV", "https://www.blue.ch", "Swisscom; bis Saison 12 Formel-E-Partner"),
    ("disneyplus", "Disney+", "payStream", "https://www.disneyplus.com", "Ab Saison 13 laut Formel E; Schweizer Partner noch offen"),
    ("f1tv", "F1 TV Pro", "payStream", "https://f1tv.formula1.com", "Offizieller Stream inkl. F2, F3 und F1 Academy"),
    ("motorvision", "Motorvision+", "payStream", "https://www.motorvision.tv", "IndyCar mit deutschem Kommentar"),
    ("sportdigital", "Sportdigital1+", "payTV", "https://www.sportdigital.de", "NASCAR Cup live (DACH), Empfang je nach TV-Anbieter"),
    ("yt-imsa", "YouTube · IMSA", "freeStream", "https://www.youtube.com/@IMSA", "Gratis-Livestream ausserhalb Nordamerikas"),
    ("yt-elms", "YouTube · ELMS", "freeStream", "https://www.youtube.com/results?search_query=European+Le+Mans+Series+live", "Offizieller Gratis-Livestream"),
    ("yt-gtworld", "YouTube · GT World", "freeStream", "https://www.youtube.com/@GTWorld", "Offizieller Gratis-Livestream"),
    ("yt-btcc", "YouTube · BTCC", "freeStream", "https://www.youtube.com/results?search_query=BTCC+live", "Gratis-Livestream ausserhalb UK und Nordamerika"),
    ("superview", "SuperView", "payStream", "https://www.supercars.com", "Internationaler Stream der Supercars (Abo)"),
    ("servustv", "ServusTV On", "freeStream", "https://www.servustv.com", "Gratis-Stream in DE/AT/CH"),
    ("sbk-pass", "WorldSBK VideoPass", "payStream", "https://www.worldsbk.com", "Offizieller Stream, alle Sessions"),
    ("ttplus", "TT+", "payStream", "https://www.iomttraces.com", "Offizieller Livestream der Isle of Man TT"),
    ("mxgp-tv", "MXGP-TV", "payStream", "https://www.mxgp-tv.com", "Offizieller Stream der Motocross-WM"),
    ("smx-pass", "SMX Video Pass", "payStream", "https://www.supermotocross.com", "Internationaler Stream für Supercross"),
    ("rallytv", "Rally.TV", "payStream", "https://rally.tv", "Alle WRC-Prüfungen live"),
    ("dakar-web", "dakar.com", "freeStream", "https://www.dakar.com", "Live-Tracking & tägliche Highlights"),
    ("yt-ppihc", "YouTube · Pikes Peak", "freeStream", "https://www.youtube.com/results?search_query=Pikes+Peak+Hill+Climb+live", "Gratis-Livestream"),
    ("yt-adac", "YouTube · ADAC Motorsport", "freeStream", "https://www.youtube.com/@ADACMotorsport", "Livestream je nach Rechtelage"),
    ("yt-porsche", "YouTube · Porsche Motorsport", "freeStream", "https://www.youtube.com/@PorscheMotorsport", "Livestream je nach Rechtelage"),
    ("yt-macau", "YouTube · Macau Grand Prix", "freeStream", "https://www.youtube.com/results?search_query=Macau+Grand+Prix+live", "Livestream je nach Region"),
]

# ---------------------------------------------------------------------------
# Serien (Reihenfolge = Anzeige-Reihenfolge, Kategorien nach erstem Auftreten)
# ---------------------------------------------------------------------------
SERIES = [
    # Formel
    ("f1", "Formel 1", "F1", "Formel", "Die Königsklasse", "#E10600", ["srf2", "playsrf", "sky"], "https://www.formula1.com"),
    ("f2", "Formel 2", "F2", "Formel", "Sprungbrett zur F1", "#0090D0", ["sky", "f1tv"], "https://www.fiaformula2.com"),
    ("f3", "Formel 3", "F3", "Formel", "Nachwuchs-Formelserie", "#E57200", ["sky", "f1tv"], "https://www.fiaformula3.com"),
    ("f1academy", "F1 Academy", "F1A", "Formel", "Formelserie für Frauen", "#E6007E", ["f1tv", "sky"], "https://www.f1academy.com"),
    ("indycar", "IndyCar", "Indy", "Formel", "Inkl. Indy 500", "#22356F", ["sky", "motorvision"], "https://www.indycar.com"),
    ("fe", "Formel E", "FE", "Formel", "Elektrische Stadtrennen", "#00B2A9", ["disneyplus", "bluetv"], "https://www.fiaformulae.com"),
    # Langstrecke
    ("wec", "Langstrecken-WM (WEC)", "WEC", "Langstrecke", "Inkl. 24h Le Mans", "#0057B8", ["eurosport", "hbomax", "fiawecplus"], "https://www.fiawec.com"),
    ("imsa", "IMSA SportsCar", "IMSA", "Langstrecke", "Inkl. 24h Daytona", "#8A1538", ["yt-imsa"], "https://www.imsa.com"),
    ("elms", "European Le Mans Series", "ELMS", "Langstrecke", "4-Stunden-Rennen in Europa", "#6A2C91", ["yt-elms"], "https://www.europeanlemansseries.com"),
    ("gtwc", "GT World Challenge Europe", "GTWC", "Langstrecke", "Inkl. 24h Spa", "#F26522", ["yt-gtworld"], "https://www.gt-world-challenge-europe.com"),
    ("nls", "Nürburgring Langstrecken-Serie", "NLS", "Langstrecke", "Nordschleife", "#008C45", ["yt-vln", "nls-web"], "https://www.nuerburgring-langstrecken-serie.de"),
    ("n24", "24h Nürburgring", "24h", "Langstrecke", "Grüne Hölle, 24 Stunden", "#F2A900", ["yt-24h", "n24-web"], "https://www.24h-rennen.de"),
    # Tourenwagen / GT
    ("dtm", "DTM", "DTM", "Tourenwagen / GT", "GT3-Sprintrennen", "#1B3D8F", ["prosieben", "joyn"], "https://www.dtm.com"),
    ("gtmasters", "ADAC GT Masters", "GTM", "Tourenwagen / GT", "GT3-Sprints im DTM-Rahmen", "#F2B800", ["joyn", "yt-adac"], "https://www.adac-motorsport.de/adac-gt-masters/"),
    ("carreracup", "Porsche Carrera Cup Deutschland", "CCD", "Tourenwagen / GT", "Markenpokal im DTM-Rahmen", "#3C3C46", ["joyn", "yt-porsche"], "https://www.adac-motorsport.de/porsche-carrera-cup-deutschland/"),
    ("supercup", "Porsche Supercup", "PSC", "Tourenwagen / GT", "Markenpokal im F1-Rahmen", "#B12B28", ["sky", "f1tv"], "https://racing.porsche.com/mobil-1-supercup"),
    ("carreracupna", "Porsche Carrera Cup North America", "CCNA", "Tourenwagen / GT", "Markenpokal bei F1, IMSA und IndyCar in den USA", "#1F4E79", ["yt-porsche"], "https://racing.porsche.com/en-US/series/carrera-cup-north-america"),
    ("macau", "Macau Grand Prix", "Macau", "Tourenwagen / GT", "GT World Cup auf dem Guia Circuit", "#0B8A6E", ["yt-macau"], "https://www.macau.grandprix.gov.mo"),
    ("btcc", "British Touring Car Championship", "BTCC", "Tourenwagen / GT", "Britische Tourenwagen", "#D4145A", ["yt-btcc"], "https://www.btcc.net"),
    ("supercars", "Supercars", "SC", "Tourenwagen / GT", "V8-Tourenwagen aus Australien", "#B5121B", ["superview"], "https://www.supercars.com"),
    ("nascar", "NASCAR Cup Series", "NASCAR", "Tourenwagen / GT", "Stockcars, inkl. Daytona 500", "#FFB81C", ["sportdigital"], "https://www.nascar.com"),
    # Motorrad
    ("motogp", "MotoGP", "MotoGP", "Motorrad", "Motorrad-WM", "#C8102E", ["srf2", "playsrf", "sky"], "https://www.motogp.com"),
    ("moto2", "Moto2", "Moto2", "Motorrad", "Mittelklasse der Motorrad-WM", "#3F51B5", ["playsrf", "sky"], "https://www.motogp.com"),
    ("moto3", "Moto3", "Moto3", "Motorrad", "Einstiegsklasse der Motorrad-WM", "#00897B", ["playsrf", "sky"], "https://www.motogp.com"),
    ("wsbk", "Superbike-WM (WorldSBK)", "SBK", "Motorrad", "Seriennahe Superbikes", "#1D7FD1", ["servustv", "sbk-pass"], "https://www.worldsbk.com"),
    ("iomtt", "Isle of Man TT", "TT", "Motorrad", "Strassenrennen auf der Isle of Man", "#B8860B", ["ttplus"], "https://www.iomttraces.com"),
    ("mxgp", "Motocross-WM (MXGP)", "MXGP", "Motorrad", "Motocross weltweit", "#FF7A00", ["eurosport", "hbomax", "mxgp-tv"], "https://www.mxgp.com"),
    ("supercross", "Supercross (AMA)", "SX", "Motorrad", "US-Stadionrennen", "#5E35B1", ["smx-pass"], "https://www.supercrossonline.com"),
    # Rallye & Bergrennen
    ("wrc", "Rallye-WM (WRC)", "WRC", "Rallye & Bergrennen", "Rallye-Weltmeisterschaft", "#0033A0", ["rallytv"], "https://www.wrc.com"),
    ("dakar", "Rallye Dakar", "Dakar", "Rallye & Bergrennen", "Wüstenrallye in Saudi-Arabien", "#B07D3C", ["eurosport", "dakar-web"], "https://www.dakar.com"),
    ("pikespeak", "Pikes Peak Hill Climb", "Pikes", "Rallye & Bergrennen", "Bergrennen in Colorado", "#2F6F4F", ["yt-ppihc"], "https://ppihc.org"),
]

EVENTS = []


def t_(de, en, fr, it):
    return {"de": de, "en": en, "fr": fr, "it": it}


def d(date_str):
    """'24.10.2026' -> date"""
    return datetime.strptime(date_str, "%d.%m.%Y").date()


def at(day, hhmm):
    h, m = hhmm.split(":")
    return datetime(day.year, day.month, day.day, int(h), int(m))


def event(series, slug, name, circuit, location, cc, tz, sessions, sources, note=None, channel_ids=None):
    """sessions: Liste von (kind, name, naive local datetime, durationMinutes|None, confirmed)"""
    zone = ZoneInfo(tz)
    converted = []
    for kind, sname, local, dur, confirmed in sessions:
        utc = local.replace(tzinfo=zone).astimezone(timezone.utc)
        converted.append((utc, kind, sname, dur or DEFAULT_DURATION[kind], confirmed))
    converted.sort(key=lambda s: s[0])
    year = converted[0][0].astimezone(zone).year
    event_id = f"{series}-{year}-{slug}"
    counters = {}
    out_sessions = []
    for utc, kind, sname, dur, confirmed in converted:
        counters[kind] = counters.get(kind, 0) + 1
        out_sessions.append({
            "id": f"{event_id}-{kind}-{counters[kind]}",
            "kind": kind,
            "name": sname,
            "start": utc.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "durationMinutes": dur,
            "confirmed": confirmed,
        })
    EVENTS.append({
        "id": event_id,
        "seriesId": series,
        "name": name,
        "circuit": circuit,
        "location": location,
        "countryCode": cc,
        "sessions": out_sessions,
        "sources": sources,
        "channelIds": channel_ids,
        "note": note,
    })


# ---------------------------------------------------------------------------
# Formel 1 – Rest 2026 (bestätigt)
# ---------------------------------------------------------------------------
F1_2026_SRC = [
    "https://www.formel1.de/formel-1-kalender/2026",
    "https://www.motorsport-total.com/formel-1/termin-kalender/2026",
]
for slug, name, circuit, loc, cc, tz, quali, race in [
    ("usa", "Grosser Preis der USA", "Circuit of the Americas", "Austin", "US", "America/Chicago", "24.10.2026 16:00", "25.10.2026 15:00"),
    ("mexiko", "Grosser Preis von Mexiko", "Autódromo Hermanos Rodríguez", "Mexiko-Stadt", "MX", "America/Mexico_City", "31.10.2026 15:00", "01.11.2026 14:00"),
    ("sao-paulo", "Grosser Preis von São Paulo", "Interlagos", "São Paulo", "BR", "America/Sao_Paulo", "07.11.2026 15:00", "08.11.2026 14:00"),
    ("las-vegas", "Grosser Preis von Las Vegas", "Las Vegas Strip Circuit", "Las Vegas", "US", "America/Los_Angeles", "20.11.2026 20:00", "21.11.2026 20:00"),
    ("katar", "Grosser Preis von Katar", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "28.11.2026 21:00", "29.11.2026 19:00"),
    ("abu-dhabi", "Grosser Preis von Abu Dhabi", "Yas Marina Circuit", "Abu Dhabi", "AE", "Asia/Dubai", "05.12.2026 18:00", "06.12.2026 17:00"),
]:
    qd, qt = quali.split()
    rd, rt = race.split()
    event("f1", slug, name, circuit, loc, cc, tz, [
        ("qualifying", "Qualifying", at(d(qd), qt), None, True),
        ("race", "Rennen", at(d(rd), rt), None, True),
    ], F1_2026_SRC)

# ---------------------------------------------------------------------------
# Formel 1 – 2027 (Daten offiziell, Zeiten provisorisch)
# Qualifying am Tag vor dem Rennen, Sprint am gleichen Tag wie das Qualifying.
# ---------------------------------------------------------------------------
F1_2027_SRC = [
    "https://www.mclaren.com/racing/formula-1/2026/2027-calendar-announced/",
    "https://en.wikipedia.org/wiki/2027_Formula_One_World_Championship",
]
F1_2027 = [
    ("bahrain", "Grosser Preis von Bahrain", "Bahrain International Circuit", "Sakhir", "BH", "Asia/Bahrain", "14.03.2027", "18:00", "19:00", "14:30"),
    ("saudi-arabien", "Grosser Preis von Saudi-Arabien", "Jeddah Corniche Circuit", "Dschidda", "SA", "Asia/Riyadh", "21.03.2027", "20:00", "20:00", None),
    ("australien", "Grosser Preis von Australien", "Albert Park", "Melbourne", "AU", "Australia/Melbourne", "04.04.2027", "15:00", "16:00", "11:30"),
    ("japan", "Grosser Preis von Japan", "Suzuka", "Suzuka", "JP", "Asia/Tokyo", "11.04.2027", "14:00", "15:00", "11:30"),
    ("china", "Grosser Preis von China", "Shanghai International Circuit", "Shanghai", "CN", "Asia/Shanghai", "18.04.2027", "15:00", "15:00", None),
    ("miami", "Grosser Preis von Miami", "Miami International Autodrome", "Miami", "US", "America/New_York", "02.05.2027", "16:00", "16:00", None),
    ("kanada", "Grosser Preis von Kanada", "Circuit Gilles Villeneuve", "Montréal", "CA", "America/Toronto", "23.05.2027", "14:00", "16:00", "12:00"),
    ("monaco", "Grosser Preis von Monaco", "Circuit de Monaco", "Monte Carlo", "MC", "Europe/Monaco", "06.06.2027", "15:00", "16:00", "12:00"),
    ("portugal", "Grosser Preis von Portugal", "Autódromo Internacional do Algarve", "Portimão", "PT", "Europe/Lisbon", "20.06.2027", "15:00", "16:00", None),
    ("grossbritannien", "Grosser Preis von Grossbritannien", "Silverstone", "Silverstone", "GB", "Europe/London", "04.07.2027", "15:00", "16:00", "12:00"),
    ("oesterreich", "Grosser Preis von Österreich", "Red Bull Ring", "Spielberg", "AT", "Europe/Vienna", "11.07.2027", "15:00", "16:00", None),
    ("belgien", "Grosser Preis von Belgien", "Spa-Francorchamps", "Spa", "BE", "Europe/Brussels", "25.07.2027", "15:00", "16:00", None),
    ("ungarn", "Grosser Preis von Ungarn", "Hungaroring", "Budapest", "HU", "Europe/Budapest", "01.08.2027", "15:00", "16:00", None),
    ("italien", "Grosser Preis von Italien", "Monza", "Monza", "IT", "Europe/Rome", "05.09.2027", "15:00", "16:00", "12:00"),
    ("spanien", "Grosser Preis von Spanien", "Madring", "Madrid", "ES", "Europe/Madrid", "12.09.2027", "15:00", "16:00", None),
    ("aserbaidschan", "Grosser Preis von Aserbaidschan", "Baku City Circuit", "Baku", "AZ", "Asia/Baku", "26.09.2027", "15:00", "16:00", None),
    ("tuerkei", "Grosser Preis der Türkei", "Istanbul Park", "Istanbul", "TR", "Europe/Istanbul", "03.10.2027", "15:00", "16:00", None),
    ("singapur", "Grosser Preis von Singapur", "Marina Bay", "Singapur", "SG", "Asia/Singapore", "10.10.2027", "20:00", "21:00", None),
    ("usa", "Grosser Preis der USA", "Circuit of the Americas", "Austin", "US", "America/Chicago", "24.10.2027", "15:00", "16:00", None),
    ("mexiko", "Grosser Preis von Mexiko", "Autódromo Hermanos Rodríguez", "Mexiko-Stadt", "MX", "America/Mexico_City", "31.10.2027", "14:00", "15:00", None),
    ("sao-paulo", "Grosser Preis von São Paulo", "Interlagos", "São Paulo", "BR", "America/Sao_Paulo", "07.11.2027", "14:00", "15:00", "11:00"),
    ("las-vegas", "Grosser Preis von Las Vegas", "Las Vegas Strip Circuit", "Las Vegas", "US", "America/Los_Angeles", "20.11.2027", "20:00", "20:00", None),
    ("katar", "Grosser Preis von Katar", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "05.12.2027", "19:00", "21:00", "17:00"),
    ("abu-dhabi", "Grosser Preis von Abu Dhabi", "Yas Marina Circuit", "Abu Dhabi", "AE", "Asia/Dubai", "12.12.2027", "17:00", "18:00", "14:00"),
]
for slug, name, circuit, loc, cc, tz, raceday, race, quali, sprint in F1_2027:
    rday = d(raceday)
    qday = rday - timedelta(days=1)
    sessions = [
        ("qualifying", "Qualifying", at(qday, quali), None, False),
        ("race", "Rennen", at(rday, race), None, False),
    ]
    if sprint:
        sessions.append(("sprint", "Sprint", at(qday, sprint), None, False))
    event("f1", slug, name, circuit, loc, cc, tz, sessions, F1_2027_SRC,
          note="Daten offiziell, Startzeiten noch provisorisch")

# ---------------------------------------------------------------------------
# MotoGP (Sprint Samstag 30 Min., Rennen Sonntag 45 Min.)
# ---------------------------------------------------------------------------
MOTOGP_2026_SRC = ["https://www.crash.net/motogp"]
MOTOGP_2027_SRC = ["https://www.motogp.com/en/news/2026/09/25/2027-motogp-calendar-revealed/1092589"]
MOTOGP = [
    ("australien", "Grand Prix von Australien", "Phillip Island", "Phillip Island", "AU", "Australia/Melbourne", "25.10.2026", "15:00", "14:00", True),
    ("malaysia", "Grand Prix von Malaysia", "Sepang International Circuit", "Sepang", "MY", "Asia/Kuala_Lumpur", "01.11.2026", "16:00", "15:00", False),
    ("katar", "Grand Prix von Katar", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "08.11.2026", "19:00", "20:00", False),
    ("portugal", "Grand Prix von Portugal", "Autódromo Internacional do Algarve", "Portimão", "PT", "Europe/Lisbon", "22.11.2026", "15:00", "14:00", False),
    ("valencia", "Grand Prix von Valencia", "Circuit Ricardo Tormo", "Valencia", "ES", "Europe/Madrid", "29.11.2026", "15:00", "14:00", False),
    ("thailand", "Grand Prix von Thailand", "Chang International Circuit", "Buriram", "TH", "Asia/Bangkok", "07.03.2027", "16:00", "15:00", False),
    ("katar", "Grand Prix von Katar", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "14.03.2027", "19:00", "20:00", False),
    ("brasilien", "Grand Prix von Brasilien", "Autódromo de Goiânia", "Goiânia", "BR", "America/Sao_Paulo", "04.04.2027", "15:00", "14:00", False),
    ("argentinien", "Grand Prix von Argentinien", "Autódromo Oscar y Juan Gálvez", "Buenos Aires", "AR", "America/Argentina/Buenos_Aires", "11.04.2027", "15:00", "14:00", False),
    ("usa", "Grand Prix der USA", "Circuit of the Americas", "Austin", "US", "America/Chicago", "25.04.2027", "15:00", "14:00", False),
    ("spanien", "Grand Prix von Spanien", "Circuito de Jerez", "Jerez", "ES", "Europe/Madrid", "09.05.2027", "15:00", "14:00", False),
    ("frankreich", "Grand Prix von Frankreich", "Bugatti Circuit", "Le Mans", "FR", "Europe/Paris", "16.05.2027", "15:00", "14:00", False),
    ("italien", "Grand Prix von Italien", "Mugello", "Mugello", "IT", "Europe/Rome", "30.05.2027", "15:00", "14:00", False),
    ("katalonien", "Grand Prix von Katalonien", "Circuit de Barcelona-Catalunya", "Barcelona", "ES", "Europe/Madrid", "13.06.2027", "15:00", "14:00", False),
    ("niederlande", "Dutch TT", "TT Circuit Assen", "Assen", "NL", "Europe/Amsterdam", "27.06.2027", "15:00", "14:00", False),
    ("deutschland", "Grand Prix von Deutschland", "Sachsenring", "Hohenstein-Ernstthal", "DE", "Europe/Berlin", "11.07.2027", "15:00", "14:00", False),
    ("tschechien", "Grand Prix von Tschechien", "Automotodrom Brno", "Brünn", "CZ", "Europe/Prague", "18.07.2027", "15:00", "14:00", False),
    ("grossbritannien", "Grand Prix von Grossbritannien", "Silverstone", "Silverstone", "GB", "Europe/London", "15.08.2027", "15:00", "14:00", False),
    ("oesterreich", "Grand Prix von Österreich", "Red Bull Ring", "Spielberg", "AT", "Europe/Vienna", "29.08.2027", "15:00", "14:00", False),
    ("san-marino", "Grand Prix von San Marino", "Misano World Circuit", "Misano", "SM", "Europe/Rome", "12.09.2027", "15:00", "14:00", False),
    ("aragon", "Grand Prix von Aragón", "MotorLand Aragón", "Alcañiz", "ES", "Europe/Madrid", "19.09.2027", "15:00", "14:00", False),
    ("portugal", "Grand Prix von Portugal", "Autódromo Internacional do Algarve", "Portimão", "PT", "Europe/Lisbon", "03.10.2027", "15:00", "14:00", False),
    ("japan", "Grand Prix von Japan", "Mobility Resort Motegi", "Motegi", "JP", "Asia/Tokyo", "17.10.2027", "15:00", "14:00", False),
    ("malaysia", "Grand Prix von Malaysia", "Sepang International Circuit", "Sepang", "MY", "Asia/Kuala_Lumpur", "24.10.2027", "16:00", "15:00", False),
    ("indonesien", "Grand Prix von Indonesien", "Mandalika", "Lombok", "ID", "Asia/Makassar", "31.10.2027", "16:00", "15:00", False),
    ("australien", "Grand Prix von Australien", "Adelaide Street Circuit", "Adelaide", "AU", "Australia/Adelaide", "14.11.2027", "15:00", "14:00", False),
    ("valencia", "Grand Prix von Valencia", "Circuit Ricardo Tormo", "Valencia", "ES", "Europe/Madrid", "28.11.2027", "15:00", "14:00", False),
]
for slug, name, circuit, loc, cc, tz, raceday, sprint, race, confirmed in MOTOGP:
    rday = d(raceday)
    event("motogp", slug, name, circuit, loc, cc, tz, [
        ("sprint", "Sprint", at(rday - timedelta(days=1), sprint), 30, confirmed),
        ("race", "Rennen", at(rday, race), 45, confirmed),
    ], MOTOGP_2026_SRC if rday.year == 2026 else MOTOGP_2027_SRC,
        note=None if confirmed else "Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# DTM 2027 (Rennen 1 Sa 13:30, Rennen 2 So 13:30, Hockenheim So 16:30)
# ---------------------------------------------------------------------------
DTM_SRC = [
    "https://www.hockenheimring.de/2026/08/dtm-2027-alpen-auftakt-stadtspektakel-und-nordsee-action/",
    "https://www.motorsport-magazin.com/dtm/",
]
for slug, name, circuit, loc, cc, tz, saturday in [
    ("spielberg", "DTM Spielberg", "Red Bull Ring", "Spielberg", "AT", "Europe/Vienna", "24.04.2027"),
    ("oschersleben", "DTM Oschersleben", "Motorsport Arena Oschersleben", "Oschersleben", "DE", "Europe/Berlin", "08.05.2027"),
    ("lausitzring", "DTM Lausitzring", "Lausitzring", "Klettwitz", "DE", "Europe/Berlin", "19.06.2027"),
    ("norisring", "DTM Norisring", "Norisring", "Nürnberg", "DE", "Europe/Berlin", "03.07.2027"),
    ("zandvoort", "DTM Zandvoort", "Circuit Zandvoort", "Zandvoort", "NL", "Europe/Amsterdam", "07.08.2027"),
    ("nuerburgring", "DTM Nürburgring", "Nürburgring GP-Strecke", "Nürburg", "DE", "Europe/Berlin", "21.08.2027"),
    ("sachsenring", "DTM Sachsenring", "Sachsenring", "Hohenstein-Ernstthal", "DE", "Europe/Berlin", "25.09.2027"),
    ("hockenheim", "DTM Finale Hockenheim", "Hockenheimring", "Hockenheim", "DE", "Europe/Berlin", "09.10.2027"),
]:
    sat = d(saturday)
    sunday_time = "16:30" if slug == "hockenheim" else "13:30"
    event("dtm", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen 1", at(sat, "13:30"), 60, False),
        ("race", "Rennen 2", at(sat + timedelta(days=1), sunday_time), 60, False),
    ], DTM_SRC, note="Daten offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# NLS 2027 (Zeittraining 08:30 / 90 Min., Rennen 12:00)
# ---------------------------------------------------------------------------
NLS_SRC = ["https://www.motorsport-total.com/nls/", "https://www.motorsport-xl.de"]
for slug, name, date, race_minutes in [
    ("nls1", "NLS 1", "20.03.2027", 240),
    ("nls2", "NLS 2", "17.04.2027", 240),
    ("nls3", "NLS 3", "03.07.2027", 240),
    ("nls4", "NLS 4 · 6h-Rennen", "07.08.2027", 360),
    ("nls5", "NLS 5", "11.09.2027", 240),
    ("nls6", "NLS 6", "12.09.2027", 240),
    ("nls7", "NLS 7", "25.09.2027", 240),
    ("nls8", "NLS 8 · Saisonfinale", "09.10.2027", 240),
]:
    day = d(date)
    event("nls", slug, name, "Nürburgring Nordschleife", "Nürburg", "DE", "Europe/Berlin", [
        ("qualifying", "Zeittraining", at(day, "08:30"), 90, False),
        ("race", "Rennen", at(day, "12:00"), race_minutes, False),
    ], NLS_SRC, note="Daten offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# 24h Nürburgring 2027
# ---------------------------------------------------------------------------
N24_SRC = ["https://www.24h-rennen.de/termine/", "https://www.motorsport-total.com"]
event("n24", "qualifiers", "24h Qualifiers", "Nürburgring Nordschleife", "Nürburg", "DE", "Europe/Berlin", [
    ("race", "Qualifikationsrennen 1", at(d("01.05.2027"), "13:00"), 180, False),
    ("race", "Qualifikationsrennen 2", at(d("02.05.2027"), "13:00"), 180, False),
], N24_SRC, note="Datum offiziell (30. April – 2. Mai), Startzeiten provisorisch")
event("n24", "rennen", "55. ADAC 24h Nürburgring", "Nordschleife + GP-Strecke", "Nürburg", "DE", "Europe/Berlin", [
    ("qualifying", "Top-Qualifying", at(d("28.05.2027"), "17:00"), 60, False),
    ("race", "24h-Rennen", at(d("29.05.2027"), "15:30"), 1440, False),
], N24_SRC, note="Datum offiziell (27.–30. Mai), Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# WEC (nur Rennen)
# ---------------------------------------------------------------------------
WEC_SRC = ["https://www.fiawec.com", "https://www.fiawec.com/en/race/show/4955"]
for slug, name, circuit, loc, cc, tz, date, start, minutes in [
    ("bahrain", "8 Stunden von Bahrain", "Bahrain International Circuit", "Sakhir", "BH", "Asia/Bahrain", "07.11.2026", "14:00", 480),
    ("katar", "Qatar 1812 km", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "27.03.2027", "13:00", 600),
    ("imola", "6 Stunden von Imola", "Autodromo Enzo e Dino Ferrari", "Imola", "IT", "Europe/Rome", "11.04.2027", "13:00", 360),
    ("silverstone", "6 Stunden von Silverstone", "Silverstone", "Silverstone", "GB", "Europe/London", "25.04.2027", "12:00", 360),
    ("spa", "6 Stunden von Spa-Francorchamps", "Spa-Francorchamps", "Spa", "BE", "Europe/Brussels", "15.05.2027", "13:00", 360),
    ("le-mans", "24 Stunden von Le Mans", "Circuit de la Sarthe", "Le Mans", "FR", "Europe/Paris", "12.06.2027", "16:00", 1440),
    ("sao-paulo", "6 Stunden von São Paulo", "Interlagos", "São Paulo", "BR", "America/Sao_Paulo", "11.07.2027", "12:00", 360),
    ("cota", "Lone Star Le Mans", "Circuit of the Americas", "Austin", "US", "America/Chicago", "12.09.2027", "13:00", 360),
    ("fuji", "6 Stunden von Fuji", "Fuji Speedway", "Oyama", "JP", "Asia/Tokyo", "26.09.2027", "11:00", 360),
    ("bahrain", "8 Stunden von Bahrain", "Bahrain International Circuit", "Sakhir", "BH", "Asia/Bahrain", "06.11.2027", "14:00", 480),
]:
    event("wec", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen", at(d(date), start), minutes, False),
    ], WEC_SRC, note="Startzeit provisorisch")

# ---------------------------------------------------------------------------
# Formel E, Saison 13 (2026/27), Rennen 60 Min.
# ---------------------------------------------------------------------------
FE_SRC = ["https://www.fiaformulae.com/en/news"]
for slug, name, circuit, loc, cc, tz, days, start in [
    ("jeddah", "Jeddah E-Prix", "Jeddah Corniche Circuit", "Dschidda", "SA", "Asia/Riyadh", ["18.12.2026", "19.12.2026"], "20:00"),
    ("mexiko", "Mexico City E-Prix", "Autódromo Hermanos Rodríguez", "Mexiko-Stadt", "MX", "America/Mexico_City", ["16.01.2027"], "15:00"),
    ("austin", "Austin E-Prix", "Circuit of the Americas", "Austin", "US", "America/Chicago", ["06.02.2027"], "15:00"),
    ("miami", "Miami E-Prix", "Homestead-Miami Speedway", "Miami", "US", "America/New_York", ["20.02.2027"], "16:00"),
    ("sao-paulo", "São Paulo E-Prix", "Anhembi Sambadrome", "São Paulo", "BR", "America/Sao_Paulo", ["13.03.2027"], "14:00"),
    ("sanya", "Sanya E-Prix", "Haitang Bay Circuit", "Sanya", "CN", "Asia/Shanghai", ["17.04.2027"], "15:00"),
    ("monaco", "Monaco E-Prix", "Circuit de Monaco", "Monte Carlo", "MC", "Europe/Monaco", ["01.05.2027", "02.05.2027"], "15:00"),
    ("berlin", "Berlin E-Prix", "Tempelhof Airport Street Circuit", "Berlin", "DE", "Europe/Berlin", ["08.05.2027", "09.05.2027"], "15:00"),
    ("london", "London E-Prix", "Brands Hatch", "Kent", "GB", "Europe/London", ["29.05.2027", "30.05.2027"], "15:00"),
    ("zandvoort", "Zandvoort E-Prix", "Circuit Zandvoort", "Zandvoort", "NL", "Europe/Amsterdam", ["18.06.2027", "19.06.2027"], "15:00"),
    ("madrid", "Madrid E-Prix", "Circuito del Jarama", "Madrid", "ES", "Europe/Madrid", ["26.06.2027", "27.06.2027"], "15:00"),
    ("shanghai", "Shanghai E-Prix", "Shanghai International Circuit", "Shanghai", "CN", "Asia/Shanghai", ["10.07.2027", "11.07.2027"], "15:00"),
    ("tokyo", "Tokyo E-Prix", "Tokyo Street Circuit", "Tokio", "JP", "Asia/Tokyo", ["24.07.2027", "25.07.2027"], "15:00"),
]:
    if len(days) == 1:
        sessions = [("race", "Rennen", at(d(days[0]), start), 60, False)]
    else:
        sessions = [("race", f"Rennen {i + 1}", at(d(day), start), 60, False) for i, day in enumerate(days)]
    event("fe", slug, name, circuit, loc, cc, tz, sessions, FE_SRC,
          note="Kalender provisorisch, Startzeiten provisorisch")


# ===========================================================================
# Erweiterung vom 16.10.2026: weitere Serien
# ===========================================================================

def shift(dt, hours=0.0):
    return dt + timedelta(hours=hours)


# ---------------------------------------------------------------------------
# Formel 2 / Formel 3 – im Rahmenprogramm der F1
# Sprint am Samstag, Hauptrennen am Sonntag; Zeiten relativ zum F1-Zeitplan (provisorisch).
# ---------------------------------------------------------------------------
F2F3_SRC = [
    "https://www.formula1.com/en/latest/article/fia-formula-2-and-fia-formula-3-announce-2027-calendars.7IToHJjbGez7YrJpMiihyH",
    "https://racer.com/2026/10/05/montreal-istanbul-mexico-city-join-f2-calendar-for-2027",
]
F2_2026_SRC = ["https://en.wikipedia.org/wiki/2026_FIA_Formula_2_Championship"]
F1_LOOKUP = {row[0]: row for row in F1_2027}

# Rest 2026: Lusail und Yas Marina (Daten offiziell)
for slug, circuit, loc, cc, tz, sprint_at, feature_at in [
    ("katar", "Lusail International Circuit", "Lusail", "QA", "Asia/Qatar", "28.11.2026 18:00", "29.11.2026 15:00"),
    ("abu-dhabi", "Yas Marina Circuit", "Abu Dhabi", "AE", "Asia/Dubai", "05.12.2026 15:00", "06.12.2026 13:00"),
]:
    sd, st = sprint_at.split()
    fd, ft = feature_at.split()
    event("f2", slug, f"F2 {loc}", circuit, loc, cc, tz, [
        ("sprint", "Sprintrennen", at(d(sd), st), 45, False),
        ("race", "Hauptrennen", at(d(fd), ft), 60, False),
    ], F2_2026_SRC, note="Datum offiziell, Startzeiten provisorisch")


def feeder_series(series, prefix, slugs, sprint_offset, feature_offset, sprint_min, feature_min):
    for slug in slugs:
        _, _, circuit, loc, cc, tz, raceday, race, quali, _ = F1_LOOKUP[slug]
        rday = d(raceday)
        qday = rday - timedelta(days=1)
        note = "Daten gemäss F1-Kalender, Startzeiten provisorisch"
        if slug == "kanada":
            note += "; Montreal noch unter Vertragsvorbehalt"
        event(series, slug, f"{prefix} {loc}", circuit, loc, cc, tz, [
            ("sprint", "Sprintrennen", shift(at(qday, quali), sprint_offset), sprint_min, False),
            ("race", "Hauptrennen", shift(at(rday, race), feature_offset), feature_min, False),
        ], F2F3_SRC, note=note)


feeder_series("f2", "F2", ["bahrain", "saudi-arabien", "australien", "kanada", "monaco", "grossbritannien",
                           "oesterreich", "italien", "spanien", "aserbaidschan", "tuerkei", "mexiko",
                           "katar", "abu-dhabi"], -3, -4, 45, 60)
feeder_series("f3", "F3", ["bahrain", "saudi-arabien", "australien", "kanada", "monaco", "grossbritannien",
                           "oesterreich", "italien", "spanien", "tuerkei"], -6, -6, 40, 50)

# ---------------------------------------------------------------------------
# F1 Academy – Rest 2026 (Kalender 2027 noch nicht veröffentlicht)
# ---------------------------------------------------------------------------
F1A_SRC = ["https://en.wikipedia.org/wiki/2026_F1_Academy_season", "https://www.f1academy.com"]
event("f1academy", "austin", "F1 Academy Austin", "Circuit of the Americas", "Austin", "US", "America/Chicago", [
    ("race", "Rennen 1", at(d("24.10.2026"), "09:30"), 30, False),
    ("race", "Rennen 2", at(d("24.10.2026"), "13:15"), 30, False),
    ("race", "Rennen 3", at(d("25.10.2026"), "11:00"), 30, False),
], F1A_SRC, note="Datum offiziell, Startzeiten provisorisch")
event("f1academy", "las-vegas", "F1 Academy Las Vegas", "Las Vegas Strip Circuit", "Las Vegas", "US", "America/Los_Angeles", [
    ("race", "Rennen 1", at(d("20.11.2026"), "16:30"), 30, False),
    ("race", "Rennen 2", at(d("21.11.2026"), "16:00"), 30, False),
], F1A_SRC, note="Datum offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# IndyCar 2027 (Phase 1 offiziell; Markham, Milwaukee, Laguna Seca noch ohne Datum)
# ---------------------------------------------------------------------------
INDY_SRC = ["https://www.indycar.com/news/2026/08/08-12-early-2027-sked", "https://en.wikipedia.org/wiki/2027_IndyCar_Series"]
for slug, name, circuit, loc, tz, date, start, minutes in [
    ("st-petersburg", "Grand Prix of St. Petersburg", "Streets of St. Petersburg", "St. Petersburg", "America/New_York", "07.03.2027", "12:00", 120),
    ("phoenix", "Good Ranchers 250", "Phoenix Raceway", "Avondale", "America/Phoenix", "13.03.2027", "13:00", 120),
    ("arlington", "Grand Prix of Arlington", "Streets of Arlington", "Arlington", "America/Chicago", "21.03.2027", "13:00", 120),
    ("barber", "Indy Grand Prix of Alabama", "Barber Motorsports Park", "Birmingham", "America/Chicago", "04.04.2027", "13:30", 120),
    ("long-beach", "Grand Prix of Long Beach", "Streets of Long Beach", "Long Beach", "America/Los_Angeles", "18.04.2027", "13:00", 120),
    ("ims-road", "Sonsio Grand Prix", "Indianapolis Motor Speedway (Road Course)", "Speedway", "America/Indiana/Indianapolis", "15.05.2027", "15:30", 120),
    ("indy500", "111. Indianapolis 500", "Indianapolis Motor Speedway", "Speedway", "America/Indiana/Indianapolis", "30.05.2027", "12:45", 210),
    ("detroit", "Detroit Grand Prix", "Streets of Detroit", "Detroit", "America/Detroit", "06.06.2027", "12:30", 120),
    ("gateway", "Bommarito Automotive Group 500", "World Wide Technology Raceway", "Madison", "America/Chicago", "13.06.2027", "15:00", 120),
    ("road-america", "Grand Prix at Road America", "Road America", "Elkhart Lake", "America/Chicago", "27.06.2027", "12:00", 120),
]:
    event("indycar", slug, name, circuit, loc, "US", tz, [
        ("race", "Rennen", at(d(date), start), minutes, False),
    ], INDY_SRC, note="Datum laut IndyCar bzw. Medienberichten, Startzeit provisorisch")

# ---------------------------------------------------------------------------
# IMSA WeatherTech SportsCar Championship 2027 (provisorischer Kalender)
# ---------------------------------------------------------------------------
IMSA_SRC = ["https://en.wikipedia.org/wiki/2027_IMSA_SportsCar_Championship", "https://www.imsa.com"]
for slug, name, circuit, loc, cc, tz, date, start, minutes in [
    ("daytona", "Rolex 24 at Daytona", "Daytona International Speedway", "Daytona Beach", "US", "America/New_York", "30.01.2027", "13:40", 1440),
    ("sebring", "12 Stunden von Sebring", "Sebring International Raceway", "Sebring", "US", "America/New_York", "20.03.2027", "10:10", 720),
    ("long-beach", "Grand Prix of Long Beach", "Long Beach Street Circuit", "Long Beach", "US", "America/Los_Angeles", "17.04.2027", "15:05", 100),
    ("laguna-seca", "Monterey SportsCar Championship", "WeatherTech Raceway Laguna Seca", "Monterey", "US", "America/Los_Angeles", "02.05.2027", "13:00", 160),
    ("detroit", "Detroit Sports Car Classic", "Detroit Street Circuit", "Detroit", "US", "America/Detroit", "05.06.2027", "11:30", 100),
    ("watkins-glen", "6 Stunden von Watkins Glen", "Watkins Glen International", "Watkins Glen", "US", "America/New_York", "27.06.2027", "10:40", 360),
    ("mosport", "Chevrolet Grand Prix", "Canadian Tire Motorsport Park", "Bowmanville", "CA", "America/Toronto", "11.07.2027", "13:05", 160),
    ("road-america", "6 Stunden von Road America", "Road America", "Elkhart Lake", "US", "America/Chicago", "08.08.2027", "11:10", 360),
    ("vir", "GT Challenge at VIR", "Virginia International Raceway", "Alton", "US", "America/New_York", "22.08.2027", "14:05", 160),
    ("indianapolis", "Battle on the Bricks", "Indianapolis Motor Speedway", "Speedway", "US", "America/Indiana/Indianapolis", "19.09.2027", "14:00", 160),
    ("petit-le-mans", "Petit Le Mans", "Michelin Raceway Road Atlanta", "Braselton", "US", "America/New_York", "09.10.2027", "12:10", 600),
]:
    event("imsa", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen", at(d(date), start), minutes, False),
    ], IMSA_SRC, note="Kalender provisorisch, Startzeit provisorisch")

# ---------------------------------------------------------------------------
# European Le Mans Series 2027
# ---------------------------------------------------------------------------
ELMS_SRC = [
    "https://www.24h-lemans.com/en/news/six-race-calendar-and-early-start-for-exciting-2027-elms-season-60875",
    "https://sportscar365.com/lemans/elms/earlier-start-for-unchanged-2027-calendar/",
]
for slug, name, circuit, loc, cc, tz, date, minutes in [
    ("barcelona", "6 Stunden von Barcelona", "Circuit de Barcelona-Catalunya", "Montmeló", "ES", "Europe/Madrid", "14.03.2027", 360),
    ("le-castellet", "4 Stunden von Le Castellet", "Circuit Paul Ricard", "Le Castellet", "FR", "Europe/Paris", "02.05.2027", 240),
    ("imola", "4 Stunden von Imola", "Autodromo Enzo e Dino Ferrari", "Imola", "IT", "Europe/Rome", "04.07.2027", 240),
    ("spa", "4 Stunden von Spa-Francorchamps", "Spa-Francorchamps", "Spa", "BE", "Europe/Brussels", "22.08.2027", 240),
    ("silverstone", "4 Stunden von Silverstone", "Silverstone", "Silverstone", "GB", "Europe/London", "05.09.2027", 240),
    ("portimao", "4 Stunden von Portimão", "Autódromo Internacional do Algarve", "Portimão", "PT", "Europe/Lisbon", "02.10.2027", 240),
]:
    event("elms", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen", at(d(date), "12:00"), minutes, False),
    ], ELMS_SRC, note="Datum offiziell, Startzeit provisorisch")

# ---------------------------------------------------------------------------
# GT World Challenge Europe 2027 (Endurance Cup + Sprint Cup)
# ---------------------------------------------------------------------------
GTWC_SRC = ["https://www.speedweek.com/en/a/sportscar/gt-world-challenge-europe-announces-race-calendar-for-2027",
            "https://www.gt-world-challenge-europe.com"]
for slug, name, circuit, loc, cc, tz, date, start, minutes in [
    ("paul-ricard", "Paul Ricard (Endurance)", "Circuit Paul Ricard", "Le Castellet", "FR", "Europe/Paris", "18.04.2027", "12:00", 360),
    ("imola", "Imola (Endurance)", "Autodromo Enzo e Dino Ferrari", "Imola", "IT", "Europe/Rome", "23.05.2027", "14:30", 180),
    ("spa", "24 Stunden von Spa", "Spa-Francorchamps", "Spa", "BE", "Europe/Brussels", "26.06.2027", "16:30", 1440),
    ("nuerburgring", "Nürburgring (Endurance)", "Nürburgring GP-Strecke", "Nürburg", "DE", "Europe/Berlin", "29.08.2027", "14:30", 180),
    ("barcelona", "Barcelona (Endurance)", "Circuit de Barcelona-Catalunya", "Montmeló", "ES", "Europe/Madrid", "24.10.2027", "14:30", 180),
]:
    event("gtwc", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen", at(d(date), start), minutes, False),
    ], GTWC_SRC, note="Datum offiziell, Startzeit provisorisch")
for slug, name, circuit, loc, cc, tz, saturday in [
    ("brands-hatch", "Brands Hatch (Sprint)", "Brands Hatch", "Kent", "GB", "Europe/London", "01.05.2027"),
    ("misano", "Misano (Sprint)", "Misano World Circuit", "Misano Adriatico", "IT", "Europe/Rome", "17.07.2027"),
    ("magny-cours", "Magny-Cours (Sprint)", "Circuit de Nevers Magny-Cours", "Magny-Cours", "FR", "Europe/Paris", "31.07.2027"),
    ("zandvoort", "Zandvoort (Sprint)", "Circuit Zandvoort", "Zandvoort", "NL", "Europe/Amsterdam", "18.09.2027"),
    ("hungaroring", "Hungaroring (Sprint)", "Hungaroring", "Budapest", "HU", "Europe/Budapest", "02.10.2027"),
]:
    sat = d(saturday)
    event("gtwc", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen 1", at(sat, "15:30"), 60, False),
        ("race", "Rennen 2", at(sat + timedelta(days=1), "14:15"), 60, False),
    ], GTWC_SRC, note="Datum offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# BTCC 2027 (Qualifying Samstag, drei Rennen Sonntag)
# ---------------------------------------------------------------------------
BTCC_SRC = ["https://en.wikipedia.org/wiki/2027_British_Touring_Car_Championship", "https://www.btcc.net"]
for slug, name, circuit, loc, saturday in [
    ("donington", "BTCC Donington Park", "Donington Park (National)", "Castle Donington", "10.04.2027"),
    ("brands-hatch-indy", "BTCC Brands Hatch Indy", "Brands Hatch (Indy)", "Kent", "08.05.2027"),
    ("snetterton", "BTCC Snetterton", "Snetterton 300", "Norfolk", "29.05.2027"),
    ("oulton-park", "BTCC Oulton Park", "Oulton Park (Island)", "Cheshire", "12.06.2027"),
    ("thruxton", "BTCC Thruxton", "Thruxton", "Hampshire", "24.07.2027"),
    ("knockhill", "BTCC Knockhill", "Knockhill", "Fife", "07.08.2027"),
    ("croft", "BTCC Croft", "Croft", "North Yorkshire", "14.08.2027"),
    ("donington-gp", "BTCC Donington Park GP", "Donington Park (GP)", "Castle Donington", "11.09.2027"),
    ("silverstone", "BTCC Silverstone", "Silverstone (National)", "Silverstone", "25.09.2027"),
    ("brands-hatch-gp", "BTCC Finale Brands Hatch", "Brands Hatch (GP)", "Kent", "09.10.2027"),
]:
    sat = d(saturday)
    sun = sat + timedelta(days=1)
    event("btcc", slug, name, circuit, loc, "GB", "Europe/London", [
        ("qualifying", "Qualifying", at(sat, "15:30"), 30, False),
        ("race", "Rennen 1", at(sun, "11:30"), 40, False),
        ("race", "Rennen 2", at(sun, "14:15"), 40, False),
        ("race", "Rennen 3", at(sun, "16:45"), 40, False),
    ], BTCC_SRC, note="Datum offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# Supercars – Rest 2026 (Kalender 2027 noch nicht veröffentlicht)
# ---------------------------------------------------------------------------
SC_SRC = ["https://en.wikipedia.org/wiki/2026_Supercars_Championship", "https://www.supercars.com"]
event("supercars", "gold-coast", "Gold Coast 500", "Surfers Paradise Street Circuit", "Surfers Paradise", "AU", "Australia/Brisbane", [
    ("race", "Rennen 1", at(d("24.10.2026"), "14:30"), 120, False),
    ("race", "Rennen 2", at(d("25.10.2026"), "14:30"), 120, False),
], SC_SRC, note="Datum offiziell, Startzeiten provisorisch")
event("supercars", "sandown", "Sandown 500", "Sandown Raceway", "Melbourne", "AU", "Australia/Melbourne", [
    ("race", "Rennen", at(d("08.11.2026"), "11:30"), 210, False),
], SC_SRC, note="Datum offiziell, Startzeit provisorisch")
event("supercars", "adelaide", "Adelaide Grand Final", "Adelaide Street Circuit", "Adelaide", "AU", "Australia/Adelaide", [
    ("race", "Rennen 1", at(d("28.11.2026"), "14:30"), 120, False),
    ("race", "Rennen 2", at(d("29.11.2026"), "14:30"), 120, False),
], SC_SRC, note="Datum offiziell, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# NASCAR Cup Series (Zeiten in US-Ostküstenzeit)
# ---------------------------------------------------------------------------
NASCAR_2026_SRC = ["https://en.wikipedia.org/wiki/2026_NASCAR_Cup_Series", "https://www.nascar.com/news-media/2025/11/12/nascar-announces-start-times-networks-for-2026-national-series-races/"]
for slug, name, circuit, loc, date, start, confirmed in [
    ("phoenix", "Freeway Insurance 500", "Phoenix Raceway", "Avondale", "18.10.2026", "15:00", False),
    ("talladega", "YellaWood 500", "Talladega Superspeedway", "Lincoln", "25.10.2026", "14:00", True),
    ("martinsville", "Xfinity 500", "Martinsville Speedway", "Ridgeway", "01.11.2026", "14:00", True),
    ("homestead", "Straight Talk Wireless 400 (Finale)", "Homestead-Miami Speedway", "Homestead", "08.11.2026", "15:00", True),
]:
    event("nascar", slug, name, circuit, loc, "US", "America/New_York", [
        ("race", "Rennen", at(d(date), start), 210, confirmed),
    ], NASCAR_2026_SRC, note=None if confirmed else "Startzeit provisorisch")

NASCAR_2027_SRC = ["https://en.wikipedia.org/wiki/2027_NASCAR_Cup_Series", "https://www.nascar.com"]
for slug, name, circuit, loc, date, start, minutes in [
    ("clash", "Clash at Daytona (Showrennen)", "Daytona International Speedway", "Daytona Beach", "13.02.2027", "20:00", 150),
    ("daytona-500", "Daytona 500", "Daytona International Speedway", "Daytona Beach", "21.02.2027", "14:30", 240),
    ("atlanta", "Autotrader 400", "EchoPark Speedway", "Hampton", "28.02.2027", None, None),
    ("cota", "DuraMAX Grand Prix", "Circuit of the Americas", "Austin", "07.03.2027", "15:30", 180),
    ("phoenix", "Straight Talk Wireless 500", "Phoenix Raceway", "Avondale", "14.03.2027", "15:30", None),
    ("las-vegas", "Pennzoil 400", "Las Vegas Motor Speedway", "Las Vegas", "21.03.2027", "15:30", None),
    ("darlington", "Goodyear 400", "Darlington Raceway", "Darlington", "04.04.2027", None, None),
    ("bristol", "Food City 500", "Bristol Motor Speedway", "Bristol", "11.04.2027", None, None),
    ("martinsville", "Cook Out 400", "Martinsville Speedway", "Ridgeway", "18.04.2027", None, None),
    ("talladega", "Jack Link's 500", "Talladega Superspeedway", "Lincoln", "25.04.2027", None, None),
    ("texas", "Würth 400", "Texas Motor Speedway", "Fort Worth", "02.05.2027", None, None),
    ("kansas", "AdventHealth 400", "Kansas Speedway", "Kansas City", "09.05.2027", None, None),
    ("dover", "Dover 400", "Dover Motor Speedway", "Dover", "16.05.2027", None, None),
    ("all-star", "All-Star Race (Showrennen)", "North Wilkesboro Speedway", "North Wilkesboro", "23.05.2027", "20:00", 150),
    ("charlotte", "Coca-Cola 600", "Charlotte Motor Speedway", "Concord", "30.05.2027", "18:00", 270),
    ("nashville", "Cracker Barrel 400", "Nashville Superspeedway", "Lebanon", "06.06.2027", None, None),
    ("pocono", "Great American Getaway 400", "Pocono Raceway", "Long Pond", "13.06.2027", None, None),
    ("michigan", "FireKeepers Casino 400", "Michigan International Speedway", "Brooklyn", "20.06.2027", None, None),
    ("chicagoland", "eero 400", "Chicagoland Speedway", "Joliet", "27.06.2027", None, None),
    ("iowa", "Iowa Corn 350", "Iowa Speedway", "Newton", "04.07.2027", None, None),
    ("sonoma", "Toyota/Save Mart 350", "Sonoma Raceway", "Sonoma", "11.07.2027", "15:30", 180),
    ("atlanta-2", "Dollar Tree 400", "EchoPark Speedway", "Hampton", "18.07.2027", None, None),
    ("indianapolis", "Brickyard 400", "Indianapolis Motor Speedway", "Speedway", "25.07.2027", "14:00", None),
    ("san-diego", "Anduril 250", "Coronado Street Course", "San Diego", "01.08.2027", "15:30", 180),
    ("bristol-night", "Bass Pro Shops Night Race", "Bristol Motor Speedway", "Bristol", "14.08.2027", None, None),
    ("gateway", "Enjoy Illinois 300", "World Wide Technology Raceway", "Madison", "22.08.2027", None, None),
    ("daytona-night", "Coke Zero Sugar 400", "Daytona International Speedway", "Daytona Beach", "28.08.2027", None, None),
    ("southern-500", "Southern 500", "Darlington Raceway", "Darlington", "05.09.2027", "18:00", 240),
    ("richmond", "Cook Out 400", "Richmond Raceway", "Richmond", "11.09.2027", None, None),
    ("watkins-glen", "Go Bowling at The Glen", "Watkins Glen International", "Watkins Glen", "19.09.2027", None, 180),
    ("new-hampshire", "Dollar Tree 301", "New Hampshire Motor Speedway", "Loudon", "26.09.2027", "14:00", None),
    ("kansas-2", "Hollywood Casino 400", "Kansas Speedway", "Kansas City", "03.10.2027", None, None),
    ("las-vegas-2", "South Point 400", "Las Vegas Motor Speedway", "Las Vegas", "10.10.2027", "17:30", None),
    ("charlotte-roval", "Bank of America 400", "Charlotte Motor Speedway (Roval)", "Concord", "17.10.2027", "14:00", 180),
    ("phoenix-2", "Freeway Insurance 500", "Phoenix Raceway", "Avondale", "24.10.2027", "15:00", None),
    ("talladega-2", "YellaWood 500", "Talladega Superspeedway", "Lincoln", "31.10.2027", "14:00", None),
    ("martinsville-2", "Xfinity 500", "Martinsville Speedway", "Ridgeway", "07.11.2027", "14:00", None),
    ("homestead", "Straight Talk Wireless 400 (Finale)", "Homestead-Miami Speedway", "Homestead", "14.11.2027", "15:00", None),
]:
    day = d(date)
    # Standard: Samstag 19:30 (Nachtrennen), sonst 15:00 Ostküstenzeit
    start = start or ("19:30" if day.weekday() == 5 else "15:00")
    event("nascar", slug, name, circuit, loc, "US", "America/New_York", [
        ("race", "Rennen", at(day, start), minutes or 210, False),
    ], NASCAR_2027_SRC, note="Datum offiziell, Startzeit provisorisch")

# ---------------------------------------------------------------------------
# Moto2 / Moto3 – gleiche Wochenenden wie MotoGP, Rennen am Sonntag vor der MotoGP
# ---------------------------------------------------------------------------
for series, offset in [("moto3", -3.0), ("moto2", -1.75)]:
    for slug, name, circuit, loc, cc, tz, raceday, _sprint, race, _confirmed in MOTOGP:
        rday = d(raceday)
        event(series, slug, name, circuit, loc, cc, tz, [
            ("race", "Rennen", shift(at(rday, race), offset), 40, False),
        ], MOTOGP_2026_SRC if rday.year == 2026 else MOTOGP_2027_SRC,
            note="Startzeit provisorisch (abgeleitet vom MotoGP-Zeitplan)")

# ---------------------------------------------------------------------------
# Superbike-WM 2027 (provisorisch): Rennen 1 Sa, Superpole-Rennen + Rennen 2 So
# ---------------------------------------------------------------------------
SBK_SRC = ["https://www.cyclenews.com/2026/10/article/2027-fim-world-superbike-calendar/", "https://www.worldsbk.com"]
for slug, circuit, loc, cc, tz, friday in [
    ("phillip-island", "Phillip Island", "Phillip Island", "AU", "Australia/Melbourne", "19.02.2027"),
    ("portimao", "Autódromo Internacional do Algarve", "Portimão", "PT", "Europe/Lisbon", "19.03.2027"),
    ("valencia", "Circuit Ricardo Tormo", "Valencia", "ES", "Europe/Madrid", "02.04.2027"),
    ("assen", "TT Circuit Assen", "Assen", "NL", "Europe/Amsterdam", "16.04.2027"),
    ("aragon", "MotorLand Aragón", "Alcañiz", "ES", "Europe/Madrid", "21.05.2027"),
    ("most", "Autodrom Most", "Most", "CZ", "Europe/Prague", "04.06.2027"),
    ("misano", "Misano World Circuit", "Misano Adriatico", "IT", "Europe/Rome", "18.06.2027"),
    ("donington", "Donington Park", "Castle Donington", "GB", "Europe/London", "09.07.2027"),
    ("magny-cours", "Circuit de Nevers Magny-Cours", "Magny-Cours", "FR", "Europe/Paris", "03.09.2027"),
    ("cremona", "Cremona Circuit", "San Martino del Lago", "IT", "Europe/Rome", "24.09.2027"),
    ("estoril", "Circuito do Estoril", "Estoril", "PT", "Europe/Lisbon", "15.10.2027"),
    ("shanghai", "Shanghai International Circuit", "Shanghai", "CN", "Asia/Shanghai", "29.10.2027"),
]:
    sat = d(friday) + timedelta(days=1)
    sun = sat + timedelta(days=1)
    event("wsbk", slug, f"WorldSBK {loc}", circuit, loc, cc, tz, [
        ("race", "Rennen 1", at(sat, "14:00"), 40, False),
        ("sprint", "Superpole-Rennen", at(sun, "11:00"), 20, False),
        ("race", "Rennen 2", at(sun, "14:00"), 40, False),
    ], SBK_SRC, note="Kalender provisorisch, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# Isle of Man TT 2027 (Renntage laut Veranstalter; Zeiten wetterabhängig)
# ---------------------------------------------------------------------------
TT_SRC = ["https://www.iomttraces.com/latest/news/tt-2027-dates-isle-of-man-tt-races/",
          "https://the-race.com/tt/isle-of-man-tt-2027-schedule-changes"]
event("iomtt", "races", "Isle of Man TT", "Snaefell Mountain Course", "Douglas", "IM", "Europe/Isle_of_Man", [
    ("race", "Superbike TT", at(d("05.06.2027"), "10:45"), 115, False),
    ("race", "Supersport TT 1", at(d("06.06.2027"), "10:45"), 75, False),
    ("race", "Superstock TT", at(d("08.06.2027"), "10:45"), 75, False),
    ("race", "Sidecar TT 1", at(d("08.06.2027"), "14:00"), 45, False),
    ("race", "Supersport TT 2", at(d("09.06.2027"), "10:45"), 75, False),
    ("race", "Sportbike TT 1", at(d("09.06.2027"), "14:00"), 80, False),
    ("race", "Senior TT", at(d("11.06.2027"), "10:45"), 115, False),
    ("race", "Sidecar TT 2", at(d("12.06.2027"), "10:45"), 45, False),
    ("race", "Sportbike TT 2", at(d("12.06.2027"), "14:00"), 80, False),
], TT_SRC, note="Renntage offiziell, Startzeiten provisorisch und wetterabhängig")

# ---------------------------------------------------------------------------
# Motocross-WM 2027 (provisorisch) – zwei MXGP-Läufe am Sonntag
# ---------------------------------------------------------------------------
MXGP_SRC = ["https://www.fim-moto.com/en/news/news-detail/article/provisional-2027-fim-motorcross-world-championship-calendar-announced"]
for slug, name, circuit, loc, cc, tz, date in [
    ("andalusien", "MXGP von Andalusien", "Motocross-Strecke Almonte", "Almonte", "ES", "Europe/Madrid", "28.02.2027"),
    ("argentinien", "MXGP von Argentinien", "Motocross-Strecke Bariloche", "Bariloche", "AR", "America/Argentina/Buenos_Aires", "14.03.2027"),
    ("italien", "MXGP von Italien", "Motocross-Strecke Montevarchi", "Montevarchi", "IT", "Europe/Rome", "28.03.2027"),
    ("sardinien", "MXGP von Sardinien", "Motocross-Strecke Riola Sardo", "Riola Sardo", "IT", "Europe/Rome", "04.04.2027"),
    ("spanien", "MXGP von Spanien", "Strecke noch offen", "Spanien", "ES", "Europe/Madrid", "18.04.2027"),
    ("trentino", "MXGP von Trentino", "Motocross-Strecke Pietramurata", "Pietramurata", "IT", "Europe/Rome", "25.04.2027"),
    ("china", "MXGP von China", "Motocross-Strecke Shanghai", "Shanghai", "CN", "Asia/Shanghai", "02.05.2027"),
    ("portugal", "MXGP von Portugal", "Strecke noch offen", "Portugal", "PT", "Europe/Lisbon", "23.05.2027"),
    ("frankreich", "MXGP von Frankreich", "Motocross-Strecke Saint-Jean-d'Angély", "Saint-Jean-d'Angély", "FR", "Europe/Paris", "30.05.2027"),
    ("lettland", "MXGP von Lettland", "Motocross-Strecke Ķegums", "Ķegums", "LV", "Europe/Riga", "13.06.2027"),
    ("deutschland", "MXGP von Deutschland", "Motocross-Strecke Teutschenthal", "Teutschenthal", "DE", "Europe/Berlin", "20.06.2027"),
    ("grossbritannien", "MXGP von Grossbritannien", "Foxhills", "Foxhills", "GB", "Europe/London", "27.06.2027"),
    ("tschechien", "MXGP von Tschechien", "Motocross-Strecke Loket", "Loket", "CZ", "Europe/Prague", "25.07.2027"),
    ("flandern", "MXGP von Flandern", "Motocross-Strecke Lommel", "Lommel", "BE", "Europe/Brussels", "01.08.2027"),
    ("schweden", "MXGP von Schweden", "Motocross-Strecke Uddevalla", "Uddevalla", "SE", "Europe/Stockholm", "15.08.2027"),
    ("niederlande", "MXGP der Niederlande", "Motocross-Strecke Arnhem", "Arnhem", "NL", "Europe/Amsterdam", "22.08.2027"),
    ("tuerkei", "MXGP der Türkei", "Motocross-Strecke Afyonkarahisar", "Afyonkarahisar", "TR", "Europe/Istanbul", "05.09.2027"),
    ("australien", "MXGP von Australien", "Motocross-Strecke Darwin", "Darwin", "AU", "Australia/Darwin", "19.09.2027"),
    ("schweiz", "MXGP der Schweiz", "Strecke noch offen", "Schweiz", "CH", "Europe/Zurich", "03.10.2027"),
]:
    day = d(date)
    event("mxgp", slug, name, circuit, loc, cc, tz, [
        ("race", "MXGP Lauf 1", at(day, "14:10"), 40, False),
        ("race", "MXGP Lauf 2", at(day, "17:10"), 40, False),
    ], MXGP_SRC, note="Kalender provisorisch, Startzeiten provisorisch")
event("mxgp", "nations", "Motocross der Nationen", "TT Circuit Assen", "Assen", "NL", "Europe/Amsterdam", [
    ("race", "Lauf 1", at(d("10.10.2027"), "11:30"), 40, False),
    ("race", "Lauf 2", at(d("10.10.2027"), "14:15"), 40, False),
    ("race", "Lauf 3", at(d("10.10.2027"), "15:45"), 40, False),
], MXGP_SRC, note="Datum provisorisch, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# Supercross 2027 – Samstagabend, Night Show
# ---------------------------------------------------------------------------
SX_SRC = ["https://ultimatemotorcycling.com/2026/10/03/2027-supercross-schedule-17-rounds-dates-venues-tickets/",
          "https://www.supercrossonline.com"]
for slug, name, stadium, loc, tz, date in [
    ("anaheim-1", "Anaheim 1", "Angel Stadium", "Anaheim", "America/Los_Angeles", "09.01.2027"),
    ("san-diego", "San Diego", "Snapdragon Stadium", "San Diego", "America/Los_Angeles", "16.01.2027"),
    ("anaheim-2", "Anaheim 2", "Angel Stadium", "Anaheim", "America/Los_Angeles", "23.01.2027"),
    ("san-antonio", "San Antonio", "Alamodome", "San Antonio", "America/Chicago", "30.01.2027"),
    ("tampa", "Tampa", "Raymond James Stadium", "Tampa", "America/New_York", "06.02.2027"),
    ("glendale", "Glendale", "State Farm Stadium", "Glendale", "America/Phoenix", "13.02.2027"),
    ("detroit", "Detroit", "Ford Field", "Detroit", "America/Detroit", "20.02.2027"),
    ("arlington", "Arlington", "AT&T Stadium", "Arlington", "America/Chicago", "27.02.2027"),
    ("daytona", "Daytona", "Daytona International Speedway", "Daytona Beach", "America/New_York", "06.03.2027"),
    ("indianapolis", "Indianapolis", "Lucas Oil Stadium", "Indianapolis", "America/Indiana/Indianapolis", "13.03.2027"),
    ("seattle", "Seattle", "Lumen Field", "Seattle", "America/Los_Angeles", "20.03.2027"),
    ("foxborough", "Foxborough", "Gillette Stadium", "Foxborough", "America/New_York", "03.04.2027"),
    ("baltimore", "Baltimore", "M&T Bank Stadium", "Baltimore", "America/New_York", "10.04.2027"),
    ("east-rutherford", "East Rutherford", "MetLife Stadium", "East Rutherford", "America/New_York", "17.04.2027"),
    ("pittsburgh", "Pittsburgh", "Acrisure Stadium", "Pittsburgh", "America/New_York", "24.04.2027"),
    ("denver", "Denver", "Empower Field at Mile High", "Denver", "America/Denver", "08.05.2027"),
    ("salt-lake-city", "Salt Lake City (Finale)", "Rice-Eccles Stadium", "Salt Lake City", "America/Denver", "15.05.2027"),
]:
    event("supercross", slug, f"Supercross {name}", stadium, loc, "US", tz, [
        ("race", "Night Show", at(d(date), "19:00"), 180, False),
    ], SX_SRC, note="Datum offiziell, Startzeit provisorisch")

# ---------------------------------------------------------------------------
# Rallye-WM 2027 (provisorisch): erster voller Tag + Power Stage
# ---------------------------------------------------------------------------
WRC_SRC = ["https://en.wikipedia.org/wiki/2027_World_Rally_Championship", "https://www.wrc.com"]
for slug, name, base, cc, tz, first, last in [
    ("monte-carlo", "Rallye Monte-Carlo", "Gap", "MC", "Europe/Paris", "21.01.2027", "24.01.2027"),
    ("schweden", "Rallye Schweden", "Umeå", "SE", "Europe/Stockholm", "18.02.2027", "21.02.2027"),
    ("kenia", "Safari Rallye Kenia", "Nairobi", "KE", "Africa/Nairobi", "18.03.2027", "21.03.2027"),
    ("kroatien", "Rallye Kroatien", "Rijeka", "HR", "Europe/Zagreb", "08.04.2027", "11.04.2027"),
    ("kanaren", "Rallye Islas Canarias", "Las Palmas", "ES", "Atlantic/Canary", "06.05.2027", "09.05.2027"),
    ("japan", "Rallye Japan", "Toyota (Aichi)", "JP", "Asia/Tokyo", "03.06.2027", "06.06.2027"),
    ("akropolis", "Akropolis-Rallye", "Loutraki", "GR", "Europe/Athens", "24.06.2027", "27.06.2027"),
    ("italien", "Rallye Italien (Rom)", "Rom", "IT", "Europe/Rome", "08.07.2027", "11.07.2027"),
    ("estland", "Rallye Estland", "Tartu", "EE", "Europe/Tallinn", "22.07.2027", "25.07.2027"),
    ("finnland", "Rallye Finnland", "Jyväskylä", "FI", "Europe/Helsinki", "29.07.2027", "01.08.2027"),
    ("usa", "Rallye USA", "Knoxville", "US", "America/New_York", "26.08.2027", "29.08.2027"),
    ("schottland", "Rallye Schottland", "Aberdeen", "GB", "Europe/London", "30.09.2027", "03.10.2027"),
    ("paraguay", "Rallye Paraguay", "Encarnación", "PY", "America/Asuncion", "21.10.2027", "24.10.2027"),
    ("chile", "Rallye Chile", "Concepción", "CL", "America/Santiago", "04.11.2027", "07.11.2027"),
    ("saudi-arabien", "Rallye Saudi-Arabien", "Dschidda", "SA", "Asia/Riyadh", "25.11.2027", "28.11.2027"),
]:
    event("wrc", slug, name, "Wertungsprüfungen", base, cc, tz, [
        ("race", "Erster voller Rallye-Tag", at(d(first) + timedelta(days=1), "08:00"), 600, False),
        ("race", "Power Stage", at(d(last), "13:15"), 30, False),
    ], WRC_SRC, note="Kalender provisorisch, Startzeiten provisorisch")

# ---------------------------------------------------------------------------
# Rallye Dakar 2027: 1.–15. Januar, Prolog + 13 Etappen + 1 Ruhetag
# ---------------------------------------------------------------------------
DAKAR_SRC = ["https://www.x-raid.de/en/x-raid-looking-forward-to-dakar-2027-route-announced/", "https://www.dakar.com"]
event("dakar", "rallye", "Rallye Dakar 2027", "Start & Ziel King Abdullah Economic City", "KAEC (bei Dschidda)", "SA", "Asia/Riyadh", [
    ("qualifying", "Prolog", at(d("01.01.2027"), "10:00"), 60, False),
    ("race", "Etappe 1", at(d("02.01.2027"), "07:00"), 480, False),
    ("race", "Schlussetappe", at(d("15.01.2027"), "08:00"), 240, False),
], DAKAR_SRC, note="Zeitraum offiziell (1.–15. Januar), Etappenzeiten provisorisch")

# ---------------------------------------------------------------------------
# Pikes Peak International Hill Climb 2027
# ---------------------------------------------------------------------------
event("pikespeak", "race-day", "105. Pikes Peak International Hill Climb", "Pikes Peak Highway", "Colorado Springs", "US", "America/Denver", [
    ("race", "Renntag", at(d("27.06.2027"), "08:00"), 480, False),
], ["https://ppihc.org"], note="Datum offiziell, Startzeit provisorisch")


# ===========================================================================
# Erweiterung vom 18.10.2026: ADAC- und Porsche-Cups, Macau
# ===========================================================================

# ADAC GT Masters 2027: Lauf 1 Sa, Lauf 2 So (je 60 Min.), fünfmal im DTM-Rahmen
GTM_SRC = ["https://de.wikipedia.org/wiki/ADAC_GT_Masters_2027",
           "https://www.motorsport-total.com/gt-masters/news/adac-gt-masters-praesentiert-kalender-2027-und-aenderungen-am-rennformat-26100203"]
for slug, name, circuit, loc, cc, tz, saturday in [
    ("spielberg", "GT Masters Spielberg", "Red Bull Ring", "Spielberg", "AT", "Europe/Vienna", "24.04.2027"),
    ("lausitzring", "GT Masters Lausitzring", "Lausitzring", "Klettwitz", "DE", "Europe/Berlin", "19.06.2027"),
    ("nuerburgring", "GT Masters Nürburgring", "Nürburgring GP-Strecke", "Nürburg", "DE", "Europe/Berlin", "10.07.2027"),
    ("zandvoort", "GT Masters Zandvoort", "Circuit Zandvoort", "Zandvoort", "NL", "Europe/Amsterdam", "07.08.2027"),
    ("sachsenring", "GT Masters Sachsenring", "Sachsenring", "Hohenstein-Ernstthal", "DE", "Europe/Berlin", "25.09.2027"),
    ("hockenheim", "GT Masters Finale Hockenheim", "Hockenheimring", "Hockenheim", "DE", "Europe/Berlin", "09.10.2027"),
]:
    sat = d(saturday)
    event("gtmasters", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen 1", at(sat, "11:15"), 60, False),
        ("race", "Rennen 2", at(sat + timedelta(days=1), "11:15"), 60, False),
    ], GTM_SRC, note="Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch")

# Porsche Carrera Cup Deutschland 2027: zwei Sprints à 30 Min. + 1 Runde
# Monza (International GT Open) ist angekündigt, aber noch ohne Datum.
CCD_SRC = ["https://ran.joyn.de/sports/motorsport/porsche-sixt-carrera-cup-deutschland/porsche-sixt-carrera-cup-deutschland-titelentscheidung-auf-dem-hockenheimring-rennkalender-fuer2027-steht-fest-197075",
           "https://racing.porsche.com/series/carrera-cup-deutschland"]
for slug, name, circuit, loc, cc, tz, saturday, sat_time, sun_time in [
    ("imola", "Carrera Cup Imola", "Autodromo Enzo e Dino Ferrari", "Imola", "IT", "Europe/Rome", "10.04.2027", "14:00", "09:30"),
    ("spielberg", "Carrera Cup Spielberg", "Red Bull Ring", "Spielberg", "AT", "Europe/Vienna", "24.04.2027", "10:50", "12:30"),
    ("norisring", "Carrera Cup Norisring", "Norisring", "Nürnberg", "DE", "Europe/Berlin", "03.07.2027", "10:50", "12:30"),
    ("zandvoort", "Carrera Cup Zandvoort", "Circuit Zandvoort", "Zandvoort", "NL", "Europe/Amsterdam", "07.08.2027", "10:50", "12:30"),
    ("nuerburgring", "Carrera Cup Nürburgring", "Nürburgring GP-Strecke", "Nürburg", "DE", "Europe/Berlin", "21.08.2027", "10:50", "12:30"),
    ("sachsenring", "Carrera Cup Sachsenring", "Sachsenring", "Hohenstein-Ernstthal", "DE", "Europe/Berlin", "25.09.2027", "10:50", "12:30"),
    ("hockenheim", "Carrera Cup Finale Hockenheim", "Hockenheimring", "Hockenheim", "DE", "Europe/Berlin", "09.10.2027", "10:50", "12:30"),
]:
    sat = d(saturday)
    event("carreracup", slug, name, circuit, loc, cc, tz, [
        ("race", "Rennen 1", at(sat, sat_time), 35, False),
        ("race", "Rennen 2", at(sat + timedelta(days=1), sun_time), 35, False),
    ], CCD_SRC, note="Daten aus dem DTM- bzw. WEC-Kalender, Startzeiten provisorisch")

# Porsche Supercup 2027 (vorläufig): Rennen am F1-Renntag, ca. 3:45 Std. vor dem Grand Prix
PSC_SRC = ["https://soymotor.com/competicion/noticias/la-porsche-supercup-confirma-su-calendario-de-2027-con-una-carrera-en-madring",
           "https://racing.porsche.com/mobil-1-supercup"]
for slug in ["monaco", "portugal", "oesterreich", "belgien", "ungarn", "italien", "spanien", "tuerkei"]:
    _, _, circuit, loc, cc, tz, raceday, race, _, _ = F1_LOOKUP[slug]
    event("supercup", slug, f"Supercup {loc}", circuit, loc, cc, tz, [
        ("race", "Rennen", shift(at(d(raceday), race), -3.75), 30, False),
    ], PSC_SRC, note="Kalender vorläufig, Startzeit provisorisch")

# Macau Grand Prix 2026 (19.–22. November): FIA GT World Cup + Formel-Regional-Weltcup
event("macau", "grand-prix", "73. Macau Grand Prix", "Guia Circuit", "Macau", "MO", "Asia/Macau", [
    ("sprint", "GT World Cup · Qualifikationsrennen", at(d("21.11.2026"), "12:30"), 40, False),
    ("race", "GT World Cup · Hauptrennen", at(d("22.11.2026"), "11:30"), 60, False),
    ("race", "Formel Regional · Grand Prix", at(d("22.11.2026"), "15:30"), 60, False),
], ["https://www.dailysportscar.com/2025/12/10/2026-fia-gt-world-cup-date-set.html",
    "https://www.macau.grandprix.gov.mo"], note="Datum offiziell, Startzeiten provisorisch")


# Offizielle Ticketshops (nur offizielle Shops der Serie bzw. des Veranstalters)
F1_TICKETS = "https://tickets.formula1.com"
TICKETS = {
    "f1": F1_TICKETS, "f2": F1_TICKETS, "f3": F1_TICKETS, "f1academy": F1_TICKETS, "supercup": F1_TICKETS,
    "indycar": "https://www.indycar.com/tickets",
    "fe": "https://www.fiaformulae.com/en/tickets",
    "imsa": "https://www.imsa.com/tickets",
    "gtwc": "https://www.gt-world-challenge-europe.com/tickets",
    "nls": "https://www.nuerburgring-langstrecken-serie.de/tickets",
    "n24": "https://www.24h-rennen.de/tickets/",
    "dtm": "https://www.dtm.com/de/tickets", "gtmasters": "https://www.dtm.com/de/tickets",
    "carreracup": "https://www.dtm.com/de/tickets",
    "macau": "https://www.macau.grandprix.gov.mo",
    "btcc": "https://www.btcc.net/tickets/",
    "supercars": "https://www.supercars.com/tickets",
    "nascar": "https://www.nascar.com/tickets/",
    "motogp": "https://tickets.motogp.com", "moto2": "https://tickets.motogp.com", "moto3": "https://tickets.motogp.com",
    "iomtt": "https://www.iomttraces.com/tickets/",
    "supercross": "https://www.supermotocross.com/tickets",
    "pikespeak": "https://ppihc.org/tickets/",
}
# Einzelne Events mit eigenem Shop (überschreibt den Serien-Shop)
EVENT_TICKETS = {
    "wec-2027-le-mans": "https://www.24h-lemans.com/en/tickets",
    # Carrera Cup NA: Tickets über den Veranstalter des Hauptevents (F1 bzw. IMSA)
    "carreracupna-2026-austin": F1_TICKETS, "carreracupna-2027-austin": F1_TICKETS, "carreracupna-2027-miami": F1_TICKETS,
    **{f"carreracupna-2027-{s}": "https://www.imsa.com/tickets"
       for s in ["daytona", "sebring", "long-beach", "road-america", "road-atlanta"]},
}

# Live-Timing (nur geprüfte Links)
LIVE_TIMING = {
    "f1": "https://www.formula1.com/en/timing/f1-live",
    "indycar": "https://www.indycar.com/timing-and-scoring",
    "fe": "https://www.fiaformulae.com/en/live-timing",
    "wec": "https://fiawec.alkamelsystems.com",
    "imsa": "https://imsa.alkamelsystems.com",
    "elms": "https://elms.alkamelsystems.com",
    "gtwc": "https://www.gt-world-challenge-europe.com/live",
    "nls": "https://livetiming.azurewebsites.net",
    "n24": "https://livetiming.azurewebsites.net",
    "dtm": "https://www.dtm.com/de/livetiming",
    "btcc": "https://www.tsl-timing.com",
    "supercars": "https://www.supercars.com/live-timing",
    "nascar": "https://www.nascar.com/live-leaderboard/",
    "motogp": "https://www.motogp.com/en/live",
    "moto2": "https://www.motogp.com/en/live",
    "moto3": "https://www.motogp.com/en/live",
    "iomtt": "https://www.iomttraces.com/live-timing/",
    "mxgp": "https://www.mxgp.com/live-timing",
    "supercup": "https://racing.porsche.com/mobil-1-supercup/live-timing",
}


# ---------------------------------------------------------------------------
# Kalender-Abos (.ics) für GitHub Pages: pro Serie und pro Favorit
# ---------------------------------------------------------------------------
def _ics_escape(text):
    return text.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")


def _ics_fold(line):
    raw = line.encode("utf-8")
    if len(raw) <= 75:
        return line
    out, current = [], b""
    for ch in line:
        b = ch.encode("utf-8")
        if len(current) + len(b) > (75 if not out else 74):
            out.append(current.decode("utf-8"))
            current = b""
        current += b
    out.append(current.decode("utf-8"))
    return "\r\n ".join(out)


def write_calendars(data):
    CALENDAR_DIR.mkdir(parents=True, exist_ok=True)
    series = {s["id"]: s for s in data["series"]}
    channels = {c["id"]: c for c in data["channels"]}
    stamp = data["updatedAt"].replace("-", "").replace(":", "")

    def calendar(name, events):
        lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Stintly//Renndaten//DE",
                 "CALSCALE:GREGORIAN", "METHOD:PUBLISH", f"X-WR-CALNAME:{_ics_escape(name)}",
                 "X-PUBLISHED-TTL:PT12H", "REFRESH-INTERVAL;VALUE=DURATION:PT12H"]
        for e in events:
            s_info = series[e["seriesId"]]
            ch_ids = e.get("channelIds") or s_info["channelIds"]
            where = " · ".join(channels[c]["name"] for c in ch_ids if c in channels)
            for s in e["sessions"]:
                start = s["start"].replace("-", "").replace(":", "")
                desc = f"Wo schauen: {where}" if where else ""
                if not s["confirmed"]:
                    desc += "\nStartzeit provisorisch"
                if e.get("note"):
                    desc += f"\n{e['note']}"
                lines += ["BEGIN:VEVENT", f"UID:{s['id']}@stintly", f"DTSTAMP:{stamp}", f"DTSTART:{start}",
                          f"DURATION:PT{s['durationMinutes']}M",
                          f"SUMMARY:{_ics_escape(s_info['shortName'] + ' · ' + e['name'] + ' – ' + s['name'])}",
                          f"LOCATION:{_ics_escape(e['circuit'] + ', ' + e['location'])}",
                          f"DESCRIPTION:{_ics_escape(desc.strip())}", "END:VEVENT"]
        lines.append("END:VCALENDAR")
        return "\r\n".join(_ics_fold(l) for l in lines) + "\r\n"

    for s in data["series"]:
        evs = [e for e in data["events"] if e["seriesId"] == s["id"]]
        (CALENDAR_DIR / f"{s['id']}.ics").write_text(calendar(f"Stintly · {s['name']}", evs), encoding="utf-8")
        s["calendarUrl"] = f"{SITE}/calendar/{s['id']}.ics"

# Porsche Carrera Cup North America (zwei Rennen pro Wochenende, je ca. 40 Min.)
CCNA_SRC = ["https://racing.porsche.com/en-US/articles/pccna-2027-calendar-announcement",
            "https://newsroom.porsche.com/en_US/2025/motorsport/2026-porsche-carrera-cup-north-america-calendar-unveiled.html"]
for slug, name, circuit, loc, tz, day1, t1, day2, t2, note in [
    ("austin", "Carrera Cup NA Austin (Finale)", "Circuit of the Americas", "Austin", "America/Chicago",
     "24.10.2026", "11:30", "25.10.2026", "10:00", "Datum offiziell (F1-Rahmenprogramm), Startzeiten provisorisch"),
    ("daytona", "Carrera Cup NA Daytona", "Daytona International Speedway", "Daytona Beach", "America/New_York",
     "28.01.2027", "13:00", "29.01.2027", "11:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("sebring", "Carrera Cup NA Sebring", "Sebring International Raceway", "Sebring", "America/New_York",
     "18.03.2027", "13:00", "19.03.2027", "11:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("long-beach", "Carrera Cup NA Long Beach", "Long Beach Street Circuit", "Long Beach", "America/Los_Angeles",
     "17.04.2027", "11:00", "18.04.2027", "10:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("miami", "Carrera Cup NA Miami", "Miami International Autodrome", "Miami", "America/New_York",
     "01.05.2027", "11:30", "02.05.2027", "10:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("road-america", "Carrera Cup NA Road America", "Road America", "Elkhart Lake", "America/Chicago",
     "06.08.2027", "13:00", "07.08.2027", "11:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("road-atlanta", "Carrera Cup NA Road Atlanta", "Michelin Raceway Road Atlanta", "Braselton", "America/New_York",
     "07.10.2027", "13:00", "08.10.2027", "11:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
    ("austin", "Carrera Cup NA Austin (Finale)", "Circuit of the Americas", "Austin", "America/Chicago",
     "23.10.2027", "11:30", "24.10.2027", "10:00", "Daten offiziell (Änderungen vorbehalten), Startzeiten provisorisch"),
]:
    event("carreracupna", slug, name, circuit, loc, "US", tz, [
        ("race", "Rennen 1", at(d(day1), t1), 40, False),
        ("race", "Rennen 2", at(d(day2), t2), 40, False),
    ], CCNA_SRC, note=note)


# ---------------------------------------------------------------------------
def build():
    events = sorted(EVENTS, key=lambda e: (e["sessions"][0]["start"], e["id"]))
    for e in events:
        e["ticketsUrl"] = EVENT_TICKETS.get(e["id"])
    return {
        "schemaVersion": 1,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "region": "CH",
        "channels": [
            {"id": i, "name": n, "kind": k, "url": u, "note": note}
            for i, n, k, u, note in CHANNELS
        ],
        "series": [
            {"id": i, "name": n, "shortName": s, "category": c, "tagline": tl,
             "color": col, "channelIds": ch, "website": w, "liveTimingUrl": LIVE_TIMING.get(i),
             "ticketsUrl": TICKETS.get(i)}
            for i, n, s, c, tl, col, ch, w in SERIES
        ],
        "events": events,
    }


def main():
    data = build()
    unknown = [e for e in EVENT_TICKETS if not any(ev["id"] == e for ev in data["events"])]
    if unknown:
        raise SystemExit(f"EVENT_TICKETS verweist auf unbekannte Events: {unknown}")
    write_calendars(data)
    missing = translate_data(data)
    if missing:
        print("Hinweis – ohne Übersetzung (App zeigt Deutsch):", ", ".join(missing))
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    for path in OUTPUTS:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    sessions = sum(len(e["sessions"]) for e in data["events"])
    print(f"Geschrieben: {len(data['series'])} Serien, {len(data['events'])} Events, "
          f"{sessions} Sessions, {len(data['channels'])} Sender")


if __name__ == "__main__":
    main()
