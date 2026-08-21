"""Test aggiuntivi sui casi limite non coperti dalle specifiche fornite.

Il modulo verifica il comportamento della formula di stress sui casi degeneri,
a integrazione dei test forniti con il progetto. Copre in particolare il ramo di
guardia che intercetta l'insieme vuoto di rilevazioni, a tutela della robustezza
della funzione.
"""

import numpy as np

from winery_adventures.computations import pairwise_stress_function


def test_pairwise_stress_empty_returns_zero():
    """La formula restituisce 0.0 su array vuoti, senza divisione per zero."""
    empty = np.array([], dtype=np.float64)
    assert pairwise_stress_function(empty, empty, empty) == 0.0