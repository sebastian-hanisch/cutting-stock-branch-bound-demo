"""
Branch & Bound am Cutting-Stock-Problem – interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Wurzel der zweiten Exakte-Suche-Linie (Cutting-Stock-Linie): derselbe methodische
Bogen wie die Rucksack-Linie, aber auf dem klassischen 1D-Cutting-Stock-Problem statt
Rucksack - Vorbereitung für Column Generation und Branch & Price, die eigentlichen
neuen Stücke dieser Linie.

Lauffähig mit: streamlit run app.py
"""

import time

import streamlit as st

import csbb_constants as C
from csbb_bounds import weak_bound
from csbb_bruteforce import solve_bruteforce
from csbb_evaluation import stats_up_to_step, symmetry_comparison
from csbb_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from csbb_scenario import expand_pieces, generate_instance
from csbb_solver import solve
from csbb_visualization import build_tree_figure

st.set_page_config(page_title="Cutting Stock Branch & Bound – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _compute_solve(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    result = solve(instance, weak_bound)
    true_optimum = solve_bruteforce(instance)
    return instance, result, true_optimum


@st.cache_data(show_spinner=False)
def _compute_symmetry_comparison(n_types, roll_width, max_demand, seed):
    instance = generate_instance(n_types, roll_width, max_demand, seed)
    return symmetry_comparison(instance, weak_bound)


st.title("🌳📏 Branch & Bound am Cutting-Stock-Problem")
st.markdown(
    """
Wurzel einer zweiten Exakte-Suche-Linie: dasselbe Grundprinzip wie
[branch-bound-demo](https://github.com/sebastian-hanisch/branch-bound-demo), aber ein
anderes Vehikel-Problem - das klassische **1D-Cutting-Stock-Problem**: eine Rolle
fester Breite, mehrere Auftragsbreiten mit Bedarf, gesucht die minimale Anzahl
Rollen. Über die Brücke "Bedarfsmengen zu Einzelstücken aufgelöst" wird daraus **Bin
Packing** - packe alle Stücke in die minimale Anzahl Bins. Genau **wie** der
Suchbaum dabei verzweigt, erklärt der aufgeklappte Abschnitt direkt darunter.
"""
)
st.caption(
    "Anders als die Fall-Demos im Portfolio, die an einem Anwendungsfall mehrere Verfahren "
    "vergleichen, zeigt diese Demo - wie branch-bound-demo aus der ersten Exakte-Suche-Linie - "
    "ein Verfahren an einem wachsenden Beispiel. Bewusst ein zweites, komplexeres Vehikel-"
    "Problem: die kommenden Stücke dieser Linie (Column Generation, Branch & Price) "
    "brauchen ein Problem, dessen Struktur reine Rucksack-Instanzen nicht hergeben."
)

with st.expander("So funktioniert die Suche", expanded=True):
    st.markdown(
        r"""
Die Stücke werden absteigend nach Breite sortiert (First-Fit-Decreasing-Reihenfolge)
und der Reihe nach platziert. An jedem Suchbaum-Knoten hat das nächste Stück mehrere
Optionen: in eines der bereits geöffneten Bins, in das es noch passt - oder ein neues
Bin öffnen. Jede Option ist ein eigener Ast.

**Bewusst KEINE Regel gegen austauschbare (symmetrische) Bins**: zwei leere oder
gleich gefüllte Bins sind für das Ergebnis komplett gleichwertig, aber die Suche
behandelt sie trotzdem als unterschiedliche Optionen - genau das ist Bin Packings
berüchtigte, ehrliche Schwäche. Siehe "📐 Wie viel kostet Symmetrie wirklich?" weiter
unten, wie stark das den Suchbaum tatsächlich aufbläht.

Eine Schranke (untere Grenze für die noch nötige Bin-Anzahl) schneidet Äste ab, die
den bisher besten Fund nicht mehr unterbieten können - im Baum unten so beschriftet:

- **"Verzweigt (weiter untersucht)"** - hier wird noch weiterentschieden.
- **"Gestutzt (Bound zu schwach)"** - abgebrochen, weil selbst die optimistische
  Schranke keine Verbesserung mehr verspricht.
- **"Neue beste Lösung"** - ein vollständiger Kandidat mit weniger Bins als bisher.
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
PRESET_HELP = {
    "Winzige Instanz (Baum komplett sichtbar)": "3 Aufträge, je einmal - der komplette Suchbaum passt aufs Bild.",
    "Spürbare Symmetrie (mehrere gleich breite Aufträge)": "Mehrere Aufträge derselben Breite - der Suchbaum ist hier über 12× größer, als er sein müsste, siehe der Vergleich weiter unten.",
    "Größere Instanz (der Baum wächst deutlich)": "6 Auftragstypen mit höherem Bedarf - der Suchbaum wächst spürbar, bleibt aber in Sekundenbruchteilen lösbar.",
}
preset_cols = st.columns(len(C.PRESETS))
for i, name in enumerate(C.PRESETS.keys()):
    with preset_cols[i]:
        st.button(name, use_container_width=True, on_click=apply_preset, args=(name,), help=PRESET_HELP[name])

st.caption(
    "🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, "
    "um ein Szenario zu teilen."
)

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    n_types = st.slider("Anzahl Auftragstypen", *bounds("n_types_slider"), key="n_types_slider")
    roll_width = st.slider("Rollenbreite", *bounds("roll_width_slider"), key="roll_width_slider")
    max_demand = st.slider(
        "Maximaler Bedarf je Auftragstyp", *bounds("max_demand_slider"), key="max_demand_slider",
        help="Höherer Bedarf bedeutet mehr identische Stücke - mehr Symmetrie im Suchbaum.",
    )
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1)

    st.button(
        "🎲 Neue Instanz generieren",
        use_container_width=True,
        on_click=randomize_seed,
        help="Würfelt neue Auftragsbreiten und -mengen.",
    )

sync_query_params(n_types, roll_width, max_demand, seed)

scenario_key = (int(n_types), int(roll_width), int(max_demand), int(seed))

with st.spinner("Durchsuche den Baum..."):
    instance, result, true_optimum = _compute_solve(*scenario_key)

pieces = expand_pieces(instance)
st.caption(
    f"🔗 {instance.n_types} Auftragstypen, Breiten {instance.item_widths} mit Bedarf "
    f"{instance.item_demands} → {len(pieces)} Einzelstücke, Rollenbreite {instance.roll_width}."
)

st.markdown("## 🎯 Der Suchbaum in Aktion")

if "csbb_step" not in st.session_state or st.session_state.get("csbb_step_owner") != scenario_key:
    st.session_state["csbb_step"] = len(result.nodes) - 1
    st.session_state["csbb_step_owner"] = scenario_key

max_step = len(result.nodes) - 1
step_col, play_col = st.columns([5, 1])
with step_col:
    if max_step == 0:
        step = 0
        st.caption("Nur der Wurzelknoten - kein Regler nötig.")
    else:
        step = st.slider(
            "Schritt (Knoten)", 0, max_step, key="csbb_step",
            help="Ein Schritt = ein besuchter Suchbaum-Knoten, in Besuchsreihenfolge.",
        )
with play_col:
    auto_play = st.button("▶️ Abspielen", use_container_width=True)

render_note = (
    f" (zeigt die ersten {C.MAX_NODES_RENDERED:,} von {len(result.nodes):,} Knoten)"
    if len(result.nodes) > C.MAX_NODES_RENDERED
    else ""
)
st.caption(f"{len(result.nodes):,} Knoten insgesamt besucht{render_note}.")

tree_slot = st.empty()


def _render(current_step):
    tree_slot.plotly_chart(
        build_tree_figure(instance, result, current_step, C.MAX_NODES_RENDERED),
        use_container_width=True, key=f"tree_{current_step}",
    )


if auto_play:
    n_frames = min(max_step + 1, 60)
    frame_skip = max(1, (max_step + 1) // n_frames)
    for s in list(range(0, max_step, frame_skip)) + [max_step]:
        _render(s)
        time.sleep(0.08)
    step = max_step
else:
    _render(step)

live = stats_up_to_step(result, step)
lm1, lm2, lm3 = st.columns(3)
lm1.metric("Besuchte Knoten (bisher)", f"{live['nodes_so_far']:,}")
lm2.metric(
    "Gestutzt (Bound)", f"{live['pruned_bound']:,}",
    help="Äste, die abgebrochen wurden, weil die Schranke keine Verbesserung mehr versprach.",
)
lm3.metric(
    "Bester Fund bisher", live["current_best"] if live["current_best"] is not None else "–",
    help="Die wenigsten Rollen einer bislang vollständig gefundenen Lösung.",
)

if result.truncated:
    st.error(
        f"⛔ Abgebrochen bei {C.MAX_NODES_EXPLORED:,} untersuchten Knoten - das gezeigte Ergebnis ist die "
        f"beste bislang gefundene, nicht garantiert optimale Lösung."
    )
else:
    st.caption(
        f"Bewiesenes Optimum: **{result.best_value}** Rollen - stimmt mit der unabhängigen "
        f"Bruteforce-Referenz überein."
        if result.best_value == true_optimum
        else f"⚠️ Optimum {result.best_value} weicht von der Bruteforce-Referenz {true_optimum} ab - bitte melden."
    )

st.markdown("---")

st.subheader("📐 Wie viel kostet Symmetrie wirklich?")
st.markdown(
    """
Live für Ihre aktuelle Instanz: derselbe Suchlauf, einmal normal, einmal mit
künstlich aufgebrochener Symmetrie (jedes Einzelstück wird zu seinem eigenen,
winzig abweichenden Auftragstyp - die Packungsstruktur bleibt praktisch identisch,
nur die exakte Gleichheit zwischen austauschbaren Stücken verschwindet).
"""
)

cmp = _compute_symmetry_comparison(*scenario_key)
cc1, cc2, cc3 = st.columns(3)
cc1.metric(
    "Normale Instanz", f"{cmp['normal_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["normal_truncated"] else ""),
)
cc2.metric(
    "Symmetrie aufgebrochen", f"{cmp['desym_nodes']:,} Knoten" + (" (abgebrochen)" if cmp["desym_truncated"] else ""),
    delta=f"{cmp['desym_nodes'] - cmp['normal_nodes']:,} ggü. normal", delta_color="inverse",
)
cc3.metric("Beide finden dasselbe Optimum", cmp["normal_best"])

factor = cmp["normal_nodes"] / cmp["desym_nodes"] if cmp["desym_nodes"] else float("inf")
if cmp["normal_best"] != cmp["desym_best"]:
    st.warning("⚠️ Die beiden Varianten sind sich uneinig - das sollte nie passieren, bitte melden.")
elif factor >= 1.5:
    st.success(
        f"✅ Bei dieser Instanz durchsucht die normale (symmetrische) Version **{factor:.1f}×** so viele "
        f"Knoten wie die entsymmetrisierte - für dasselbe bewiesene Optimum. Der Unterschied ist reine "
        f"Verschwendung: rein austauschbare Bin-Reihenfolgen, kein zusätzlicher Erkenntnisgewinn."
    )
else:
    st.info(
        "Bei dieser Instanz macht sich Symmetrie kaum bemerkbar - probieren Sie das Preset "
        "\"Spürbare Symmetrie\" oder mehrere Aufträge derselben Breite."
    )

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Cutting Stock, ein Rollentyp**: Rollenbreite $W$, $n$ Auftragstypen mit Breite
$w_i$ und Bedarf $q_i$. Minimiere die Anzahl benötigter Rollen. Über die Brücke
"Bedarf zu Einzelstücken aufgelöst" identisch zu **Bin Packing**: packe alle
Einzelstücke in die minimale Anzahl Bins der Kapazität $W$.

**Schranken** (untere Grenze für die insgesamt benötigte Bin-Anzahl):

$$
L_1 = |\text{Bins}| + \left\lceil \frac{\max(0,\ \text{Restbreite} - \text{Restkapazität offener Bins})}{W} \right\rceil
$$

Eine zweite, unabhängig gültige Schranke berücksichtigt, dass Stücke mit Breite
$> W/2$ nie zu zweit in einem Bin liegen können. **Überraschender Fund beim
Kalibrieren**: bei dieser (absteigenden) Verzweigungsreihenfolge ändert diese
zweite Schranke die Knotenzahl nie - jedes vorher platzierte Stück ist mindestens so
breit wie das aktuelle, lässt also höchstens $W/2$ Restkapazität übrig. Ein Stück
mit Breite $> W/2$ kann strukturell also nie in ein bereits geöffnetes Bin passen -
die Verzweigung erzeugt die "passt in bestehendes Bin"-Option für solche Stücke
deshalb nie überhaupt. Die zweite Schranke verhindert genau das, was die
Suchreihenfolge schon unmöglich macht: keine neue Information, kein zusätzliches
Pruning. Implementiert (und mit einem eigenen Test dauerhaft belegt) in
`csbb_bounds.py`.

Implementiert in `csbb_solver.py` (Tiefensuche), `csbb_bounds.py` (Schranken) und
`csbb_bruteforce.py` (unabhängige Referenzlösung für Tests).
        """
    )

st.markdown("---")

st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
