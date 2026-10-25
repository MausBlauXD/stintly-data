"""Übersetzungen der Datentexte (Deutsch → Englisch, Französisch, Italienisch).

Die App zeigt die Übersetzung passend zur Gerätesprache und fällt sonst auf Deutsch zurück.
Fehlt eine Übersetzung, ist das kein Fehler – `validate_races.py` meldet es nur als Hinweis.
"""
import re

LANGS = ("en", "fr", "it")


def t(en, fr, it):
    return {"en": en, "fr": fr, "it": it}


TAGLINES = {
    "f1": t("The pinnacle of motorsport", "La catégorie reine", "La classe regina"),
    "f2": t("Stepping stone to F1", "Antichambre de la F1", "Trampolino verso la F1"),
    "f3": t("Junior single-seater series", "Formule de promotion", "Serie formula giovanile"),
    "f1academy": t("All-female single-seater series", "Série de monoplaces féminine", "Serie di monoposto femminile"),
    "indycar": t("Incl. Indy 500", "Avec l'Indy 500", "Con la Indy 500"),
    "fe": t("Electric street racing", "Courses électriques en ville", "Gare elettriche in città"),
    "wec": t("Incl. 24h of Le Mans", "Avec les 24 Heures du Mans", "Con la 24 Ore di Le Mans"),
    "imsa": t("Incl. Daytona 24", "Avec les 24 Heures de Daytona", "Con la 24 Ore di Daytona"),
    "elms": t("4-hour races across Europe", "Courses de 4 heures en Europe", "Gare di 4 ore in Europa"),
    "gtwc": t("Incl. 24h of Spa", "Avec les 24 Heures de Spa", "Con la 24 Ore di Spa"),
    "nls": t("Nordschleife", "Nordschleife", "Nordschleife"),
    "n24": t("Green Hell, 24 hours", "Enfer vert, 24 heures", "Inferno verde, 24 ore"),
    "dtm": t("GT3 sprint races", "Courses sprint GT3", "Gare sprint GT3"),
    "gtmasters": t("GT3 sprints at DTM events", "Sprints GT3 en lever de rideau du DTM", "Sprint GT3 nel weekend DTM"),
    "carreracup": t("One-make cup at DTM events", "Coupe monomarque en lever de rideau du DTM", "Monomarca nel weekend DTM"),
    "supercup": t("One-make cup at F1 events", "Coupe monomarque en lever de rideau de la F1", "Monomarca nel weekend di F1"),
    "carreracupna": t("One-make cup at F1, IMSA and IndyCar events in the US", "Coupe monomarque aux courses F1, IMSA et IndyCar aux États-Unis", "Monomarca nei weekend di F1, IMSA e IndyCar negli USA"),
    "macau": t("GT World Cup on the Guia Circuit", "GT World Cup sur le circuit de Guia", "GT World Cup sul circuito di Guia"),
    "btcc": t("British touring cars", "Voitures de tourisme britanniques", "Turismo britannico"),
    "supercars": t("V8 touring cars from Australia", "Voitures de tourisme V8 australiennes", "Turismo V8 australiane"),
    "nascar": t("Stock cars, incl. Daytona 500", "Stock-cars, avec le Daytona 500", "Stock car, con la Daytona 500"),
    "motogp": t("Motorcycle world championship", "Championnat du monde moto", "Mondiale di motociclismo"),
    "moto2": t("Intermediate class of the world championship", "Catégorie intermédiaire du mondial", "Classe intermedia del mondiale"),
    "moto3": t("Entry class of the world championship", "Catégorie d'entrée du mondial", "Classe d'ingresso del mondiale"),
    "wsbk": t("Production-based superbikes", "Superbikes dérivées de la série", "Superbike derivate di serie"),
    "iomtt": t("Road racing on the Isle of Man", "Courses sur route à l'île de Man", "Corse su strada all'Isola di Man"),
    "mxgp": t("Motocross worldwide", "Motocross dans le monde entier", "Motocross in tutto il mondo"),
    "supercross": t("US stadium racing", "Courses en stade aux États-Unis", "Gare negli stadi USA"),
    "wrc": t("World Rally Championship", "Championnat du monde des rallyes", "Campionato del mondo rally"),
    "dakar": t("Desert rally in Saudi Arabia", "Rallye-raid en Arabie saoudite", "Rally raid in Arabia Saudita"),
    "pikespeak": t("Hill climb in Colorado", "Course de côte au Colorado", "Cronoscalata in Colorado"),
}

