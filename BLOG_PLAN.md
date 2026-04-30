# Football Analytics Blog — Detaillierter Plan

## Positionierung

**Zielgruppe:** Data Scientists und Python-Entwickler mit Fußballinteresse, sowie Fußball-Enthusiasten mit Interesse an Daten. Kein Vorwissen in Football Analytics notwendig — die Serie baut systematisch auf.

**Ton:** Analytisch aber zugänglich. Kein akademisches Paper, aber auch kein reiner Fan-Blog. Jeder Artikel hat konkreten Mehrwert: entweder lernst du etwas über Python/Data Science, oder du verstehst Fußball tiefer.

**Datenbasis:** Statsbomb Open Data (kostenlos, frei verwendbar mit Credit)
- 868 La-Liga-Spiele (2004–2021) — Hauptquelle
- Women's World Cup 2019 & 2023 — inkl. 360°-Daten für 2023
- UEFA Euro 2020 & 2024 — inkl. 360°-Daten
- Bundesliga 2023/24 — inkl. 360°-Daten
- Champions League Finals (18 Spiele)
- FA WSL (3 Saisons), NWSL (2018)

**Tech Stack:** Python, pandas, matplotlib, mplsoccer, networkx, Jupyter Notebooks

---

## Säule 1: Einstieg in die Welt der Fußballanalyse

*Ziel dieser Serie: Leser ohne Vorkenntnisse abholen und ihnen die Werkzeuge in die Hand geben, eigene Analysen zu bauen. Notebook-Format, viel Code, viel Erklärung.*

---

### Artikel 1.1 — Die Daten hinter dem Spiel: Einführung in Football Analytics

**Hook:** Jedes Mal wenn ein Spieler den Ball berührt, entsteht ein Datenpunkt. Ein einziges Spiel erzeugt über 3.000 Events. Was steckt dahinter?

**Inhalt:**
- Was ist Event-Data? Erklärung des Statsbomb-Datenmodells
- Überblick der Eventtypen: Pass, Shot, Carry, Pressure, Duel, ...
- Wie ist eine JSON-Datei aufgebaut? Erste Schritte im Notebook
- Das Koordinatensystem: Pitch-Dimensionen (120×80 Yards), Ursprung links unten
- Erste einfache Abfragen: Wie viele Pässe hat Team X gespielt? Wer hat am meisten geschossen?

**Datenbasis:** Ein einzelnes Bundesliga-Spiel (Bayer Leverkusen vs. Werder Bremen, 5:0)
**Visualisierung:** Tabelle der Event-Typen mit Häufigkeiten, einfacher Bar Chart
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐☆☆☆☆
**Code-Anteil:** Hoch — jeder Schritt erklärt

---

### Artikel 1.2 — Ein Fußballfeld in Python zeichnen (von Null)

**Hook:** Bevor wir Daten visualisieren, brauchen wir eine Leinwand. So baust du ein sauberes Fußballfeld mit reinem matplotlib — ohne fertige Bibliotheken.

**Inhalt:**
- matplotlib-Grundlagen: Figures, Axes, Patches
- Pitch Schritt für Schritt: Außenlinien, Mittelkreis, Strafräume, Tore, Elfmeterpunkte
- Koordinaten korrekt setzen, Aspect Ratio beachten
- Pitch-Farben: helles vs. dunkles Theme
- Bonus: mplsoccer als Shortcut vorstellen

**Datenbasis:** Keine Daten — reine Visualisierungsübung
**Visualisierung:** Fertige Pitch-Grafik (hell + dunkel)
**Länge:** ~1.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆
**Code-Anteil:** Sehr hoch — Schritt-für-Schritt-Build

---

### Artikel 1.3 — Shot Maps: Wo schießt ein Team?

**Hook:** Eine Shot Map sagt mehr über ein Team als jede Torstatistik. So baust du sie in Python.

**Inhalt:**
- Shot-Events aus den Daten extrahieren
- xG erklären: Was bedeutet der Wert, wie wird er berechnet?
- Schüsse auf dem Pitch plotten: Position, xG als Punktgröße, Outcome als Farbe
- Beide Teams nebeneinander — normalisierte Angriffsrichtung
- Interpretation: Was verrät die Shot Map über das Spiel?

