"""Übersetzungen der Datentexte (Deutsch → Englisch, Französisch, Italienisch, Spanisch, Portugiesisch).

Die App zeigt die Übersetzung passend zur Gerätesprache und fällt sonst auf Deutsch zurück.
Fehlt eine Übersetzung, ist das kein Fehler – `validate_races.py` meldet es nur als Hinweis.
"""
import re

LANGS = ("en", "fr", "it", "es", "pt")


def t(en, fr, it, es, pt):
    return {"en": en, "fr": fr, "it": it, "es": es, "pt": pt}


TAGLINES = {
    "f1": t("The pinnacle of motorsport", "La catégorie reine", "La classe regina", "La cima del automovilismo", "O auge do automobilismo"),
    "f2": t("Stepping stone to F1", "Antichambre de la F1", "Trampolino verso la F1", "La antesala de la F1", "A porta de entrada para a F1"),
    "f3": t("Junior single-seater series", "Formule de promotion", "Serie formula giovanile", "Categoría de promoción de monoplazas", "Categoria de base de monopostos"),
    "f1academy": t("All-female single-seater series", "Série de monoplaces féminine", "Serie di monoposto femminile", "Serie de monoplazas femenina", "Categoria feminina de monopostos"),
    "indycar": t("Incl. Indy 500", "Avec l'Indy 500", "Con la Indy 500", "Con las 500 Millas de Indianápolis", "Com as 500 Milhas de Indianápolis"),
    "superformula": t("Japanese single-seater series", "Monoplaces japonaises", "Monoposto giapponesi", "Monoplazas japoneses", "Monopostos japoneses"),
    "fe": t("Electric street racing", "Courses électriques en ville", "Gare elettriche in città", "Carreras eléctricas urbanas", "Corridas elétricas nas cidades"),
    "wec": t("Incl. 24h of Le Mans", "Avec les 24 Heures du Mans", "Con la 24 Ore di Le Mans", "Con las 24 Horas de Le Mans", "Com as 24 Horas de Le Mans"),
    "imsa": t("Incl. Daytona 24", "Avec les 24 Heures de Daytona", "Con la 24 Ore di Daytona", "Con las 24 Horas de Daytona", "Com as 24 Horas de Daytona"),
    "elms": t("4-hour races across Europe", "Courses de 4 heures en Europe", "Gare di 4 ore in Europa", "Carreras de 4 horas por Europa", "Corridas de 4 horas pela Europa"),
    "alms": t("Winter season of the Le Mans series", "Saison d'hiver des séries Le Mans", "Stagione invernale delle serie Le Mans", "Temporada de invierno de las series Le Mans", "Temporada de inverno das séries Le Mans"),
    "gtwc": t("Incl. 24h of Spa", "Avec les 24 Heures de Spa", "Con la 24 Ore di Spa", "Con las 24 Horas de Spa", "Com as 24 Horas de Spa"),
    "nls": t("Nordschleife", "Nordschleife", "Nordschleife", "Nordschleife", "Nordschleife"),
    "n24": t("Green Hell, 24 hours", "Enfer vert, 24 heures", "Inferno verde, 24 ore", "El Infierno Verde, 24 horas", "O Inferno Verde, 24 horas"),
    "dtm": t("GT3 sprint races", "Courses sprint GT3", "Gare sprint GT3", "Carreras sprint GT3", "Corridas sprint GT3"),
    "gtmasters": t("GT3 sprints at DTM events", "Sprints GT3 en lever de rideau du DTM", "Sprint GT3 nel weekend DTM", "Sprints GT3 en los fines de semana del DTM", "Sprints GT3 nos fins de semana do DTM"),
    "carreracup": t("One-make cup at DTM events", "Coupe monomarque en lever de rideau du DTM", "Monomarca nel weekend DTM", "Copa monomarca en los fines de semana del DTM", "Copa monomarca nos fins de semana do DTM"),
    "supercup": t("One-make cup at F1 events", "Coupe monomarque en lever de rideau de la F1", "Monomarca nel weekend di F1", "Copa monomarca en los fines de semana de F1", "Copa monomarca nos fins de semana da F1"),
    "carreracupna": t("One-make cup at F1, IMSA and IndyCar events in the US", "Coupe monomarque aux courses F1, IMSA et IndyCar aux États-Unis", "Monomarca nei weekend di F1, IMSA e IndyCar negli USA", "Copa monomarca en F1, IMSA e IndyCar en EE. UU.", "Copa monomarca na F1, IMSA e IndyCar nos EUA"),
    "macau": t("GT World Cup on the Guia Circuit", "GT World Cup sur le circuit de Guia", "GT World Cup sul circuito di Guia", "GT World Cup en el circuito de Guia", "GT World Cup no circuito da Guia"),
    "btcc": t("British touring cars", "Voitures de tourisme britanniques", "Turismo britannico", "Turismos británicos", "Turismos britânicos"),
    "supercars": t("V8 touring cars from Australia", "Voitures de tourisme V8 australiennes", "Turismo V8 australiane", "Turismos V8 de Australia", "Turismos V8 da Austrália"),
    "supergt": t("Japanese GT championship", "Championnat GT japonais", "Campionato GT giapponese", "Campeonato GT japonés", "Campeonato GT japonês"),
    "nascar": t("Stock cars, incl. Daytona 500", "Stock-cars, avec le Daytona 500", "Stock car, con la Daytona 500", "Stock cars, con las 500 Millas de Daytona", "Stock cars, com as 500 Milhas de Daytona"),
    "motogp": t("Motorcycle world championship", "Championnat du monde moto", "Mondiale di motociclismo", "Mundial de motociclismo", "Mundial de motovelocidade"),
    "moto2": t("Intermediate class of the world championship", "Catégorie intermédiaire du mondial", "Classe intermedia del mondiale", "Categoría intermedia del mundial", "Categoria intermediária do mundial"),
    "moto3": t("Entry class of the world championship", "Catégorie d'entrée du mondial", "Classe d'ingresso del mondiale", "Categoría de acceso del mundial", "Categoria de entrada do mundial"),
    "wsbk": t("Production-based superbikes", "Superbikes dérivées de la série", "Superbike derivate di serie", "Superbikes derivadas de serie", "Superbikes derivadas de série"),
    "iomtt": t("Road racing on the Isle of Man", "Courses sur route à l'île de Man", "Corse su strada all'Isola di Man", "Carreras en carretera en la Isla de Man", "Corridas de rua na Ilha de Man"),
    "mxgp": t("Motocross worldwide", "Motocross dans le monde entier", "Motocross in tutto il mondo", "Motocross por todo el mundo", "Motocross pelo mundo"),
    "supercross": t("US stadium racing", "Courses en stade aux États-Unis", "Gare negli stadi USA", "Carreras en estadios de EE. UU.", "Corridas em estádios dos EUA"),
    "wrc": t("World Rally Championship", "Championnat du monde des rallyes", "Campionato del mondo rally", "Campeonato del Mundo de Rallyes", "Campeonato Mundial de Rali"),
    "dakar": t("Desert rally in Saudi Arabia", "Rallye-raid en Arabie saoudite", "Rally raid in Arabia Saudita", "Rally raid en Arabia Saudí", "Rali cross-country na Arábia Saudita"),
    "pikespeak": t("Hill climb in Colorado", "Course de côte au Colorado", "Cronoscalata in Colorado", "Subida de montaña en Colorado", "Subida de montanha no Colorado"),
}