CHANNEL_NOTES = {
    "srf2": t("Sometimes on SRF info or SRF 1", "Parfois sur SRF info ou SRF 1", "A volte su SRF info o SRF 1"),
    "playsrf": t("Free live stream in Switzerland", "Livestream gratuit en Suisse", "Livestream gratuito in Svizzera"),
    "sky": t("All sessions, subscription required", "Toutes les sessions, abonnement requis", "Tutte le sessioni, abbonamento necessario"),
    "prosieben": t("Availability in Switzerland depends on your TV provider", "Réception en Suisse selon l'opérateur TV", "Ricezione in Svizzera secondo l'operatore TV"),
    "joyn": t("Free live stream; may be geo-blocked in Switzerland", "Livestream gratuit ; peut être bloqué en Suisse", "Livestream gratuito; può essere bloccato in Svizzera"),
    "yt-vln": t("Official free NLS live stream", "Livestream officiel gratuit de la NLS", "Livestream ufficiale gratuito della NLS"),
    "nls-web": t("Live stream & live timing", "Livestream et chronométrage", "Livestream e cronometraggio"),
    "yt-24h": t("Free live stream", "Livestream gratuit", "Livestream gratuito"),
    "n24-web": t("Live stream & live timing", "Livestream et chronométrage", "Livestream e cronometraggio"),
    "eurosport": t("Usually Eurosport 2, finale often on Eurosport 1", "Surtout Eurosport 2, la fin souvent sur Eurosport 1", "Di solito Eurosport 2, il finale spesso su Eurosport 1"),
    "fiawecplus": t("Official WEC stream", "Stream officiel du WEC", "Stream ufficiale del WEC"),
    "bluetv": t("Swisscom; Formula E partner until season 12", "Swisscom ; partenaire Formule E jusqu'à la saison 12", "Swisscom; partner Formula E fino alla stagione 12"),
    "disneyplus": t("From season 13 per Formula E; Swiss partner still open", "Dès la saison 13 selon la Formule E ; partenaire suisse encore ouvert", "Dalla stagione 13 secondo la Formula E; partner svizzero ancora aperto"),
    "f1tv": t("Official stream incl. F2, F3 and F1 Academy", "Stream officiel avec F2, F3 et F1 Academy", "Stream ufficiale con F2, F3 e F1 Academy"),
    "motorvision": t("IndyCar with German commentary", "IndyCar commenté en allemand", "IndyCar con commento in tedesco"),
    "sportdigital": t("NASCAR Cup live (DACH), availability depends on TV provider", "NASCAR Cup en direct (DACH), selon l'opérateur TV", "NASCAR Cup in diretta (DACH), secondo l'operatore TV"),
    "yt-imsa": t("Free live stream outside North America", "Livestream gratuit hors Amérique du Nord", "Livestream gratuito fuori dal Nord America"),
    "yt-elms": t("Official free live stream", "Livestream officiel gratuit", "Livestream ufficiale gratuito"),
    "yt-gtworld": t("Official free live stream", "Livestream officiel gratuit", "Livestream ufficiale gratuito"),
    "yt-btcc": t("Free live stream outside the UK and North America", "Livestream gratuit hors Royaume-Uni et Amérique du Nord", "Livestream gratuito fuori da Regno Unito e Nord America"),
    "superview": t("International Supercars stream (subscription)", "Stream international des Supercars (abonnement)", "Stream internazionale delle Supercars (abbonamento)"),
    "servustv": t("Free stream in DE/AT/CH", "Stream gratuit en DE/AT/CH", "Stream gratuito in DE/AT/CH"),
    "sbk-pass": t("Official stream, all sessions", "Stream officiel, toutes les sessions", "Stream ufficiale, tutte le sessioni"),
    "ttplus": t("Official Isle of Man TT live stream", "Livestream officiel du TT de l'île de Man", "Livestream ufficiale del TT dell'Isola di Man"),
    "mxgp-tv": t("Official motocross world championship stream", "Stream officiel du mondial de motocross", "Stream ufficiale del mondiale motocross"),
    "smx-pass": t("International Supercross stream", "Stream international du Supercross", "Stream internazionale del Supercross"),
    "rallytv": t("Every WRC stage live", "Toutes les spéciales WRC en direct", "Tutte le prove WRC in diretta"),
    "dakar-web": t("Live tracking & daily highlights", "Suivi en direct et résumés quotidiens", "Tracking live e highlights quotidiani"),
    "yt-ppihc": t("Free live stream", "Livestream gratuit", "Livestream gratuito"),
    "yt-adac": t("Live stream depending on rights", "Livestream selon les droits", "Livestream secondo i diritti"),
    "yt-porsche": t("Live stream depending on rights", "Livestream selon les droits", "Livestream secondo i diritti"),
    "yt-macau": t("Live stream depending on region", "Livestream selon la région", "Livestream secondo la regione"),
}