**Datenbasis:** La Liga 2020/21 (mit 360°-Daten als Bonus)
**Visualisierung:** Shot Map für ein konkretes Spiel (Heim + Auswärts)
**Länge:** ~1.200 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆
**Code-Anteil:** Hoch

---

### Artikel 1.4 — Pass-Netzwerke: Wer spielt mit wem?

**Hook:** Ein Pass-Netzwerk macht das Spiel einer Mannschaft sichtbar — welche Verbindungen dominieren, wer ist zentral, wer ist isoliert?

**Inhalt:**
- Pass-Events filtern: nur erfolgreiche Pässe
- Durchschnittliche Spielerposition berechnen (aus allen Ballaktionen)
- Verbindungsstärke: Wie viele Pässe zwischen Spieler A und B?
- NetworkX + matplotlib: Knoten (Spieler), Kanten (Pässe), Gewichtung
- Lesehilfe: Was verrät das Netzwerk taktisch?
- Variation: Vergleich 1. Halbzeit vs. 2. Halbzeit nach Einwechslung

**Datenbasis:** La Liga 2015/16 (Barcelona oder Real Madrid)
**Visualisierung:** Pass-Netzwerk auf Pitch, farbkodiert nach Pässen
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆
**Code-Anteil:** Hoch
**Bibliotheken:** networkx

---

### Artikel 1.5 — Heatmaps: Wo ist ein Spieler oder Team aktiv?

**Hook:** Heatmaps zeigen auf einem Blick, in welchen Zonen ein Team spielt — und wo es vermeidet zu spielen.

**Inhalt:**
- Touch-Events aggregieren (alle Events mit Koordinaten)
- 2D-Histogramm vs. KDE (Kernel Density Estimation) — Unterschiede und Wann was
- mplsoccer Pitch mit eingebautem Heatmap-Support
- Anwendung 1: Pressing-Zonen (wo findet Pressure statt?)
- Anwendung 2: Touch Map eines Spielers über eine Saison

**Datenbasis:** La Liga 2015/16 (Messi Touch Map) oder Bundesliga 2023/24 (Pressing Bayer Leverkusen)
**Visualisierung:** Side-by-Side Heatmap Heim vs. Auswärts, Spieler-Heatmap
**Länge:** ~1.200 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆
**Code-Anteil:** Mittel

---

## Säule 2: Tactical Analysis

*Ziel: Taktische Konzepte mit Daten erklären und belegen. Weniger "wie programmiere ich das", mehr "was sagen uns die Daten". Code bleibt präsent, steht aber nicht im Mittelpunkt.*

---

### Artikel 2.1 — Was ist xG — und warum liegt es manchmal falsch?

**Hook:** Expected Goals sind überall. Aber was berechnet das Modell eigentlich — und wann sollte man ihm nicht trauen?

**Inhalt:**
- xG-Modell erklärt: Welche Faktoren fließen ein? (Position, Körperteil, Spielsituation, Vorbereitungsaktion)
- xG vs. tatsächliche Tore: Über eine Saison sollte es sich annähern — über ein Spiel oft nicht
- Visualisierung: xG-Verlauf über einen Spieltag (Cumulative xG Chart)
- Wer überperformt dauerhaft? Wer unterperformt? (La Liga Karrieredaten)
- Grenzen des Modells: Was xG nicht misst (Keeper-Position, Ablenker)

**Datenbasis:** La Liga 2015/16 (komplette Saison, 380 Spiele)
**Visualisierungen:** xG vs. Tore Scatter, Cumulative xG für ein Spiel, Saison-Ranking
**Länge:** ~2.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆

---

### Artikel 2.2 — Pressing messen: Was steckt hinter PPDA?

**Hook:** Jedes Team presst — aber nicht jedes Team presst gleich effektiv. PPDA macht den Unterschied messbar.