CHANNEL_NOTES = {
    "srf2": t("Sometimes on SRF info or SRF 1", "Parfois sur SRF info ou SRF 1", "A volte su SRF info o SRF 1", "A veces en SRF info o SRF 1", "Às vezes no SRF info ou SRF 1"),
    "playsrf": t("Free live stream in Switzerland", "Livestream gratuit en Suisse", "Livestream gratuito in Svizzera", "Streaming gratis en Suiza", "Transmissão grátis na Suíça"),
    "sky": t("All sessions, subscription required", "Toutes les sessions, abonnement requis", "Tutte le sessioni, abbonamento necessario", "Todas las sesiones, requiere suscripción", "Todas as sessões, exige assinatura"),
    "prosieben": t("Availability in Switzerland depends on your TV provider", "Réception en Suisse selon l'opérateur TV", "Ricezione in Svizzera secondo l'operatore TV", "En Suiza depende de tu operador de TV", "Na Suíça depende da operadora de TV"),
    "joyn": t("Free live stream; may be geo-blocked in Switzerland", "Livestream gratuit ; peut être bloqué en Suisse", "Livestream gratuito; può essere bloccato in Svizzera", "Streaming gratis; puede estar bloqueado en Suiza", "Transmissão grátis; pode estar bloqueada na Suíça"),
    "yt-vln": t("Official free NLS live stream", "Livestream officiel gratuit de la NLS", "Livestream ufficiale gratuito della NLS", "Streaming oficial gratuito de la NLS", "Transmissão oficial gratuita da NLS"),
    "nls-web": t("Live stream & live timing", "Livestream et chronométrage", "Livestream e cronometraggio", "Streaming y tiempos en directo", "Transmissão e cronometragem ao vivo"),
    "yt-24h": t("Free live stream", "Livestream gratuit", "Livestream gratuito", "Streaming gratis", "Transmissão grátis"),
    "n24-web": t("Live stream & live timing", "Livestream et chronométrage", "Livestream e cronometraggio", "Streaming y tiempos en directo", "Transmissão e cronometragem ao vivo"),
    "eurosport": t("Usually Eurosport 2, finale often on Eurosport 1", "Surtout Eurosport 2, la fin souvent sur Eurosport 1", "Di solito Eurosport 2, il finale spesso su Eurosport 1", "Sobre todo Eurosport 2, el final a menudo en Eurosport 1", "Geralmente Eurosport 2, o final muitas vezes no Eurosport 1"),
    "fiawecplus": t("Official WEC stream", "Stream officiel du WEC", "Stream ufficiale del WEC", "Streaming oficial del WEC", "Transmissão oficial do WEC"),
    "bluetv": t("Swisscom; Formula E partner until season 12", "Swisscom ; partenaire Formule E jusqu'à la saison 12", "Swisscom; partner Formula E fino alla stagione 12", "Swisscom; socio de la Fórmula E hasta la temporada 12", "Swisscom; parceira da Fórmula E até a temporada 12"),
    "disneyplus": t("From season 13 per Formula E; Swiss partner still open", "Dès la saison 13 selon la Formule E ; partenaire suisse encore ouvert", "Dalla stagione 13 secondo la Formula E; partner svizzero ancora aperto", "Desde la temporada 13 según la Fórmula E; socio suizo aún por confirmar", "A partir da temporada 13 segundo a Fórmula E; parceiro suíço ainda em aberto"),
    "f1tv": t("Official stream incl. F2, F3 and F1 Academy", "Stream officiel avec F2, F3 et F1 Academy", "Stream ufficiale con F2, F3 e F1 Academy", "Streaming oficial con F2, F3 y F1 Academy", "Transmissão oficial com F2, F3 e F1 Academy"),
    "motorvision": t("IndyCar with German commentary", "IndyCar commenté en allemand", "IndyCar con commento in tedesco", "IndyCar con comentarios en alemán", "IndyCar com narração em alemão"),
    "sportdigital": t("NASCAR Cup live (DACH), availability depends on TV provider", "NASCAR Cup en direct (DACH), selon l'opérateur TV", "NASCAR Cup in diretta (DACH), secondo l'operatore TV", "NASCAR Cup en directo (DACH), según operador de TV", "NASCAR Cup ao vivo (DACH), conforme a operadora de TV"),
    "yt-imsa": t("Free live stream outside North America", "Livestream gratuit hors Amérique du Nord", "Livestream gratuito fuori dal Nord America", "Streaming gratis fuera de Norteamérica", "Transmissão grátis fora da América do Norte"),
    "yt-elms": t("Official free live stream", "Livestream officiel gratuit", "Livestream ufficiale gratuito", "Streaming oficial gratuito", "Transmissão oficial gratuita"),
    "yt-gtworld": t("Official free live stream", "Livestream officiel gratuit", "Livestream ufficiale gratuito", "Streaming oficial gratuito", "Transmissão oficial gratuita"),
    "yt-btcc": t("Free live stream outside the UK and North America", "Livestream gratuit hors Royaume-Uni et Amérique du Nord", "Livestream gratuito fuori da Regno Unito e Nord America", "Streaming gratis fuera de Reino Unido y Norteamérica", "Transmissão grátis fora do Reino Unido e da América do Norte"),
    "superview": t("International Supercars stream (subscription)", "Stream international des Supercars (abonnement)", "Stream internazionale delle Supercars (abbonamento)", "Streaming internacional de Supercars (suscripción)", "Transmissão internacional da Supercars (assinatura)"),
    "servustv": t("Free stream in DE/AT/CH", "Stream gratuit en DE/AT/CH", "Stream gratuito in DE/AT/CH", "Streaming gratis en DE/AT/CH", "Transmissão grátis em DE/AT/CH"),
    "sbk-pass": t("Official stream, all sessions", "Stream officiel, toutes les sessions", "Stream ufficiale, tutte le sessioni", "Streaming oficial, todas las sesiones", "Transmissão oficial, todas as sessões"),
    "ttplus": t("Official Isle of Man TT live stream", "Livestream officiel du TT de l'île de Man", "Livestream ufficiale del TT dell'Isola di Man", "Streaming oficial del TT de la Isla de Man", "Transmissão oficial do TT da Ilha de Man"),
    "mxgp-tv": t("Official motocross world championship stream", "Stream officiel du mondial de motocross", "Stream ufficiale del mondiale motocross", "Streaming oficial del mundial de motocross", "Transmissão oficial do mundial de motocross"),
    "smx-pass": t("International Supercross stream", "Stream international du Supercross", "Stream internazionale del Supercross", "Streaming internacional de Supercross", "Transmissão internacional do Supercross"),
    "rallytv": t("Every WRC stage live", "Toutes les spéciales WRC en direct", "Tutte le prove WRC in diretta", "Todos los tramos del WRC en directo", "Todas as especiais do WRC ao vivo"),
    "dakar-web": t("Live tracking & daily highlights", "Suivi en direct et résumés quotidiens", "Tracking live e highlights quotidiani", "Seguimiento en directo y resúmenes diarios", "Rastreamento ao vivo e resumos diários"),
    "yt-ppihc": t("Free live stream", "Livestream gratuit", "Livestream gratuito", "Streaming gratis", "Transmissão grátis"),
    "yt-adac": t("Live stream depending on rights", "Livestream selon les droits", "Livestream secondo i diritti", "Streaming según derechos", "Transmissão conforme os direitos"),
    "yt-porsche": t("Live stream depending on rights", "Livestream selon les droits", "Livestream secondo i diritti", "Streaming según derechos", "Transmissão conforme os direitos"),
    "yt-macau": t("Live stream depending on region", "Livestream selon la région", "Livestream secondo la regione", "Streaming según la región", "Transmissão conforme a região"),
    "yt-supergt": t("Live stream depending on region", "Livestream selon la région", "Livestream secondo la regione", "Streaming según la región", "Transmissão conforme a região"),
    "sfgo": t("Official Super Formula app (subscription)", "App officielle de la Super Formula (abonnement)", "App ufficiale della Super Formula (abbonamento)", "App oficial de la Super Formula (suscripción)", "App oficial da Super Formula (assinatura)"),
    "yt-alms": t("Official free live stream", "Livestream officiel gratuit", "Livestream ufficiale gratuito", "Streaming oficial gratuito", "Transmissão oficial gratuita"),
}