# Bausteine der Event-Notizen (durch ", " bzw. "; " getrennt)
NOTE_PARTS = {
    "Startzeiten provisorisch": t("start times provisional", "horaires provisoires", "orari provvisori"),
    "Startzeiten noch provisorisch": t("start times still provisional", "horaires encore provisoires", "orari ancora provvisori"),
    "Startzeit provisorisch": t("start time provisional", "horaire provisoire", "orario provvisorio"),
    "Startzeit provisorisch (abgeleitet vom MotoGP-Zeitplan)": t("start time provisional (based on the MotoGP schedule)", "horaire provisoire (d'après le programme MotoGP)", "orario provvisorio (in base al programma MotoGP)"),
    "Startzeiten provisorisch und wetterabhängig": t("start times provisional and weather-dependent", "horaires provisoires et selon la météo", "orari provvisori e legati al meteo"),
    "Etappenzeiten provisorisch": t("stage times provisional", "horaires des étapes provisoires", "orari delle tappe provvisori"),
    "Daten offiziell": t("dates official", "dates officielles", "date ufficiali"),
    "Daten offiziell (Änderungen vorbehalten)": t("dates official (subject to change)", "dates officielles (sous réserve)", "date ufficiali (salvo modifiche)"),
    "Datum offiziell": t("date official", "date officielle", "data ufficiale"),
    "Datum offiziell (27.–30. Mai)": t("date official (27–30 May)", "date officielle (27–30 mai)", "data ufficiale (27–30 maggio)"),
    "Datum offiziell (30. April – 2. Mai)": t("date official (30 April – 2 May)", "date officielle (30 avril – 2 mai)", "data ufficiale (30 aprile – 2 maggio)"),
    "Datum provisorisch": t("date provisional", "date provisoire", "data provvisoria"),
    "Datum laut IndyCar bzw. Medienberichten": t("date per IndyCar or media reports", "date selon IndyCar ou la presse", "data secondo IndyCar o la stampa"),
    "Zeitraum offiziell (1.–15. Januar)": t("dates official (1–15 January)", "période officielle (1er–15 janvier)", "periodo ufficiale (1–15 gennaio)"),
    "Renntage offiziell": t("race days official", "jours de course officiels", "giorni di gara ufficiali"),
    "Kalender provisorisch": t("calendar provisional", "calendrier provisoire", "calendario provvisorio"),
    "Kalender vorläufig": t("calendar preliminary", "calendrier préliminaire", "calendario preliminare"),
    "Daten gemäss F1-Kalender": t("dates per F1 calendar", "dates selon le calendrier F1", "date secondo il calendario F1"),
    "Datum offiziell (F1-Rahmenprogramm)": t("date official (F1 support race)", "date officielle (lever de rideau F1)", "data ufficiale (gara di supporto F1)"),
    "Daten aus dem DTM- bzw. WEC-Kalender": t("dates from the DTM/WEC calendar", "dates selon le calendrier DTM/WEC", "date dal calendario DTM/WEC"),
    "Montreal noch unter Vertragsvorbehalt": t("Montreal still subject to contract", "Montréal encore sous réserve de contrat", "Montréal ancora soggetta a contratto"),
    "AO Racing by Absolute": t("AO Racing by Absolute", "AO Racing by Absolute", "AO Racing by Absolute"),
}