**Inhalt:**
- PPDA erklärt: Passes Per Defensive Action
- Formel: Pässe des Gegners im Angriffsdrittel / Defensive Aktionen im Angriffsdrittel
- Implementierung mit Statsbomb-Daten (Pressure Events + Pässe)
- PPDA über eine Saison berechnen und Teams ranken
- Vergleich: Welche Teams pressen hoch, welche tief?
- Bonus: Korrelation PPDA mit Tabellenplatz?

**Datenbasis:** La Liga 2015/16 (alle 20 Teams, 380 Spiele)
**Visualisierungen:** PPDA-Ranking Bar Chart, PPDA vs. Punkte Scatter
**Länge:** ~1.800 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 2.3 — Through Balls: Die riskanteste Passart

**Hook:** Ein perfekter Through Ball ist der schwierigste Pass im Fußball. Wer spielt ihn am häufigsten — und wann zahlt er sich aus?

**Inhalt:**
- Pass-Felder: `through_ball`, `goal_assist`, `shot_assist` kombinieren
- Wie oft endet ein Through Ball in einem Schuss? In einem Tor?
- Spieler-Ranking: Wer spielt die meisten Through Balls? Wer ist am erfolgreichsten?
- Visualisierung: Woher kommen Through Balls (Origin Map), wohin gehen sie?
- Vergleich: Through Ball vs. Cross — Effizienz zum Torabschluss

**Datenbasis:** La Liga 2015/16 (alle Spiele)
**Visualisierungen:** Origin-Heatmap, Erfolgsquoten-Vergleich, Top-Spieler Bar Chart
**Länge:** ~1.800 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 2.4 — Freeze Frames: Wer steht wo beim Schuss?

**Hook:** Für jeden Schuss in den Statsbomb-Daten existiert ein Foto — die Positionen aller Spieler auf dem Feld in dem Moment. Das ist das versteckte Juwel.

**Inhalt:**
- Was sind Freeze Frames? Erklärung der Datenstruktur
- Visualisierung eines einzelnen Tores: Spielerpositionen, Torwart, Schütze
- Warum ist Torhüter-Position für xG relevant?
- Analyse: Wie viele Spieler stehen vor dem Ball bei einem Schuss? (Blocked Shot Analyse)
- Bonus: One-on-One-Situationen (`shot.one_on_one`) — wie oft werden sie genutzt?

**Datenbasis:** La Liga 2020/21 oder Bundesliga 2023/24 (Freeze Frame Daten vorhanden)
**Visualisierungen:** Einzelner Schuss mit allen Spielerpositionen, Aggregate View
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 2.5 — Carry-Daten: Dribblings & Ballführung verstehen

**Hook:** Pässe und Schüsse bekommen die Aufmerksamkeit. Aber Carries — also Ballführungen — verraten, wie ein Team Raum überbrückt.

**Inhalt:**
- Was ist ein Carry? Unterschied zu Pass und Dribbling
- Progressive Carries: Wer trägt den Ball am häufigsten vorwärts?
- Carry-Länge und -Richtung analysieren
- Welche Zonen werden durch Carries überbrückt? (Start → End Location Arrows)
- Verknüpfung: Carry → Shot: Wie oft führt eine Ballführung direkt zu einem Schuss?

**Datenbasis:** La Liga 2015/16
**Visualisierungen:** Arrow Map (Carry-Richtungen), Progressions-Ranking
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 2.6 — 360°-Daten: Die nächste Stufe der Fußballanalyse

**Hook:** Klassische Event-Daten sagen, was passiert. 360°-Daten sagen, wer dabei stand. Das verändert alles.

**Inhalt:**
- Was sind 360°-Daten? Erklärung der Frames und visible_area
- Welche Wettbewerbe haben 360°-Daten? (Euro 2024, WM 2023, Bundesliga 2023/24)
- Anwendung 1: Raum hinter der Abwehrlinie bei einem Pass visualisieren
- Anwendung 2: Pressing-Situations rekonstruieren — wie nah sind Gegenspieler?
- Limitierung: visible_area — was ist im Bild, was nicht?
- Ausblick: Was könnte man mit vollständigen Tracking-Daten machen?

