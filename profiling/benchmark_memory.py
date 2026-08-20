"""Profilazione della memoria del calcolo dello stress.

Misura due aspetti distinti. Il primo è la memoria ausiliaria della formula: il
ciclo compilato accumula uno scalare e non materializza la matrice delle coppie,
quindi occupa memoria O(1) oltre agli array di ingresso; una variante
vettorizzata equivalente, presente qui a solo scopo di confronto, costruisce
matrici n×n e occupa memoria O(n²). Il secondo è il picco di memoria dell'intero
processo durante ``analyze_data`` sul dataset di grandi dimensioni.

Due strumenti per due ambiti: ``tracemalloc`` osserva le allocazioni lato Python,
inclusi gli array NumPy, ma non la memoria nativa di Polars; il picco RSS del
processo, letto da ``resource``, comprende l'intero processo, Polars inclusa, ma
dipende dalla piattaforma e include la compilazione JIT una tantum.

Esecuzione dalla radice della repository, come modulo::

    python -m profiling.benchmark_memory

Il dataset va generato in precedenza con ``data_generator.py`` e atteso in
``data/full_sensors.tsv``.
"""

import resource
import sys
import tracemalloc
from pathlib import Path

import numpy as np
import polars as pl

from winery_adventures.computations import WineryHPCComputations, pairwise_stress_function

SENSORS_PATH = Path("data/full_sensors.tsv")


def _stress_vectorized(pH, temp, quantity):
    """Variante vettorizzata di confronto: costruisce matrici n×n, memoria O(n²)."""
    n = len(pH)
    if n == 0:
        return 0.0
    pH_dev = np.abs(pH[:, None] - pH[None, :])
    t_dev = np.abs(temp[:, None] - temp[None, :]) * 2.0
    qf = 500.0 / quantity[:, None] + 500.0 / quantity[None, :]
    return ((pH_dev + t_dev) * qf).sum() / (n * n)


def _tracemalloc_peak(func) -> int:
    """Restituisce il picco di memoria lato Python, in byte, durante ``func``."""
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak


def _process_peak_rss_mb() -> float:
    """Picco di memoria residente del processo, in MB (unità dipendente dalla piattaforma)."""
    raw = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    byte = raw if sys.platform == "darwin" else raw * 1024  # macOS: byte; Linux: KB
    return byte / 1024 / 1024


def main() -> None:
    """Misura la memoria della formula e il picco del processo, e ne stampa il confronto."""
    sensors = pl.read_csv(SENSORS_PATH, separator="\t")
    valid = sensors.drop_nulls(subset="quantity_liters")
    largest = max(valid.partition_by("tank_id", as_dict=True).values(), key=lambda g: g.height)
    pH = largest["pH"].to_numpy()
    temp = largest["temp"].to_numpy()
    quantity = largest["quantity_liters"].to_numpy().astype(float)
    n = len(pH)

    pairwise_stress_function(pH, temp, quantity)  # riscaldamento della compilazione JIT

    peak_loop = _tracemalloc_peak(lambda: pairwise_stress_function(pH, temp, quantity))
    peak_vec = _tracemalloc_peak(lambda: _stress_vectorized(pH, temp, quantity))

    print(f"Memoria ausiliaria della formula (cisterna con n={n} letture):")
    print(f"  array di ingresso            = {3 * n * 8 / 1024:8.1f} KB")
    print(f"  ciclo compilato (produzione) = {peak_loop / 1024:8.1f} KB   (memoria O(1))")
    print(f"  variante vettorizzata        = {peak_vec / 1024 / 1024:8.2f} MB   (memoria O(n^2))")

    WineryHPCComputations().analyze_data(sensors)
    print(f"\nPicco RSS del processo dopo analyze_data su {sensors.height} letture: {_process_peak_rss_mb():.0f} MB")
    print("  (comprende Python, le librerie, il dataset e la compilazione JIT una tantum)")


if __name__ == "__main__":
    main()