"""Defaults, slider bounds und Presets für die Cutting-Stock-Branch-&-Bound-Demo."""

DEFAULT_N_TYPES = 4
DEFAULT_MAX_DEMAND = 2
DEFAULT_ROLL_WIDTH = 100
DEFAULT_SEED = 7

N_TYPES_MIN, N_TYPES_MAX = 2, 6
MAX_DEMAND_MIN, MAX_DEMAND_MAX = 1, 4
ROLL_WIDTH_MIN, ROLL_WIDTH_MAX = 50, 200

# Auftragsbreiten werden als Anteil der Rollenbreite gezogen - hält die Instanzen
# unabhängig von der absoluten Rollenbreite vergleichbar.
WIDTH_FRACTION_RANGE = (0.15, 0.6)

# Bin-Packing-Suchbäume explodieren ohne Symmetrie-Mitigation (bewusst keine hier,
# siehe README) schon bei winzigen Instanzen - per Stresstest kalibriert: bei
# n_types=6/max_demand=4 erreicht etwa jede zehnte Instanz die Grenze (22 von 240:
# Seeds 0-59, Rollenbreiten 50/80/100/200); ein Lauf mit 100.000 Knoten dauert rund
# 0,7 s. Die App zeigt das als "abgebrochen" an (keine bewiesene Optimalität).
MAX_NODES_EXPLORED = 100_000
# Die Bruteforce-Gegenprobe der App hat keine Schranke und braucht bei großen Instanzen
# Minuten (gemessen bis 373 s bei 6 Typen, Bedarf 4, 23 Stücke); darum ein Aufrufbudget
# (rund 1,6 Mio. Aufrufe je Sekunde): wird es überschritten, entfällt die Gegenprobe.
MAX_BRUTEFORCE_CALLS = 500_000
MAX_NODES_RENDERED = 800

PRESETS = {
    "Winzige Instanz (Baum komplett sichtbar)": {
        "n_types": 3, "roll_width": 100, "max_demand": 1, "seed": 1,
    },
    "Spürbare Symmetrie (mehrere gleich breite Aufträge)": {
        "n_types": 5, "roll_width": 100, "max_demand": 3, "seed": 76,
    },
    "Größere Instanz (der Baum wächst deutlich)": {
        "n_types": 6, "roll_width": 100, "max_demand": 4, "seed": 15,
    },
}