SESSION_NAMES = {
    "Rennen": t("Race", "Course", "Gara"),
    "Qualifying": t("Qualifying", "Qualifications", "Qualifiche"),
    "Sprint": t("Sprint", "Sprint", "Sprint"),
    "Sprintrennen": t("Sprint race", "Course sprint", "Gara sprint"),
    "Hauptrennen": t("Feature race", "Course principale", "Gara principale"),
    "Zeittraining": t("Qualifying", "Essais qualificatifs", "Prove cronometrate"),
    "Top-Qualifying": t("Top qualifying", "Top qualifications", "Top qualifiche"),
    "24h-Rennen": t("24h race", "Course de 24 h", "Gara di 24 ore"),
    "Superpole-Rennen": t("Superpole race", "Course Superpole", "Gara Superpole"),
    "Prolog": t("Prologue", "Prologue", "Prologo"),
    "Schlussetappe": t("Final stage", "Dernière étape", "Tappa finale"),
    "Renntag": t("Race day", "Jour de course", "Giorno di gara"),
    "Erster voller Rallye-Tag": t("First full rally day", "Première journée complète", "Prima giornata completa"),
    "Power Stage": t("Power Stage", "Power Stage", "Power Stage"),
    "Night Show": t("Night Show", "Night Show", "Night Show"),
    "GT World Cup · Hauptrennen": t("GT World Cup · Main race", "GT World Cup · Course principale", "GT World Cup · Gara principale"),
    "GT World Cup · Qualifikationsrennen": t("GT World Cup · Qualification race", "GT World Cup · Course de qualification", "GT World Cup · Gara di qualificazione"),
    "Formel Regional · Grand Prix": t("Formula Regional · Grand Prix", "Formule Régionale · Grand Prix", "Formula Regional · Gran Premio"),
}
# Nummerierte Varianten: „Rennen 2“, „Lauf 1“, „MXGP Lauf 2“, „Etappe 1“, „Qualifikationsrennen 1“
NUMBERED = [
    (r"^Rennen (\d+)$", t("Race {n}", "Course {n}", "Gara {n}")),
    (r"^Lauf (\d+)$", t("Race {n}", "Manche {n}", "Manche {n}")),
    (r"^MXGP Lauf (\d+)$", t("MXGP race {n}", "MXGP manche {n}", "MXGP manche {n}")),
    (r"^Etappe (\d+)$", t("Stage {n}", "Étape {n}", "Tappa {n}")),
    (r"^Qualifikationsrennen (\d+)$", t("Qualifying race {n}", "Course qualificative {n}", "Gara di qualificazione {n}")),
]
# Englische Eigennamen (z. B. „Senior TT“, „Sidecar TT 2“) bleiben in allen Sprachen gleich
PROPER_NAMES = r"^[A-Z][A-Za-z]+ TT( \d+)?$"

