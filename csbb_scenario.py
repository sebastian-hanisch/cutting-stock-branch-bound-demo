"""Zufällige 1D-Cutting-Stock-Instanzen, EIN Rollentyp - die klassische Gilmore-
Gomory-Lehrbuchversion (die bereits bestehende Fall-Demo cutting-stock-demo nutzt
mehrere Rollentypen; hier bewusst nur einer, damit die kompakte Formulierung und
alle folgenden Stücke dieser Linie handhabbar bleiben)."""

from dataclasses import dataclass

import numpy as np

from csbb_constants import WIDTH_FRACTION_RANGE


@dataclass(frozen=True)
class CuttingStockInstance:
    roll_width: int
    item_widths: tuple  # eine Breite je Auftragstyp
    item_demands: tuple  # Bedarf (Menge) je Auftragstyp, parallel zu item_widths

    @property
    def n_types(self):
        return len(self.item_widths)


def generate_instance(n_types, roll_width, max_demand, seed):
    rng = np.random.default_rng(seed)
    lo = max(1, round(WIDTH_FRACTION_RANGE[0] * roll_width))
    hi = max(lo + 1, round(WIDTH_FRACTION_RANGE[1] * roll_width))
    widths = rng.integers(lo, hi + 1, size=n_types)
    demands = rng.integers(1, max_demand + 1, size=n_types)
    return CuttingStockInstance(
        roll_width=int(roll_width),
        item_widths=tuple(int(w) for w in widths),
        item_demands=tuple(int(d) for d in demands),
    )


def desymmetrized_instance(instance, scale=1000):
    """Dieselbe Instanz, aber jede Bedarfseinheit wird zu einem EIGENEN Auftragstyp
    mit Bedarf 1 und einer winzigen, eindeutigen Breiten-Abweichung - bricht exakte
    Gleichheit zwischen austauschbaren Stücken auf, ohne die Packungsstruktur
    nennenswert zu verändern (Skalierung um `scale`, damit die Abweichung
    verschwindend klein bleibt). Nur für den "Was kostet Symmetrie?"-Vergleich in
    app.py - keine echte alternative Instanz, sondern ein Vergleichs-Experiment."""
    widths = []
    for w, q in zip(instance.item_widths, instance.item_demands):
        for k in range(q):
            widths.append(w * scale + k)
    return CuttingStockInstance(
        roll_width=instance.roll_width * scale,
        item_widths=tuple(widths),
        item_demands=tuple(1 for _ in widths),
    )


def expand_pieces(instance):
    """Bedarfsmengen zu individuellen Stück-Objekten expandiert, absteigend nach
    Breite sortiert (First-Fit-Decreasing-Reihenfolge) - die Brücke zu Bin Packing:
    packe alle Einzelstücke in die minimale Anzahl Rollen."""
    pieces = []
    for w, q in zip(instance.item_widths, instance.item_demands):
        pieces.extend([w] * q)
    pieces.sort(reverse=True)
    return tuple(pieces)