**Datenbasis:** UEFA Euro 2024 oder Bundesliga 2023/24
**Visualisierungen:** Frame-Visualisierung mit Spielerpositionen, visible_area Polygon
**Länge:** ~2.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐⭐☆

---

## Säule 3: Physical Performance Analytics

*Ziel: GPS-Tracking-Daten verstehen und analysieren. Eine andere Datenwelt als Event-Daten — keine Pässe, keine Schüsse, sondern Distanzen, Geschwindigkeiten, Beschleunigungen. Datenbasis: synthetisches Dataset aus veröffentlichten sportwissenschaftlichen Benchmarks (Mohr et al. 2003, Bradley et al. 2009, Di Salvo et al. 2007).*

---

### Artikel P.1 — GPS Tracking: What the Numbers Actually Mean ✓

**Hook:** Jeder Profi trägt eine GPS-Weste. Das Gerät zeichnet seine Position mehrmals pro Sekunde auf. Was wird daraus gemacht?

**Inhalt:**
- Was misst GPS? Distanzzonen, Geschwindigkeitszonen, Beschleunigungen
- Positionsprofile: Wer läuft wie viel und wie schnell?
- m/min als Normalisierungsmetrik für verschiedene Spielzeiten
- Warum Gesamtdistanz allein nichts sagt

**Datenbasis:** Synthetisches Dataset (380 Spiele, 20 Teams, 8 Positionen)
**Visualisierungen:** Positions-Profile (6 Metriken), Distanzverteilung, m/min-Ranking
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆
**Status:** ✓ Fertig

---

### Artikel P.2 — Sprint Profiles: Speed Zones by Position

**Hook:** Wer ist schneller — ein Außenverteidiger oder ein Stürmer? Die Antwort hängt davon ab, was man unter "schnell" versteht.

**Inhalt:**
- Max Speed Verteilung nach Position
- Sprint Count und Sprint Distance im Vergleich
- Wie verteilen sich Sprints über 90 Minuten? (erste vs. zweite Halbzeit)
- "Speed Profile" eines Spielers: Einstufung nach Geschwindigkeitszone

**Datenbasis:** Synthetisches Dataset
**Visualisierungen:** Speed-Zone-Stacked-Bar, Sprint-Scatter nach Position, Halbzeit-Vergleich
**Länge:** ~1.200 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆

---

### Artikel P.3 — Distance Covered: More Is Not Always Better

**Hook:** Der Spieler mit der höchsten Gesamtdistanz ist selten der wertvollste. Warum der Kontext zählt.

**Inhalt:**
- Total Distance vs. High Intensity Distance
- Wie Spielstil die Distanzwerte beeinflusst (Pressing vs. tiefer Block)
- Home vs. Away: Unterschiede in physischer Belastung
- Substitutes vs. Starters: m/min als fairer Vergleich

**Datenbasis:** Synthetisches Dataset
**Visualisierungen:** Scatter xG vs. Distanz, Team-Ranking HI Distance, Box-Plots
**Länge:** ~1.200 Wörter + Notebook
**Schwierigkeit:** ⭐⭐☆☆☆

---

### Artikel P.4 — Accelerations: The Hidden Fitness Metric

**Hook:** Nicht die Topspeed macht einen Spieler physisch teuer — es sind die Starts und Stopps.

**Inhalt:**
- Was ist eine Beschleunigung? Medium vs. High Threshold
- Warum Beschleunigungen besser als Distanz für Verletzungsrisiko sind
- Count High Acceleration als "Neuromuscular Load"-Proxy
- Welche Positionen haben die höchste Beschleunigungsbelastung?

**Datenbasis:** Synthetisches Dataset
**Visualisierungen:** Acceleration vs. Total Distance Scatter, Position-Ranking, Correlation Heatmap
**Länge:** ~1.200 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel P.5 — Pressing Space from 360° Data

**Hook:** GPS misst Distanz. Statsbomb 360° misst Raum. Dieser Artikel verbindet beide Welten.

