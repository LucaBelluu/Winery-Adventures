"""Calcoli ad alte prestazioni sui dati dei sensori delle cisterne.

Il modulo espone la formula di stress da fermentazione, funzione libera con
complessità O(n²) compilata con Numba, e l'analizzatore concreto
``WineryHPCComputations`` che la applica per cisterna e aggiunge la colonna
``stress_score`` al DataFrame in ingresso.

Lo stress cresce al crescere della variabilità di pH e temperatura tra le
rilevazioni e al ridursi del volume di mosto: cisterne piccole e letture
disomogenee segnalano un rischio maggiore di fermentazione irregolare.
"""

import joblib
import numpy as np
import polars as pl
from numba import njit

from winery_adventures.base import BaseWineryAnalyzer


# ``@njit`` compila la funzione in codice macchina alla prima chiamata
# (nopython mode), requisito di ottimizzazione richiesto dalla consegna per la
# formula O(n²). Il corpo resta puramente numerico su array NumPy, senza oggetti
# Python, condizione necessaria alla compilazione nopython.
@njit
def pairwise_stress_function(pH_vals: np.ndarray, temp_vals: np.ndarray, quantity_vals: np.ndarray) -> float:
    """Calcola lo stress di fermentazione su un insieme di rilevazioni.

    La formula confronta ogni coppia ordinata di rilevazioni ``(i, j)`` e
    accumula il contributo dato dalla differenza di pH, dalla differenza di
    temperatura (pesata due volte) e da un fattore inversamente proporzionale al
    volume di mosto delle due cisterne. La somma finale è normalizzata sul
    numero di coppie ``n * n``.

    :param pH_vals: array dei valori di pH per ogni rilevazione.
    :param temp_vals: array dei valori di temperatura per ogni rilevazione.
    :param quantity_vals: array dei volumi di mosto in litri per ogni rilevazione.
    :returns: valore singolo di stress complessivo; ``0.0`` per array vuoti.
    """
    n = len(pH_vals)
    if n == 0:
        return 0.0
    stress_sum = 0.0
    # Doppio ciclo pieno da 0 a n-1, fedele all'algoritmo del README: ogni coppia
    # ordinata è considerata, comprese le coppie identiche (i == j), che portano
    # contributo nullo.
    for i in range(n):
        for j in range(n):
            pH_dev = abs(pH_vals[i] - pH_vals[j])
            t_dev = abs(temp_vals[i] - temp_vals[j]) * 2.0
            quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])
            stress_sum += (pH_dev + t_dev) * quantity_factor
    return stress_sum / (n * n)


class WineryHPCComputations(BaseWineryAnalyzer):
    """Analizzatore che calcola lo stress di fermentazione per ogni cisterna.

    Raggruppa le letture per ``tank_id``, valuta lo stress su ciascun gruppo con
    ``pairwise_stress_function`` e riporta il risultato, costante all'interno del
    gruppo, su ogni riga della cisterna nella colonna ``stress_score``.
    """

    def _stress_for_group(self, tank_id: int, group: pl.DataFrame, results: list) -> None:
        """Valuta lo stress di una singola cisterna e ne registra l'esito.

        Le rilevazioni prive di ``quantity_liters`` sono escluse dal calcolo,
        poiché un volume ignoto non può alimentare un fattore che divide per il
        volume. L'esito è accodato a ``results`` come coppia ``(tank_id, stress)``:
        l'accumulo per effetto collaterale permette di ignorare il valore di
        ritorno del backend parallelo.

        :param tank_id: identificativo della cisterna.
        :param group: sottoinsieme di letture appartenenti alla cisterna.
        :param results: lista condivisa su cui accodare l'esito.
        """
        group = group.drop_nulls(subset="quantity_liters")
        pH = group["pH"].to_numpy()
        temp = group["temp"].to_numpy()
        quantity = group["quantity_liters"].to_numpy()
        results.append((tank_id, pairwise_stress_function(pH, temp, quantity)))

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge ``stress_score`` calcolato per cisterna.

        :param df: letture dei sensori con colonne ``tank_id``, ``pH``, ``temp``
            e ``quantity_liters``.
        :returns: il DataFrame in ingresso con la colonna ``stress_score``.
        """
        # Partiziona le letture per cisterna: ogni gruppo è un'unità di calcolo
        # indipendente, adatta alla parallelizzazione.
        partitions = df.partition_by("tank_id", as_dict=True)

        # ``results`` raccoglie gli esiti prodotti dai task paralleli. Il backend
        # a thread condivide la memoria del processo, quindi l'accodamento resta
        # visibile al termine; ``list.append`` è atomico sotto il GIL di CPython.
        results: list[tuple[int, float]] = []
        joblib.Parallel(n_jobs=-1, prefer="threads")(
            joblib.delayed(self._stress_for_group)(key[0], group, results) for key, group in partitions.items()
        )

        # Riporta lo stress di ogni cisterna su tutte le sue righe tramite una
        # mappa ``tank_id -> stress_score``.
        stress_by_tank = {tank_id: stress for tank_id, stress in results}
        return df.with_columns(
            pl.col("tank_id").replace_strict(stress_by_tank, return_dtype=pl.Float64).alias("stress_score")
        )