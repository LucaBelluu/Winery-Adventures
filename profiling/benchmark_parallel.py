"""Benchmark della parallelizzazione del calcolo dello stress per cisterna.

Confronta l'esecuzione seriale con la parallelizzazione a thread e a processi di
Joblib, sul dataset di grandi dimensioni. Il confronto isola due effetti: il
contributo del flag ``nogil`` (thread con e senza rilascio del GIL) e il divario
tra thread e processi.

L'accumulo di produzione avviene per effetto collaterale in una lista condivisa,
schema corretto solo con i thread, che condividono la memoria del processo. La
variante a processi presente in questo script raccoglie invece i valori
restituiti, poiché processi distinti non condividono la lista: è una variante di
solo confronto, non lo schema di produzione.

Esecuzione dalla radice della repository, come modulo::

    python -m profiling.benchmark_parallel

Il dataset va generato in precedenza con ``data_generator.py`` e atteso in
``data/full_sensors.tsv``.
"""

import time
from pathlib import Path

import joblib
import polars as pl
from numba import njit

from winery_adventures.computations import pairwise_stress_function

SENSORS_PATH = Path("data/full_sensors.tsv")


# Variante senza ``nogil``, per il resto identica alla funzione di produzione,
# utile a isolare il contributo del rilascio del GIL nel confronto a thread.
@njit(fastmath=True, cache=True)
def _stress_gil(pH_vals, temp_vals, quantity_vals):
    n = len(pH_vals)
    if n == 0:
        return 0.0
    s = 0.0
    for i in range(n):
        for j in range(i + 1, n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            qf = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])
            s += (pH_dev + t_dev) * qf
    return (2.0 * s) / (n * n)


def _arrays(group: pl.DataFrame):
    """Estrae gli array NumPy di una cisterna, escluse le letture prive di volume."""
    g = group.drop_nulls(subset="quantity_liters")
    return g["pH"].to_numpy(), g["temp"].to_numpy(), g["quantity_liters"].to_numpy().astype(float)


def compute_serial(partitions, fn) -> dict:
    """Calcola lo stress di ogni cisterna in sequenza, senza parallelismo."""
    return {key[0]: fn(*_arrays(group)) for key, group in partitions.items()}


def compute_threads(partitions, fn, n_jobs: int) -> dict:
    """Calcola lo stress con backend a thread e accumulo per effetto collaterale."""
    results: list = []

    def one(tank_id, group):
        results.append((tank_id, fn(*_arrays(group))))

    joblib.Parallel(n_jobs=n_jobs, prefer="threads")(
        joblib.delayed(one)(key[0], group) for key, group in partitions.items()
    )
    return dict(results)


def _stress_return(tank_id, arrays):
    """Restituisce la coppia ``(tank_id, stress)``, adatta al backend a processi."""
    return tank_id, pairwise_stress_function(*arrays)


def compute_processes(partitions, n_jobs: int) -> dict:
    """Calcola lo stress con backend a processi, raccogliendo i valori restituiti."""
    payload = [(key[0], _arrays(group)) for key, group in partitions.items()]
    out = joblib.Parallel(n_jobs=n_jobs, backend="loky")(
        joblib.delayed(_stress_return)(tid, arr) for tid, arr in payload
    )
    return dict(out)


def _best(func, repetitions: int = 5) -> float:
    """Restituisce il tempo minimo di ``func`` dopo un riscaldamento iniziale."""
    func()  # riscaldamento: compilazione JIT e avvio del pool
    best = float("inf")
    for _ in range(repetitions):
        start = time.perf_counter()
        func()
        best = min(best, time.perf_counter() - start)
    return best


def main() -> None:
    """Misura e stampa i tempi delle quattro strategie di esecuzione."""
    sensors = pl.read_csv(SENSORS_PATH, separator="\t")
    partitions = sensors.partition_by("tank_id", as_dict=True)
    print(f"Dataset: {sensors.height} letture, {len(partitions)} cisterne, {joblib.cpu_count()} core")

    # Controllo di coerenza: le strategie devono produrre gli stessi valori.
    ref = compute_serial(partitions, pairwise_stress_function)
    assert compute_threads(partitions, pairwise_stress_function, -1) == ref
    assert dict(compute_processes(partitions, -1)) == ref

    t_serial = _best(lambda: compute_serial(partitions, pairwise_stress_function))
    t_threads_nogil = _best(lambda: compute_threads(partitions, pairwise_stress_function, -1))
    t_threads_gil = _best(lambda: compute_threads(partitions, _stress_gil, -1))
    t_processes = _best(lambda: compute_processes(partitions, -1))

    print(f"  seriale (1 job)             = {t_serial * 1000:8.1f} ms   (1.00x)")
    print(f"  thread + nogil (produzione) = {t_threads_nogil * 1000:8.1f} ms   ({t_serial / t_threads_nogil:.2f}x)")
    print(f"  thread SENZA nogil          = {t_threads_gil * 1000:8.1f} ms   ({t_serial / t_threads_gil:.2f}x)")
    print(f"  processi (loky)             = {t_processes * 1000:8.1f} ms   ({t_serial / t_processes:.2f}x)")


if __name__ == "__main__":
    main()