**Inhalt:**
- Was sind 360°-Freeze-Frames? (kurze Wiederholung aus 2.6)
- Abstände zwischen Pressing-Spieler und Ballbesitzer messen
- Pressing-Intensität als räumliche Metrik: Wie eng ist der Raum?
- Vergleich: Leverkusen vs. Werder Bremen — wer presst enger?

**Datenbasis:** Statsbomb 360° (Bundesliga 2023/24) + Verknüpfung mit physischen Konzepten
**Visualisierungen:** Freeze-Frame mit Distanzlinien, Pressing-Enge-Histogramm
**Länge:** ~1.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

## Säule 4: Deep Dive Analysen

*Ziel: Story-getriebene, längere Analysen mit konkreten Erkenntnissen. Weniger Tutorial, mehr Journalismus mit Datenbasis. Jeder Artikel hat eine These, die durch Daten beantwortet wird.*

---

### Artikel 4.1 — Messi in La Liga: 15 Jahre in Zahlen

**Hook:** Lionel Messi spielte 17 Saisons für den FC Barcelona. Die Statsbomb-Daten decken einen Großteil davon ab — genug, um seine Entwicklung datenbasiert nachzuzeichnen.

**These:** Messis Spielweise hat sich über seine Karriere fundamental verändert — von explosivem Dribbler zum Spielmacher.

**Inhalt:**
- xG pro Saison: Wann war Messi der gefährlichste Torschütze?
- Schussprofile je Saison: Verändert sich wo er abschließt?
- Assists und key passes über die Jahre
- Dribbling-Frequenz im Zeitverlauf (abnehmend?)
- Touch Map pro Saison: Wandert er auf den Flügel oder ins Zentrum?
- Vergleich: Messi als Neun (2015/16) vs. Messi als zehner

**Datenbasis:** La Liga 2004/05 bis 2020/21 (14 Saisons)
**Visualisierungen:** Karriere-Timeline-Chart, Season-by-Season Shot Map, Touch Map Evolution
**Länge:** ~3.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 4.2 — Die beste Ligasaison aller Zeiten? Barcelona 2015/16 in Daten

**Hook:** 2015/16 schoss Barcelona 112 Tore, gewann die Liga mit 91 Punkten — und hatte mit Messi, Suárez und Neymar den gefährlichsten Angriff der Geschichte. Was sagen die Daten?

**These:** Die Statsbomb-Daten für die vollständige 2015/16-Saison (380 Spiele) erlauben einen einzigartigen Blick auf das dominanteste Team dieser Ära.

**Inhalt:**
- Liga-Tabelle und xG-Tabelle im Vergleich: Wer hatte wirklich das beste Team?
- Barças xG für und gegen — wie dominant war der Angriff, wie sicher die Abwehr?
- Das MSN-Trio in Zahlen: Messi, Suárez, Neymar — wer war in welcher Situation am gefährlichsten?
- Pressing-Analyse: War Barça 2015/16 auch defensiv dominant?
- Vergleich mit dem Rest der Liga: Wie weit war Barça wirklich vorne?

**Datenbasis:** La Liga 2015/16 (380 Spiele, alle Teams)
**Visualisierungen:** xG-Tabelle, MSN Shot Profile, Liga-Pressing-Vergleich
**Länge:** ~3.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐⭐☆

---

### Artikel 4.3 — Frauenfußball in Zahlen: WM 2019 vs. WM 2023

**Hook:** Vier Jahre zwischen zwei Weltmeisterschaften. Hat sich der Frauenfußball taktisch und spielerisch verändert — und was sagen die Daten?

**These:** Der Frauenfußball 2023 ist schneller, intensiver und taktisch reifer als 2019.

**Inhalt:**
- Spieltempo: Pässe pro Minute, Spieldauer mit Ballbesitz
- Pressing-Intensität: PPDA im Turnier-Vergleich
- xG-Analyse: Werden die Chancen besser oder schlechter genutzt?
- Torhüter-Daten: Reaktionen und Saves im Vergleich
- 360°-Bonus (2023): Raumsituationen bei Schüssen
- Die dominantesten Teams beider Turniere im direkten Vergleich