# Länder/Regionen: Nominativ en/fr/it und „Grand Prix“-Formen
PLACES = {
    "Abu Dhabi": ("Abu Dhabi", "Abou Dabi", "Abu Dhabi", "Abu Dhabi Grand Prix", "Grand Prix d'Abou Dabi", "Gran Premio di Abu Dhabi"),
    "Aragón": ("Aragon", "Aragon", "Aragona", "Aragon Grand Prix", "Grand Prix d'Aragon", "Gran Premio d'Aragona"),
    "Argentinien": ("Argentina", "Argentine", "Argentina", "Argentine Grand Prix", "Grand Prix d'Argentine", "Gran Premio d'Argentina"),
    "Aserbaidschan": ("Azerbaijan", "Azerbaïdjan", "Azerbaigian", "Azerbaijan Grand Prix", "Grand Prix d'Azerbaïdjan", "Gran Premio dell'Azerbaigian"),
    "Australien": ("Australia", "Australie", "Australia", "Australian Grand Prix", "Grand Prix d'Australie", "Gran Premio d'Australia"),
    "Bahrain": ("Bahrain", "Bahreïn", "Bahrein", "Bahrain Grand Prix", "Grand Prix de Bahreïn", "Gran Premio del Bahrein"),
    "Belgien": ("Belgium", "Belgique", "Belgio", "Belgian Grand Prix", "Grand Prix de Belgique", "Gran Premio del Belgio"),
    "Brasilien": ("Brazil", "Brésil", "Brasile", "Brazilian Grand Prix", "Grand Prix du Brésil", "Gran Premio del Brasile"),
    "China": ("China", "Chine", "Cina", "Chinese Grand Prix", "Grand Prix de Chine", "Gran Premio di Cina"),
    "Deutschland": ("Germany", "Allemagne", "Germania", "German Grand Prix", "Grand Prix d'Allemagne", "Gran Premio di Germania"),
    "Frankreich": ("France", "France", "Francia", "French Grand Prix", "Grand Prix de France", "Gran Premio di Francia"),
    "Grossbritannien": ("Great Britain", "Grande-Bretagne", "Gran Bretagna", "British Grand Prix", "Grand Prix de Grande-Bretagne", "Gran Premio di Gran Bretagna"),
    "Indonesien": ("Indonesia", "Indonésie", "Indonesia", "Indonesian Grand Prix", "Grand Prix d'Indonésie", "Gran Premio d'Indonesia"),
    "Italien": ("Italy", "Italie", "Italia", "Italian Grand Prix", "Grand Prix d'Italie", "Gran Premio d'Italia"),
    "Japan": ("Japan", "Japon", "Giappone", "Japanese Grand Prix", "Grand Prix du Japon", "Gran Premio del Giappone"),
    "Kanada": ("Canada", "Canada", "Canada", "Canadian Grand Prix", "Grand Prix du Canada", "Gran Premio del Canada"),
    "Katalonien": ("Catalonia", "Catalogne", "Catalogna", "Catalan Grand Prix", "Grand Prix de Catalogne", "Gran Premio di Catalogna"),
    "Katar": ("Qatar", "Qatar", "Qatar", "Qatar Grand Prix", "Grand Prix du Qatar", "Gran Premio del Qatar"),
    "Las Vegas": ("Las Vegas", "Las Vegas", "Las Vegas", "Las Vegas Grand Prix", "Grand Prix de Las Vegas", "Gran Premio di Las Vegas"),
    "Malaysia": ("Malaysia", "Malaisie", "Malesia", "Malaysian Grand Prix", "Grand Prix de Malaisie", "Gran Premio di Malesia"),
    "Mexiko": ("Mexico", "Mexique", "Messico", "Mexico City Grand Prix", "Grand Prix de Mexico", "Gran Premio del Messico"),
    "Miami": ("Miami", "Miami", "Miami", "Miami Grand Prix", "Grand Prix de Miami", "Gran Premio di Miami"),
    "Monaco": ("Monaco", "Monaco", "Monaco", "Monaco Grand Prix", "Grand Prix de Monaco", "Gran Premio di Monaco"),
    "Portugal": ("Portugal", "Portugal", "Portogallo", "Portuguese Grand Prix", "Grand Prix du Portugal", "Gran Premio del Portogallo"),
    "San Marino": ("San Marino", "Saint-Marin", "San Marino", "San Marino Grand Prix", "Grand Prix de Saint-Marin", "Gran Premio di San Marino"),
    "Saudi-Arabien": ("Saudi Arabia", "Arabie saoudite", "Arabia Saudita", "Saudi Arabian Grand Prix", "Grand Prix d'Arabie saoudite", "Gran Premio d'Arabia Saudita"),
    "Singapur": ("Singapore", "Singapour", "Singapore", "Singapore Grand Prix", "Grand Prix de Singapour", "Gran Premio di Singapore"),
    "Spanien": ("Spain", "Espagne", "Spagna", "Spanish Grand Prix", "Grand Prix d'Espagne", "Gran Premio di Spagna"),
    "São Paulo": ("São Paulo", "São Paulo", "San Paolo", "São Paulo Grand Prix", "Grand Prix de São Paulo", "Gran Premio di San Paolo"),
    "Thailand": ("Thailand", "Thaïlande", "Thailandia", "Thai Grand Prix", "Grand Prix de Thaïlande", "Gran Premio di Thailandia"),
    "Tschechien": ("Czech Republic", "Tchéquie", "Repubblica Ceca", "Czech Grand Prix", "Grand Prix de Tchéquie", "Gran Premio della Repubblica Ceca"),
    "Türkei": ("Türkiye", "Turquie", "Turchia", "Turkish Grand Prix", "Grand Prix de Turquie", "Gran Premio di Turchia"),
    "USA": ("USA", "États-Unis", "Stati Uniti", "United States Grand Prix", "Grand Prix des États-Unis", "Gran Premio degli Stati Uniti"),
    "Ungarn": ("Hungary", "Hongrie", "Ungheria", "Hungarian Grand Prix", "Grand Prix de Hongrie", "Gran Premio d'Ungheria"),
    "Valencia": ("Valencia", "Valence", "Valencia", "Valencia Grand Prix", "Grand Prix de Valence", "Gran Premio di Valencia"),
    "Österreich": ("Austria", "Autriche", "Austria", "Austrian Grand Prix", "Grand Prix d'Autriche", "Gran Premio d'Austria"),
    # nur MXGP / Motocross
    "Andalusien": ("Andalusia", "Andalousie", "Andalusia", None, None, None),
    "Flandern": ("Flanders", "Flandre", "Fiandre", None, None, None),
    "Lettland": ("Latvia", "Lettonie", "Lettonia", None, None, None),
    "Niederlande": ("the Netherlands", "Pays-Bas", "Paesi Bassi", None, None, None),
    "Sardinien": ("Sardinia", "Sardaigne", "Sardegna", None, None, None),
    "Schweden": ("Sweden", "Suède", "Svezia", None, None, None),
    "Schweiz": ("Switzerland", "Suisse", "Svizzera", None, None, None),
    "Trentino": ("Trentino", "Trentin", "Trentino", None, None, None),
}
# französische Präposition + Artikel für „MXGP de …“
FR_DE = {"Andalusien": "d'", "Argentinien": "d'", "Australien": "d'", "Deutschland": "d'", "Italien": "d'",
         "Niederlande": "des ", "Portugal": "du ", "Tschechien": "de ", "Türkei": "de ", "Flandern": "de ",
         "Frankreich": "de ", "Grossbritannien": "de ", "Lettland": "de ", "Sardinien": "de ", "Schweden": "de ",
         "Schweiz": "de ", "Spanien": "d'", "Trentino": "du ", "China": "de "}