# Bausteine der Event-Notizen (durch ", " bzw. "; " getrennt)
NOTE_PARTS = {
    "Startzeiten provisorisch": t("start times provisional", "horaires provisoires", "orari provvisori", "horas provisionales", "horários provisórios"),
    "Startzeiten noch provisorisch": t("start times still provisional", "horaires encore provisoires", "orari ancora provvisori", "horas aún provisionales", "horários ainda provisórios"),
    "Startzeit provisorisch": t("start time provisional", "horaire provisoire", "orario provvisorio", "hora provisional", "horário provisório"),
    "Startzeit provisorisch (abgeleitet vom MotoGP-Zeitplan)": t("start time provisional (based on the MotoGP schedule)", "horaire provisoire (d'après le programme MotoGP)", "orario provvisorio (in base al programma MotoGP)", "hora provisional (según el horario de MotoGP)", "horário provisório (com base na programação da MotoGP)"),
    "Startzeiten provisorisch und wetterabhängig": t("start times provisional and weather-dependent", "horaires provisoires et selon la météo", "orari provvisori e legati al meteo", "horas provisionales y según el tiempo", "horários provisórios e dependentes do clima"),
    "Etappenzeiten provisorisch": t("stage times provisional", "horaires des étapes provisoires", "orari delle tappe provvisori", "horas de etapa provisionales", "horários das etapas provisórios"),
    "Daten offiziell": t("dates official", "dates officielles", "date ufficiali", "fechas oficiales", "datas oficiais"),
    "Daten offiziell (Änderungen vorbehalten)": t("dates official (subject to change)", "dates officielles (sous réserve)", "date ufficiali (salvo modifiche)", "fechas oficiales (sujetas a cambios)", "datas oficiais (sujeitas a mudanças)"),
    "Datum offiziell": t("date official", "date officielle", "data ufficiale", "fecha oficial", "data oficial"),
    "Datum offiziell (27.–30. Mai)": t("date official (27–30 May)", "date officielle (27–30 mai)", "data ufficiale (27–30 maggio)", "fecha oficial (27–30 de mayo)", "data oficial (27–30 de maio)"),
    "Datum offiziell (30. April – 2. Mai)": t("date official (30 April – 2 May)", "date officielle (30 avril – 2 mai)", "data ufficiale (30 aprile – 2 maggio)", "fecha oficial (30 de abril – 2 de mayo)", "data oficial (30 de abril – 2 de maio)"),
    "Datum provisorisch": t("date provisional", "date provisoire", "data provvisoria", "fecha provisional", "data provisória"),
    "Datum laut IndyCar bzw. Medienberichten": t("date per IndyCar or media reports", "date selon IndyCar ou la presse", "data secondo IndyCar o la stampa", "fecha según IndyCar o la prensa", "data segundo a IndyCar ou a imprensa"),
    "Zeitraum offiziell (1.–15. Januar)": t("dates official (1–15 January)", "période officielle (1er–15 janvier)", "periodo ufficiale (1–15 gennaio)", "periodo oficial (1–15 de enero)", "período oficial (1–15 de janeiro)"),
    "Renntage offiziell": t("race days official", "jours de course officiels", "giorni di gara ufficiali", "días de carrera oficiales", "dias de corrida oficiais"),
    "Kalender provisorisch": t("calendar provisional", "calendrier provisoire", "calendario provvisorio", "calendario provisional", "calendário provisório"),
    "Kalender vorläufig": t("calendar preliminary", "calendrier préliminaire", "calendario preliminare", "calendario preliminar", "calendário preliminar"),
    "Daten gemäss F1-Kalender": t("dates per F1 calendar", "dates selon le calendrier F1", "date secondo il calendario F1", "fechas según el calendario de F1", "datas segundo o calendário da F1"),
    "Datum offiziell (F1-Rahmenprogramm)": t("date official (F1 support race)", "date officielle (lever de rideau F1)", "data ufficiale (gara di supporto F1)", "fecha oficial (carrera de apoyo de F1)", "data oficial (corrida de apoio da F1)"),
    "Daten aus dem DTM- bzw. WEC-Kalender": t("dates from the DTM/WEC calendar", "dates selon le calendrier DTM/WEC", "date dal calendario DTM/WEC", "fechas del calendario DTM/WEC", "datas do calendário DTM/WEC"),
    "Montreal noch unter Vertragsvorbehalt": t("Montreal still subject to contract", "Montréal encore sous réserve de contrat", "Montréal ancora soggetta a contratto", "Montreal aún pendiente de contrato", "Montreal ainda depende de contrato"),
    "AO Racing by Absolute": t("AO Racing by Absolute", "AO Racing by Absolute", "AO Racing by Absolute", "AO Racing by Absolute", "AO Racing by Absolute"),
}

