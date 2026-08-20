"""Benchmark della formula di stress da fermentazione.

Confronta l'implementazione di produzione ``pairwise_stress_function`` (variante
ottimizzata per simmetria dei contributi, definita in
``winery_adventures.computations``) con un'implementazione di riferimento a ciclo
pieno, presente in questo modulo al solo scopo di confronto e non usata in
produzione. Il confronto riguarda due aspetti: la correttezza (i due risultati
devono coincidere entro la tolleranza della somma in virgola mobile) e il tempo
di esecuzione, misurato sia sulla singola funzione sia sull'intera
``analyze_data``.

Esecuzione dalla radice della repository, come modulo::

    python -m profiling.benchmark_stress

L'esecuzione come modulo pone la radice della repository sul percorso di ricerca
dei moduli, condizione necessaria all'import di ``winery_adventures``. Il dataset
di grandi dimensioni va generato in precedenza con ``data_generator.py`` e atteso
in ``data/full_sensors.tsv``.
"""

import time
from pathlib import Path

import numpy as np
import polars as pl
from numba import njit

from winery_adventures.computations import WineryHPCComputations, pairwise_stress_function

# Percorso del dataset di grandi dimensioni prodotto da ``data_generator.py``.
SENSORS_PATH = Path("data/full_sensors.tsv")


# Implementazione di riferimento a ciclo pieno O(n²), fedele all'algoritmo del
# README. Presente unicamente come termine di paragone per il benchmark: la
# versione di produzione, ottimizzata per simmetria, vive in
# ``winery_adventures.computations``.
@njit
def _baseline_full_loop(pH_vals: np.ndarray, temp_vals: np.ndarray, quantity_vals: np.ndarray) -> float:
    n = len(pH_vals)
    if n == 0:
        return 0.0
    stress_sum = 0.0
    for i in range(n):
        for j in range(n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])
            stress_sum += (pH_dev + t_dev) * quantity_factor
    return stress_sum / (n * n)


def _best_time(func, repetitions: int) -> float:
    """Restituisce il tempo minimo di ``func`` su un numero dato di ripetizioni.

    Il minimo è preferito alla media perché meno sensibile ai disturbi del
    sistema operativo, che possono solo rallentare una misura, mai accelerarla.

    :param func: callable senza argomenti da cronometrare.
    :param repetitions: numero di esecuzioni da confrontare.
    :returns: tempo minimo osservato, in secondi.
    """
    times = []
    for _ in range(repetitions):
        start = time.perf_counter()
        func()
        times.append(time.perf_counter() - start)
    return min(times)


def main() -> None:
    """Esegue il confronto e stampa correttezza e tempi delle due varianti."""
    sensors = pl.read_csv(SENSORS_PATH, separator="\t")

    # Le rilevazioni prive di volume sono escluse, coerentemente con il calcolo
    # dello stress per cisterna.
    valid = sensors.drop_nulls(subset="quantity_liters")
    groups = valid.partition_by("tank_id", as_dict=True)

    # Riscaldamento della compilazione JIT: la prima chiamata a una funzione
    # Numba compila in codice macchina e non rappresenta il tempo a regime.
    sample = next(iter(groups.values()))
    warm = (sample["pH"].to_numpy(), sample["temp"].to_numpy(), sample["quantity_liters"].to_numpy().astype(float))
    pairwise_stress_function(*warm)
    _baseline_full_loop(*warm)

    # Correttezza: differenza massima tra le due varianti su tutte le cisterne.
    max_diff = 0.0
    for group in groups.values():
        args = (group["pH"].to_numpy(), group["temp"].to_numpy(),
                group["quantity_liters"].to_numpy().astype(float))
        max_diff = max(max_diff, abs(pairwise_stress_function(*args) - _baseline_full_loop(*args)))

    # Tempo a livello di singola funzione sulla cisterna con più letture.
    largest = max(groups.values(), key=lambda g: g.height)
    big_args = (largest["pH"].to_numpy(), largest["temp"].to_numpy(),
                largest["quantity_liters"].to_numpy().astype(float))
    t_base_fn = _best_time(lambda: _baseline_full_loop(*big_args), 200)
    t_sym_fn = _best_time(lambda: pairwise_stress_function(*big_args), 200)

    # Tempo end-to-end dell'analizzatore completo sull'intero dataset.
    analyzer = WineryHPCComputations()
    analyzer.analyze_data(sensors)  # riscaldamento
    t_e2e = _best_time(lambda: analyzer.analyze_data(sensors), 7)

    print(f"Dataset: {sensors.height} letture, {len(groups)} cisterne")
    print(f"Correttezza (differenza massima su tutte le cisterne): {max_diff:.2e}")
    print(f"Cisterna più grande: {largest.height} letture")
    print(f"  ciclo pieno (riferimento):   {t_base_fn * 1000:.3f} ms")
    print(f"  simmetria (produzione):      {t_sym_fn * 1000:.3f} ms")
    print(f"  speedup di funzione:         {t_base_fn / t_sym_fn:.2f}x")
    print(f"analyze_data completo (simmetria): {t_e2e * 1000:.1f} ms")


if __name__ == "__main__":
    main()