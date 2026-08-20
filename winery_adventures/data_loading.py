"""Caricamento dei dati di ingresso della pipeline da file TSV.

Il modulo fornisce le funzioni di lettura dei due file sorgente del sistema: le
letture dei sensori e le informazioni sulle cisterne. Entrambi i file adottano
il formato TSV (valori separati da tabulazione). La stringa dei vitigni presente
nelle informazioni sulle cisterne viene suddivisa in lista, formato atteso dalla
trasformazione che conta le letture per vitigno.
"""

import polars as pl


def load_sensor_data(path: str) -> pl.DataFrame:
    """Carica le letture dei sensori da un file TSV.

    :param path: percorso del file TSV con colonne ``tank_id``, ``time``,
        ``pH``, ``temp``, ``quantity_liters``.
    :returns: DataFrame Polars con le letture dei sensori.
    """
    # Il separatore di tabulazione distingue il TSV dal CSV a virgole.
    return pl.read_csv(path, separator="\t")


def load_tank_info(path: str) -> pl.DataFrame:
    """Carica le informazioni sulle cisterne da un file TSV.

    La colonna ``grape_variety`` contiene i vitigni separati da virgola e viene
    trasformata in lista di stringhe, formato richiesto dalla trasformazione che
    conta le letture per vitigno.

    :param path: percorso del file TSV con colonne ``tank_id``,
        ``grape_variety``, ``capacity_liters``.
    :returns: DataFrame Polars con la colonna ``grape_variety`` suddivisa in
        lista.
    """
    tank_info = pl.read_csv(path, separator="\t")
    # Suddivisione della stringa dei vitigni in lista: "A,B,C" diventa
    # ["A", "B", "C"], pronta per l'esplosione nelle trasformazioni.
    return tank_info.with_columns(pl.col("grape_variety").str.split(","))