SESSION_NAMES = {
    "Rennen": t("Race", "Course", "Gara", "Carrera", "Corrida"),
    "Qualifying": t("Qualifying", "Qualifications", "Qualifiche", "Clasificación", "Classificação"),
    "Sprint": t("Sprint", "Sprint", "Sprint", "Sprint", "Sprint"),
    "Sprintrennen": t("Sprint race", "Course sprint", "Gara sprint", "Carrera sprint", "Corrida sprint"),
    "Hauptrennen": t("Feature race", "Course principale", "Gara principale", "Carrera principal", "Corrida principal"),
    "Zeittraining": t("Qualifying", "Essais qualificatifs", "Prove cronometrate", "Clasificación", "Classificação"),
    "Top-Qualifying": t("Top qualifying", "Top qualifications", "Top qualifiche", "Top Qualifying", "Top Qualifying"),
    "24h-Rennen": t("24h race", "Course de 24 h", "Gara di 24 ore", "Carrera de 24 h", "Corrida de 24 h"),
    "Superpole-Rennen": t("Superpole race", "Course Superpole", "Gara Superpole", "Carrera Superpole", "Corrida Superpole"),
    "Prolog": t("Prologue", "Prologue", "Prologo", "Prólogo", "Prólogo"),
    "Schlussetappe": t("Final stage", "Dernière étape", "Tappa finale", "Etapa final", "Etapa final"),
    "Renntag": t("Race day", "Jour de course", "Giorno di gara", "Día de carrera", "Dia de corrida"),
    "Erster voller Rallye-Tag": t("First full rally day", "Première journée complète", "Prima giornata completa", "Primer día completo", "Primeiro dia completo"),
    "Power Stage": t("Power Stage", "Power Stage", "Power Stage", "Power Stage", "Power Stage"),
    "Night Show": t("Night Show", "Night Show", "Night Show", "Night Show", "Night Show"),
    "GT World Cup · Hauptrennen": t("GT World Cup · Main race", "GT World Cup · Course principale", "GT World Cup · Gara principale", "GT World Cup · Carrera principal", "GT World Cup · Corrida principal"),
    "GT World Cup · Qualifikationsrennen": t("GT World Cup · Qualification race", "GT World Cup · Course de qualification", "GT World Cup · Gara di qualificazione", "GT World Cup · Carrera de clasificación", "GT World Cup · Corrida classificatória"),
    "Formel Regional · Grand Prix": t("Formula Regional · Grand Prix", "Formule Régionale · Grand Prix", "Formula Regional · Gran Premio", "Fórmula Regional · Gran Premio", "Fórmula Regional · Grande Prêmio"),
    "TCR World Tour · Finale": t("TCR World Tour · Finale", "TCR World Tour · Finale", "TCR World Tour · Finale", "TCR World Tour · Final", "TCR World Tour · Final"),
}
# Nummerierte Varianten: „Rennen 2“, „Lauf 1“, „MXGP Lauf 2“, „Etappe 1“, „Qualifikationsrennen 1“
NUMBERED = [
    (r"^Rennen (\d+)$", t("Race {n}", "Course {n}", "Gara {n}", "Carrera {n}", "Corrida {n}")),
    (r"^Lauf (\d+)$", t("Race {n}", "Manche {n}", "Manche {n}", "Manga {n}", "Bateria {n}")),
    (r"^MXGP Lauf (\d+)$", t("MXGP race {n}", "MXGP manche {n}", "MXGP manche {n}", "MXGP manga {n}", "MXGP bateria {n}")),
    (r"^Etappe (\d+)$", t("Stage {n}", "Étape {n}", "Tappa {n}", "Etapa {n}", "Etapa {n}")),
    (r"^Qualifikationsrennen (\d+)$", t("Qualifying race {n}", "Course qualificative {n}", "Gara di qualificazione {n}", "Carrera de clasificación {n}", "Corrida classificatória {n}")),
]
# Englische Eigennamen (z. B. „Senior TT“, „Sidecar TT 2“) bleiben in allen Sprachen gleich
PROPER_NAMES = r"^[A-Z][A-Za-z]+ TT( \d+)?$"