IT_DI = {"Niederlande": "dei ", "Tschechien": "della ", "Türkei": "di ", "Schweiz": "di ", "Portugal": "del ",
         "Trentino": "del ", "Andalusien": "dell'", "Argentinien": "dell'", "Australien": "dell'", "Italien": "d'"}

# Orte mit deutschem Namen (Event-Ort und F2/F3/Supercup-Titel)
LOCATIONS = {
    "Dschidda": t("Jeddah", "Djeddah", "Gedda"),
    "Mexiko-Stadt": t("Mexico City", "Mexico", "Città del Messico"),
    "Tokio": t("Tokyo", "Tokyo", "Tokyo"),
    "Brünn": t("Brno", "Brno", "Brno"),
    "Rom": t("Rome", "Rome", "Roma"),
    "Montréal": t("Montreal", "Montréal", "Montréal"),
    "Nürnberg": t("Nuremberg", "Nuremberg", "Norimberga"),
    "Spanien": t("Spain", "Espagne", "Spagna"),
    "Portugal": t("Portugal", "Portugal", "Portogallo"),
    "Schweiz": t("Switzerland", "Suisse", "Svizzera"),
    "KAEC (bei Dschidda)": t("KAEC (near Jeddah)", "KAEC (près de Djeddah)", "KAEC (vicino a Gedda)"),
    "Toyota (Aichi)": t("Toyota (Aichi)", "Toyota (Aichi)", "Toyota (Aichi)"),
}

