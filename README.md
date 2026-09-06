# Branch & Bound am Cutting-Stock-Problem – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-cutting-stock-branch-bound-demo.streamlit.app/)**

Wurzel der **zweiten** Exakte-Suche-Linie der "Konzepte"-Reihe für die Website
"Sebastian Hanisch – Operations Research und Machine Learning": derselbe
methodische Bogen wie die erste Linie ([branch-bound-demo](https://github.com/sebastian-hanisch/branch-bound-demo)
→ [dynamic-programming-demo](https://github.com/sebastian-hanisch/dynamic-programming-demo)
→ [cutting-planes-demo](https://github.com/sebastian-hanisch/cutting-planes-demo) →
[branch-cut-demo](https://github.com/sebastian-hanisch/branch-cut-demo) →
[constraint-programming-demo](https://github.com/sebastian-hanisch/constraint-programming-demo)),
aber auf einem zweiten Vehikel-Problem: dem klassischen **1D-Cutting-Stock-Problem**
(ein Rollentyp, mehrere Auftragsbreiten und -mengen). Der Anlass für die zweite Linie:
**Column Generation** und **Branch-and-Price** brauchen ein Problem mit einer
natürlich exponentiell großen Musterformulierung - das gibt reines Rucksack nicht her.

Nicht zu verwechseln mit der bereits bestehenden **Fall-Demo**
[cutting-stock-demo](https://github.com/sebastian-hanisch/cutting-stock-demo)
(Column Generation vs. First-Fit-Decreasing-Heuristik, mehrere Rollentypen) - diese
Linie hier vergleicht **Verfahren gegen Verfahren** auf einem bewusst einfacheren,
einzigen Rollentyp, nicht Verfahren gegen Heuristik.

## Von Cutting Stock zu Bin Packing

Bedarfsmengen werden zu individuellen Stück-Objekten expandiert (Auftrag mit
Bedarf 3 → drei Einzelstücke derselben Breite) - dann ist das Problem exakt Bin
Packing: packe alle Einzelstücke in die minimale Anzahl Rollen (Bins). Die Suche
verzweigt an jedem Schritt n-är statt binär: das nächste Stück geht entweder in
eines der bereits geöffneten Bins, in das es noch passt, oder ein neues Bin wird
geöffnet.

## Bewusst keine Symmetrie-Mitigation

Bin Packing ist berüchtigt dafür, dass austauschbare (symmetrische) Bins den
Suchbaum unnötig aufblähen. Diese Demo baut das absichtlich NICHT weg - siehe den
live-berechneten "Wie viel kostet Symmetrie wirklich?"-Vergleich in der App (bis zu
~13× mehr Knoten bei spürbarer Symmetrie im eigenen Preset). Das ist der direkte
Aufhänger für das nächste Stück dieser Linie, `cutting-stock-cutting-planes-demo`
(Symmetrie-Schnitte).

## Ein überraschender Fund beim Kalibrieren: die "starke" Schranke hilft hier nicht

Der ursprüngliche Plan sah eine zweite, schärfere Schranke vor (Stücke mit Breite
> W/2 können nie zu zweit in einem Bin liegen). Mathematisch gültig, aber breite
Sweeps UND gezielt konstruierte Gegenbeispiele fanden ausnahmslos identische
Knotenzahlen gegenüber der einfachen Schranke. Der Grund ist beweisbar, nicht nur
empirisch: bei absteigender Verzweigungsreihenfolge ist jedes vorher platzierte
Stück mindestens so breit wie das aktuelle, lässt also höchstens $W/2$
Restkapazität übrig - ein Stück mit Breite $> W/2$ kann deshalb strukturell NIE in
ein bereits geöffnetes Bin passen, die Verzweigung erzeugt diese Option für solche
Stücke also nie. Die zweite Schranke verhindert damit exakt das, was die
Suchreihenfolge schon unmöglich macht. Bewusst nicht als (dann faktisch totem)
UI-Umschalter verbaut, sondern als dokumentierte, dauerhaft getestete Erkenntnis in
`csbb_bounds.py` belassen - siehe
`tests/test_solver.py::test_strong_bound_never_changes_node_count_given_descending_order`.

## Verifikation

- **Bound-Gültigkeit**: beide Schranken unterschätzen nie die wahre minimale
  Bin-Anzahl (gegen erschöpfende Enumeration aller Vervollständigungen geprüft).
- **Bruteforce-Cross-Check**: über viele Zufallsinstanzen und alle drei Presets.
- **Symmetrie-Invariante**: die entsymmetrisierte Variante einer Instanz muss
  dasselbe Optimum finden wie die Originalinstanz.
- **Schranken-Äquivalenz-Invariante**: siehe oben - dauerhaft als Test verankert.
- **Sicherheitsgrenzen**: `MAX_NODES_EXPLORED` wird zuverlässig eingehalten.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Hauptablauf: Presets, Einstellungen, Suchbaum-Animation, Symmetrie-Vergleich, Formulierungs-Expander |
| `csbb_constants.py` | Defaults, Regler-Grenzen, Sicherheitsgrenzen, `PRESETS` |
| `csbb_presets.py` | `SettingSpec`/`SETTING_SPECS`, Permalink-Logik, Presets, Zufalls-Seed-Button |
| `csbb_scenario.py` | Zufällige Cutting-Stock-Instanzen, Bin-Packing-Brücke, Entsymmetrisierung |
| `csbb_bounds.py` | `weak_bound` (L1), `strong_bound` (mit dem oben beschriebenen Fund) |
| `csbb_solver.py` | n-äre Tiefensuche mit vollständigem Knoten-Protokoll |
| `csbb_bruteforce.py` | Unabhängige Referenzlösung (vollständige Enumeration) |
| `csbb_evaluation.py` | Kennzahlen, Symmetrie-Vergleich |
| `csbb_visualization.py` | Suchbaum-Diagramm (Plotly) |
| `tests/` | Bound-Gültigkeit, Bruteforce-Cross-Check, Symmetrie- und Schranken-Invarianten, Sicherheitsgrenzen |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