# Länder/Regionen: Nominativ en/fr/it, „Grand Prix“-Formen en/fr/it, dann Nominativ es/pt und „Grand Prix“ es/pt
PLACES = {
    "Abu Dhabi": ("Abu Dhabi", "Abou Dabi", "Abu Dhabi", "Abu Dhabi Grand Prix", "Grand Prix d'Abou Dabi", "Gran Premio di Abu Dhabi", "Abu Dabi", "Abu Dhabi", "Gran Premio de Abu Dabi", "Grande Prêmio de Abu Dhabi"),
    "Aragón": ("Aragon", "Aragon", "Aragona", "Aragon Grand Prix", "Grand Prix d'Aragon", "Gran Premio d'Aragona", "Aragón", "Aragão", "Gran Premio de Aragón", "Grande Prêmio de Aragão"),
    "Argentinien": ("Argentina", "Argentine", "Argentina", "Argentine Grand Prix", "Grand Prix d'Argentine", "Gran Premio d'Argentina", "Argentina", "Argentina", "Gran Premio de Argentina", "Grande Prêmio da Argentina"),
    "Aserbaidschan": ("Azerbaijan", "Azerbaïdjan", "Azerbaigian", "Azerbaijan Grand Prix", "Grand Prix d'Azerbaïdjan", "Gran Premio dell'Azerbaigian", "Azerbaiyán", "Azerbaijão", "Gran Premio de Azerbaiyán", "Grande Prêmio do Azerbaijão"),
    "Australien": ("Australia", "Australie", "Australia", "Australian Grand Prix", "Grand Prix d'Australie", "Gran Premio d'Australia", "Australia", "Austrália", "Gran Premio de Australia", "Grande Prêmio da Austrália"),
    "Bahrain": ("Bahrain", "Bahreïn", "Bahrein", "Bahrain Grand Prix", "Grand Prix de Bahreïn", "Gran Premio del Bahrein", "Baréin", "Bahrein", "Gran Premio de Baréin", "Grande Prêmio do Bahrein"),
    "Belgien": ("Belgium", "Belgique", "Belgio", "Belgian Grand Prix", "Grand Prix de Belgique", "Gran Premio del Belgio", "Bélgica", "Bélgica", "Gran Premio de Bélgica", "Grande Prêmio da Bélgica"),
    "Brasilien": ("Brazil", "Brésil", "Brasile", "Brazilian Grand Prix", "Grand Prix du Brésil", "Gran Premio del Brasile", "Brasil", "Brasil", "Gran Premio de Brasil", "Grande Prêmio do Brasil"),
    "China": ("China", "Chine", "Cina", "Chinese Grand Prix", "Grand Prix de Chine", "Gran Premio di Cina", "China", "China", "Gran Premio de China", "Grande Prêmio da China"),
    "Deutschland": ("Germany", "Allemagne", "Germania", "German Grand Prix", "Grand Prix d'Allemagne", "Gran Premio di Germania", "Alemania", "Alemanha", "Gran Premio de Alemania", "Grande Prêmio da Alemanha"),
    "Frankreich": ("France", "France", "Francia", "French Grand Prix", "Grand Prix de France", "Gran Premio di Francia", "Francia", "França", "Gran Premio de Francia", "Grande Prêmio da França"),
    "Grossbritannien": ("Great Britain", "Grande-Bretagne", "Gran Bretagna", "British Grand Prix", "Grand Prix de Grande-Bretagne", "Gran Premio di Gran Bretagna", "Gran Bretaña", "Grã-Bretanha", "Gran Premio de Gran Bretaña", "Grande Prêmio da Grã-Bretanha"),
    "Indonesien": ("Indonesia", "Indonésie", "Indonesia", "Indonesian Grand Prix", "Grand Prix d'Indonésie", "Gran Premio d'Indonesia", "Indonesia", "Indonésia", "Gran Premio de Indonesia", "Grande Prêmio da Indonésia"),
    "Italien": ("Italy", "Italie", "Italia", "Italian Grand Prix", "Grand Prix d'Italie", "Gran Premio d'Italia", "Italia", "Itália", "Gran Premio de Italia", "Grande Prêmio da Itália"),
    "Japan": ("Japan", "Japon", "Giappone", "Japanese Grand Prix", "Grand Prix du Japon", "Gran Premio del Giappone", "Japón", "Japão", "Gran Premio de Japón", "Grande Prêmio do Japão"),
    "Kanada": ("Canada", "Canada", "Canada", "Canadian Grand Prix", "Grand Prix du Canada", "Gran Premio del Canada", "Canadá", "Canadá", "Gran Premio de Canadá", "Grande Prêmio do Canadá"),
    "Katalonien": ("Catalonia", "Catalogne", "Catalogna", "Catalan Grand Prix", "Grand Prix de Catalogne", "Gran Premio di Catalogna", "Cataluña", "Catalunha", "Gran Premio de Cataluña", "Grande Prêmio da Catalunha"),
    "Katar": ("Qatar", "Qatar", "Qatar", "Qatar Grand Prix", "Grand Prix du Qatar", "Gran Premio del Qatar", "Catar", "Catar", "Gran Premio de Catar", "Grande Prêmio do Catar"),
    "Las Vegas": ("Las Vegas", "Las Vegas", "Las Vegas", "Las Vegas Grand Prix", "Grand Prix de Las Vegas", "Gran Premio di Las Vegas", "Las Vegas", "Las Vegas", "Gran Premio de Las Vegas", "Grande Prêmio de Las Vegas"),
    "Malaysia": ("Malaysia", "Malaisie", "Malesia", "Malaysian Grand Prix", "Grand Prix de Malaisie", "Gran Premio di Malesia", "Malasia", "Malásia", "Gran Premio de Malasia", "Grande Prêmio da Malásia"),
    "Mexiko": ("Mexico", "Mexique", "Messico", "Mexico City Grand Prix", "Grand Prix de Mexico", "Gran Premio del Messico", "México", "México", "Gran Premio de la Ciudad de México", "Grande Prêmio da Cidade do México"),
    "Miami": ("Miami", "Miami", "Miami", "Miami Grand Prix", "Grand Prix de Miami", "Gran Premio di Miami", "Miami", "Miami", "Gran Premio de Miami", "Grande Prêmio de Miami"),
    "Monaco": ("Monaco", "Monaco", "Monaco", "Monaco Grand Prix", "Grand Prix de Monaco", "Gran Premio di Monaco", "Mónaco", "Mônaco", "Gran Premio de Mónaco", "Grande Prêmio de Mônaco"),
    "Portugal": ("Portugal", "Portugal", "Portogallo", "Portuguese Grand Prix", "Grand Prix du Portugal", "Gran Premio del Portogallo", "Portugal", "Portugal", "Gran Premio de Portugal", "Grande Prêmio de Portugal"),
    "San Marino": ("San Marino", "Saint-Marin", "San Marino", "San Marino Grand Prix", "Grand Prix de Saint-Marin", "Gran Premio di San Marino", "San Marino", "San Marino", "Gran Premio de San Marino", "Grande Prêmio de San Marino"),
    "Saudi-Arabien": ("Saudi Arabia", "Arabie saoudite", "Arabia Saudita", "Saudi Arabian Grand Prix", "Grand Prix d'Arabie saoudite", "Gran Premio d'Arabia Saudita", "Arabia Saudí", "Arábia Saudita", "Gran Premio de Arabia Saudí", "Grande Prêmio da Arábia Saudita"),
    "Singapur": ("Singapore", "Singapour", "Singapore", "Singapore Grand Prix", "Grand Prix de Singapour", "Gran Premio di Singapore", "Singapur", "Singapura", "Gran Premio de Singapur", "Grande Prêmio de Singapura"),
    "Spanien": ("Spain", "Espagne", "Spagna", "Spanish Grand Prix", "Grand Prix d'Espagne", "Gran Premio di Spagna", "España", "Espanha", "Gran Premio de España", "Grande Prêmio da Espanha"),
    "São Paulo": ("São Paulo", "São Paulo", "San Paolo", "São Paulo Grand Prix", "Grand Prix de São Paulo", "Gran Premio di San Paolo", "São Paulo", "São Paulo", "Gran Premio de São Paulo", "Grande Prêmio de São Paulo"),
    "Thailand": ("Thailand", "Thaïlande", "Thailandia", "Thai Grand Prix", "Grand Prix de Thaïlande", "Gran Premio di Thailandia", "Tailandia", "Tailândia", "Gran Premio de Tailandia", "Grande Prêmio da Tailândia"),
    "Tschechien": ("Czech Republic", "Tchéquie", "Repubblica Ceca", "Czech Grand Prix", "Grand Prix de Tchéquie", "Gran Premio della Repubblica Ceca", "Chequia", "Tchéquia", "Gran Premio de la República Checa", "Grande Prêmio da República Tcheca"),
    "Türkei": ("Türkiye", "Turquie", "Turchia", "Turkish Grand Prix", "Grand Prix de Turquie", "Gran Premio di Turchia", "Turquía", "Turquia", "Gran Premio de Turquía", "Grande Prêmio da Turquia"),
    "USA": ("USA", "États-Unis", "Stati Uniti", "United States Grand Prix", "Grand Prix des États-Unis", "Gran Premio degli Stati Uniti", "EE. UU.", "EUA", "Gran Premio de Estados Unidos", "Grande Prêmio dos Estados Unidos"),
    "Ungarn": ("Hungary", "Hongrie", "Ungheria", "Hungarian Grand Prix", "Grand Prix de Hongrie", "Gran Premio d'Ungheria", "Hungría", "Hungria", "Gran Premio de Hungría", "Grande Prêmio da Hungria"),
    "Valencia": ("Valencia", "Valence", "Valencia", "Valencia Grand Prix", "Grand Prix de Valence", "Gran Premio di Valencia", "Valencia", "Valência", "Gran Premio de la Comunitat Valenciana", "Grande Prêmio de Valência"),
    "Österreich": ("Austria", "Autriche", "Austria", "Austrian Grand Prix", "Grand Prix d'Autriche", "Gran Premio d'Austria", "Austria", "Áustria", "Gran Premio de Austria", "Grande Prêmio da Áustria"),
    # nur MXGP / Motocross
    "Andalusien": ("Andalusia", "Andalousie", "Andalusia", None, None, None, "Andalucía", "Andaluzia", None, None),
    "Flandern": ("Flanders", "Flandre", "Fiandre", None, None, None, "Flandes", "Flandres", None, None),
    "Lettland": ("Latvia", "Lettonie", "Lettonia", None, None, None, "Letonia", "Letônia", None, None),
    "Niederlande": ("the Netherlands", "Pays-Bas", "Paesi Bassi", None, None, None, "Países Bajos", "Holanda", None, None),
    "Sardinien": ("Sardinia", "Sardaigne", "Sardegna", None, None, None, "Cerdeña", "Sardenha", None, None),
    "Schweden": ("Sweden", "Suède", "Svezia", None, None, None, "Suecia", "Suécia", None, None),
    "Schweiz": ("Switzerland", "Suisse", "Svizzera", None, None, None, "Suiza", "Suíça", None, None),
    "Trentino": ("Trentino", "Trentin", "Trentino", None, None, None, "Trentino", "Trentino", None, None),
}
# französische Präposition + Artikel für „MXGP de …“
FR_DE = {"Andalusien": "d'", "Argentinien": "d'", "Australien": "d'", "Deutschland": "d'", "Italien": "d'",
         "Niederlande": "des ", "Portugal": "du ", "Tschechien": "de ", "Türkei": "de ", "Flandern": "de ",
         "Frankreich": "de ", "Grossbritannien": "de ", "Lettland": "de ", "Sardinien": "de ", "Schweden": "de ",
         "Schweiz": "de ", "Spanien": "d'", "Trentino": "du ", "China": "de "}