RALLIES = {
    "Rallye Monte-Carlo": t("Rallye Monte-Carlo", "Rallye Monte-Carlo", "Rallye Monte-Carlo"),
    "Rallye Schweden": t("Rally Sweden", "Rallye de Suède", "Rally di Svezia"),
    "Safari Rallye Kenia": t("Safari Rally Kenya", "Safari Rally Kenya", "Safari Rally Kenya"),
    "Rallye Kroatien": t("Croatia Rally", "Rallye de Croatie", "Rally di Croazia"),
    "Rallye Islas Canarias": t("Rally Islas Canarias", "Rallye des Canaries", "Rally delle Canarie"),
    "Rallye Japan": t("Rally Japan", "Rallye du Japon", "Rally del Giappone"),
    "Akropolis-Rallye": t("Acropolis Rally", "Rallye de l'Acropole", "Rally dell'Acropoli"),
    "Rallye Italien (Rom)": t("Rally Italy (Rome)", "Rallye d'Italie (Rome)", "Rally d'Italia (Roma)"),
    "Rallye Estland": t("Rally Estonia", "Rallye d'Estonie", "Rally d'Estonia"),
    "Rallye Finnland": t("Rally Finland", "Rallye de Finlande", "Rally di Finlandia"),
    "Rallye USA": t("Rally USA", "Rallye des États-Unis", "Rally degli Stati Uniti"),
    "Rallye Schottland": t("Rally Scotland", "Rallye d'Écosse", "Rally di Scozia"),
    "Rallye Paraguay": t("Rally Paraguay", "Rallye du Paraguay", "Rally del Paraguay"),
    "Rallye Chile": t("Rally Chile", "Rallye du Chili", "Rally del Cile"),
    "Rallye Saudi-Arabien": t("Rally Saudi Arabia", "Rallye d'Arabie saoudite", "Rally dell'Arabia Saudita"),
}

SUFFIXES = [
    (" (Showrennen)", t(" (exhibition)", " (course d'exhibition)", " (esibizione)")),
    (" (Finale)", t(" (finale)", " (finale)", " (finale)")),
    (" · 6h-Rennen", t(" · 6h race", " · course de 6 h", " · gara di 6 ore")),
    (" · Saisonfinale", t(" · season finale", " · finale de la saison", " · finale di stagione")),
]
FIXED_NAMES = {
    "Motocross der Nationen": t("Motocross of Nations", "Motocross des Nations", "Motocross delle Nazioni"),
    "Rallye Dakar 2027": t("Dakar Rally 2027", "Rallye Dakar 2027", "Rally Dakar 2027"),
    "Isle of Man TT": t("Isle of Man TT", "TT de l'île de Man", "TT dell'Isola di Man"),
}