**Datenbasis:** Women's World Cup 2019 (52 Spiele) + 2023 (64 Spiele, inkl. 360°)
**Visualisierungen:** Side-by-Side Kennzahlen, xG-Verteilung, Pressing-Heatmaps
**Länge:** ~3.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐⭐☆

---

### Artikel 4.4 — Champions-League-Finals: Wenn Daten auf Legenden treffen

**Hook:** 18 Champions-League-Spiele, darunter einige der ikonischsten Partien der Fußballgeschichte. Was haben die Daten festgehalten?

**These:** Die Daten zeigen, dass die größten CL-Überraschungen keine Zufälle waren — sie hatten taktische Ursachen.

**Inhalt:**
- Welche Finals sind in den Daten? (Überblick)
- Ein Spiel vollständig seziert (z.B. das spektakulärste verfügbare): Minute für Minute xG-Verlauf
- Pressing-Analyse: Welches Team hat das Spiel dominiert — und warum zeigt das Ergebnis etwas anderes?
- Shot Maps beider Finalis
- Historischer Vergleich: Wie haben sich die Finals über die Jahre verändert?

**Datenbasis:** Champions League Finals (18 Spiele, 2003/04–2018/19)
**Visualisierungen:** Cumulative xG Chart, Shot Maps, Momentum-Grafik
**Länge:** ~2.500 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐☆☆

---

### Artikel 4.5 — Bayer Leverkusen 2023/24: Die Saison ohne Niederlage in Daten

**Hook:** Ungeschlagen durch eine komplette Bundesliga-Saison. War das Glück oder Genialität — und was sagen die Daten?

**These:** Leverkusens Unbesiegbarkeit war keine Anomalie. Die Daten zeigen ein Team, das in kritischen Momenten systematisch besser war als der Gegner.

**Inhalt:**
- xG für und gegen pro Spieltag: Wann hatten sie Glück, wann waren sie überlegen?
- Pressing-Profil: Wie hoch und wie intensiv war Leverkusens Pressing?
- Späte Tore: Statistik der Comebacks in Nachspielzeit (Datenbasis + ergänzende Recherche)
- 360°-Daten: Raumsituationen bei entscheidenden Toren
- Vergleich mit anderen ungeschlagenen Saisons (Arsenal 2003/04) — sofern Daten vorhanden

**Datenbasis:** Bundesliga 2023/24 (34 Spiele, inkl. 360°-Daten)
**Visualisierungen:** xG-Timeline Saison, Pressing-Heatmap, Cumulative Punkte vs. xG-Punkte
**Länge:** ~3.000 Wörter + Notebook
**Schwierigkeit:** ⭐⭐⭐⭐☆

---

## Veröffentlichungsreihenfolge

```
BATCH 1 — Serie 1 komplett (bereit zum Publizieren)
  1.1 · 1.2 · 1.3 · 1.4 · 1.5

BATCH 2 — Serie 2: Tactical Analysis
  2.1 xG · 2.2 PPDA · 2.3 Through Balls · 2.4 Freeze Frames · 2.5 Carries · 2.6 360°

BATCH 3 — Serie 3: Physical Performance
  P.1 GPS Intro · P.2 Sprints · P.3 Distance · P.4 Accelerations · P.5 Pressing Space

BATCH 4 — Serie 4: Deep Dives
  4.4 Champions League Finals (kürzerer Einstieg)
  4.1 Messi Karriere
  4.2 Barcelona 2015/16
  4.5 Leverkusen 2023/24
  4.3 Frauen-WM Vergleich
```

---

## Technische Infrastruktur pro Artikel

| Element | Format |
|---|---|
| Haupttext | Markdown / Blog-Post (Englisch) |
| Code | Jupyter Notebook |
| Daten Serie 1–2, 4 | Statsbomb Open Data (lokal) |
| Daten Serie 3 | Synthetisches GPS-Dataset (aus Benchmarks generiert) |
| Grafiken | PNG exportiert (matplotlib/mplsoccer), eingebettet im Artikel |

---

*Stand: April 2026 — 21 Artikel geplant (16 Statsbomb + 5 Physical Performance)*