IT_DI = {"Niederlande": "dei ", "Tschechien": "della ", "Türkei": "di ", "Schweiz": "di ", "Portugal": "del ",
         "Trentino": "del ", "Andalusien": "dell'", "Argentinien": "dell'", "Australien": "dell'", "Italien": "d'"}

# portugiesische Präposition + Artikel für „MXGP da …“
PT_DE = {"Niederlande": "da ", "Portugal": "de ", "Trentino": "do ", "Flandern": "de ", "China": "da ",
         "Schweden": "da ", "Lettland": "da ", "Andalusien": "da ", "Sardinien": "da ", "Schweiz": "da "}

# Orte mit deutschem Namen (Event-Ort und F2/F3/Supercup-Titel)
LOCATIONS = {
    "Dschidda": t("Jeddah", "Djeddah", "Gedda", "Yeda", "Jidá"),
    "Mexiko-Stadt": t("Mexico City", "Mexico", "Città del Messico", "Ciudad de México", "Cidade do México"),
    "Tokio": t("Tokyo", "Tokyo", "Tokyo", "Tokio", "Tóquio"),
    "Brünn": t("Brno", "Brno", "Brno", "Brno", "Brno"),
    "Rom": t("Rome", "Rome", "Roma", "Roma", "Roma"),
    "Montréal": t("Montreal", "Montréal", "Montréal", "Montreal", "Montreal"),
    "Nürnberg": t("Nuremberg", "Nuremberg", "Norimberga", "Núremberg", "Nuremberg"),
    "Spanien": t("Spain", "Espagne", "Spagna", "España", "Espanha"),
    "Portugal": t("Portugal", "Portugal", "Portogallo", "Portugal", "Portugal"),
    "Schweiz": t("Switzerland", "Suisse", "Svizzera", "Suiza", "Suíça"),
    "KAEC (bei Dschidda)": t("KAEC (near Jeddah)", "KAEC (près de Djeddah)", "KAEC (vicino a Gedda)", "KAEC (cerca de Yeda)", "KAEC (perto de Jidá)"),
    "Toyota (Aichi)": t("Toyota (Aichi)", "Toyota (Aichi)", "Toyota (Aichi)", "Toyota (Aichi)", "Toyota (Aichi)"),
}