def _session_name(name):
    if name in SESSION_NAMES:
        return SESSION_NAMES[name]
    if re.match(PROPER_NAMES, name):
        return t(name, name, name)
    for pattern, forms in NUMBERED:
        m = re.match(pattern, name)
        if m:
            return {lang: forms[lang].format(n=m.group(1)) for lang in LANGS}
    return None


def _place(name, idx):
    entry = PLACES.get(name)
    return entry[idx] if entry else None


def _event_name(name):
    if name in FIXED_NAMES:
        return FIXED_NAMES[name]
    if name in RALLIES:
        return RALLIES[name]
    for suffix, forms in SUFFIXES:
        if name.endswith(suffix):
            base = name[: -len(suffix)]
            inner = _event_name(base) or t(base, base, base)
            return {lang: inner[lang] + forms[lang] for lang in LANGS}
    m = re.match(r"^(?:Grosser Preis|Grand Prix) (?:von|der) (.+)$", name)
    if m and m.group(1) in PLACES and PLACES[m.group(1)][3]:
        p = PLACES[m.group(1)]
        return t(p[3], p[4], p[5])
    m = re.match(r"^(\d+) Stunden von (.+)$", name)
    if m:
        n, place = m.groups()
        fr_prep = "d'" if place[0] in "AEIOUÉ" else "de "
        if place.startswith("Le "):
            place_fr = "du " + place[3:]
            return t(f"{n} Hours of {place}", f"{n} Heures {place_fr}", f"{n} Ore di {place}")
        it_prep = "d'" if place[0] in "AEIOU" else "di "
        return t(f"{n} Hours of {place}", f"{n} Heures {fr_prep}{place}", f"{n} Ore {it_prep}{place}")
    m = re.match(r"^MXGP (?:von|der) (.+)$", name)
    if m and m.group(1) in PLACES:
        key = m.group(1)
        return t(f"MXGP of {_place(key, 0)}", f"MXGP {FR_DE.get(key, 'de ')}{_place(key, 1)}",
                 f"MXGP {IT_DI.get(key, 'di ')}{_place(key, 2)}")
    m = re.match(r"^(F2|F3|Supercup) (.+)$", name)
    if m and m.group(2) in LOCATIONS:
        prefix, loc = m.groups()
        return {lang: f"{prefix} {LOCATIONS[loc][lang]}" for lang in LANGS}
    return None


def _note(note):
    parts = re.split(r"(, |; )", note)
    out = {lang: "" for lang in LANGS}
    first = True
    for part in parts:
        if part in (", ", "; "):
            for lang in LANGS:
                out[lang] += part
            continue
        forms = NOTE_PARTS.get(part)
        if not forms:
            return None
        for lang in LANGS:
            text = forms[lang]
            out[lang] += text[0].upper() + text[1:] if first else text
        first = False
    return out


def translate_data(data):
    """Ergänzt *I18n-Felder in Sendern, Serien, Events und Sessions. Gibt fehlende Texte zurück."""
    missing = []
    for c in data["channels"]:
        if c.get("note"):
            c["noteI18n"] = CHANNEL_NOTES.get(c["id"])
            if c["noteI18n"] is None:
                missing.append(f"Sender-Hinweis {c['id']}")
    for s in data["series"]:
        s["taglineI18n"] = TAGLINES.get(s["id"])
        if s["taglineI18n"] is None:
            missing.append(f"Tagline {s['id']}")
    for e in data["events"]:
        e["nameI18n"] = _event_name(e["name"])
        e["locationI18n"] = LOCATIONS.get(e["location"])
        if e.get("note"):
            e["noteI18n"] = _note(e["note"])
            if e["noteI18n"] is None:
                missing.append(f"Notiz „{e['note']}“")
        for s in e["sessions"]:
            s["nameI18n"] = _session_name(s["name"])
            if s["nameI18n"] is None:
                missing.append(f"Session „{s['name']}“")
    return sorted(set(missing))