RALLIES = {
    "Rallye Monte-Carlo": t("Rallye Monte-Carlo", "Rallye Monte-Carlo", "Rallye Monte-Carlo", "Rally de Montecarlo", "Rali de Monte Carlo"),
    "Rallye Schweden": t("Rally Sweden", "Rallye de Suède", "Rally di Svezia", "Rally de Suecia", "Rali da Suécia"),
    "Safari Rallye Kenia": t("Safari Rally Kenya", "Safari Rally Kenya", "Safari Rally Kenya", "Safari Rally Kenia", "Safari Rally Quênia"),
    "Rallye Kroatien": t("Croatia Rally", "Rallye de Croatie", "Rally di Croazia", "Rally de Croacia", "Rali da Croácia"),
    "Rallye Islas Canarias": t("Rally Islas Canarias", "Rallye des Canaries", "Rally delle Canarie", "Rally Islas Canarias", "Rali Ilhas Canárias"),
    "Rallye Japan": t("Rally Japan", "Rallye du Japon", "Rally del Giappone", "Rally de Japón", "Rali do Japão"),
    "Akropolis-Rallye": t("Acropolis Rally", "Rallye de l'Acropole", "Rally dell'Acropoli", "Rally Acrópolis", "Rali da Acrópole"),
    "Rallye Italien (Rom)": t("Rally Italy (Rome)", "Rallye d'Italie (Rome)", "Rally d'Italia (Roma)", "Rally de Italia (Roma)", "Rali da Itália (Roma)"),
    "Rallye Estland": t("Rally Estonia", "Rallye d'Estonie", "Rally d'Estonia", "Rally de Estonia", "Rali da Estônia"),
    "Rallye Finnland": t("Rally Finland", "Rallye de Finlande", "Rally di Finlandia", "Rally de Finlandia", "Rali da Finlândia"),
    "Rallye USA": t("Rally USA", "Rallye des États-Unis", "Rally degli Stati Uniti", "Rally de EE. UU.", "Rali dos EUA"),
    "Rallye Schottland": t("Rally Scotland", "Rallye d'Écosse", "Rally di Scozia", "Rally de Escocia", "Rali da Escócia"),
    "Rallye Paraguay": t("Rally Paraguay", "Rallye du Paraguay", "Rally del Paraguay", "Rally de Paraguay", "Rali do Paraguai"),
    "Rallye Chile": t("Rally Chile", "Rallye du Chili", "Rally del Cile", "Rally de Chile", "Rali do Chile"),
    "Rallye Saudi-Arabien": t("Rally Saudi Arabia", "Rallye d'Arabie saoudite", "Rally dell'Arabia Saudita", "Rally de Arabia Saudí", "Rali da Arábia Saudita"),
}

SUFFIXES = [
    (" (Showrennen)", t(" (exhibition)", " (course d'exhibition)", " (esibizione)", " (exhibición)", " (exibição)")),
    (" (Finale)", t(" (finale)", " (finale)", " (finale)", " (final)", " (final)")),
    (" · 6h-Rennen", t(" · 6h race", " · course de 6 h", " · gara di 6 ore", " · carrera de 6 h", " · corrida de 6 h")),
    (" · Saisonfinale", t(" · season finale", " · finale de la saison", " · finale di stagione", " · final de temporada", " · final da temporada")),
]
FIXED_NAMES = {
    "Motocross der Nationen": t("Motocross of Nations", "Motocross des Nations", "Motocross delle Nazioni", "Motocross de las Naciones", "Motocross das Nações"),
    "Rallye Dakar 2027": t("Dakar Rally 2027", "Rallye Dakar 2027", "Rally Dakar 2027", "Rally Dakar 2027", "Rali Dakar 2027"),
    "Isle of Man TT": t("Isle of Man TT", "TT de l'île de Man", "TT dell'Isola di Man", "TT de la Isla de Man", "TT da Ilha de Man"),
}


def _session_name(name):
    if name in SESSION_NAMES:
        return SESSION_NAMES[name]
    if re.match(PROPER_NAMES, name):
        return t(name, name, name, name, name)
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
            inner = _event_name(base) or t(base, base, base, base, base)
            return {lang: inner[lang] + forms[lang] for lang in LANGS}
    m = re.match(r"^(?:Grosser Preis|Grand Prix) (?:von|der) (.+)$", name)
    if m and m.group(1) in PLACES and PLACES[m.group(1)][3]:
        p = PLACES[m.group(1)]
        return t(p[3], p[4], p[5], p[8], p[9])
    m = re.match(r"^(\d+) Stunden von (.+)$", name)
    if m:
        n, place = m.groups()
        fr_prep = "d'" if place[0] in "AEIOUÉ" else "de "
        if place.startswith("Le "):
            place_fr = "du " + place[3:]
            return t(f"{n} Hours of {place}", f"{n} Heures {place_fr}", f"{n} Ore di {place}",
                     f"{n} Horas de {place}", f"{n} Horas de {place}")
        it_prep = "d'" if place[0] in "AEIOU" else "di "
        return t(f"{n} Hours of {place}", f"{n} Heures {fr_prep}{place}", f"{n} Ore {it_prep}{place}",
                 f"{n} Horas de {place}", f"{n} Horas de {place}")
    m = re.match(r"^MXGP (?:von|der) (.+)$", name)
    if m and m.group(1) in PLACES:
        key = m.group(1)
        return t(f"MXGP of {_place(key, 0)}", f"MXGP {FR_DE.get(key, 'de ')}{_place(key, 1)}",
                 f"MXGP {IT_DI.get(key, 'di ')}{_place(key, 2)}", f"MXGP de {_place(key, 6)}",
                 f"MXGP {PT_DE.get(key, 'da ')}{_place(key, 7)}")
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
