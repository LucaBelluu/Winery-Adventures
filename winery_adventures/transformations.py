"""Trasformazioni sui dati dei sensori delle cisterne di fermentazione.

Il modulo definisce ``WineryTransformer``, sottoclasse concreta di
``BaseWineryAnalyzer`` (definita nel modulo delle basi). La classe arricchisce
il DataFrame delle letture con statistiche calcolate per cisterna e per vitigno,
lasciando invariate le colonne di origine. Ogni trasformazione aggiunge una o
più colonne e restituisce un nuovo DataFrame, senza modificare quello ricevuto.
"""

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


class WineryTransformer(BaseWineryAnalyzer):
    """Applica in sequenza le trasformazioni sulle letture dei sensori.

    Il costruttore riceve le informazioni sulle cisterne, opzionali: servono
    soltanto alla trasformazione per vitigno. In loro assenza (default ``None``)
    tale trasformazione viene omessa dalla catena.
    """

    # Temperatura di riferimento della fermentazione, in gradi Celsius.
    # Costante di classe: identica per ogni istanza e usata come base della
    # deviazione di temperatura.
    STANDARD_TEMPERATURE = 26.0

    def __init__(self, tank_info: pl.DataFrame | None = None) -> None:
        """Conserva le informazioni sulle cisterne per l'uso nelle trasformazioni.

        :param tank_info: DataFrame con la colonna ``grape_variety`` già suddivisa
            in lista di stringhe, oppure ``None`` se le informazioni non servono.
        """
        self.tank_info = tank_info

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Concatena le trasformazioni in sequenza e restituisce il DataFrame arricchito.

        Applica prima le trasformazioni che preservano la grana dei dati (media del
        pH, conteggio delle letture, deviazione di temperatura) e, soltanto se sono
        disponibili le informazioni sulle cisterne, per ultima la trasformazione per
        vitigno, che esplode le righe. Questo ordine evita di falsare i conteggi per
        cisterna con le righe duplicate dall'esplosione e impedisce il sollevamento
        di ``AttributeError`` quando le informazioni sulle cisterne mancano.

        :param df: DataFrame delle letture dei sensori.
        :returns: DataFrame arricchito con le colonne prodotte dalle trasformazioni.
        """
        df = self.add_avg_ph_per_tank(df)
        df = self.add_num_readings_per_tank(df)
        df = self.add_temperature_deviation(df)
        # La trasformazione per vitigno richiede le informazioni sulle cisterne.
        if self.tank_info is not None:
            df = self.add_num_readings_per_grape_variety(df)
        return df

    def add_avg_ph_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge ``avg_pH_per_tank`` con il pH medio di ogni cisterna.

        La media viene calcolata per gruppo di ``tank_id`` e riportata su ogni
        riga del gruppo, senza ridurre il numero di righe.

        :param df: DataFrame delle letture dei sensori.
        :returns: DataFrame con la nuova colonna ``avg_pH_per_tank``.
        """
        return df.with_columns(pl.col("pH").mean().over("tank_id").alias("avg_pH_per_tank"))

    def add_num_readings_per_tank(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge ``tank_num_readings`` con il numero di letture di ogni cisterna.

        Il conteggio viene calcolato per gruppo di ``tank_id`` e riportato su ogni
        riga del gruppo, senza ridurre il numero di righe.

        :param df: DataFrame delle letture dei sensori.
        :returns: DataFrame con la nuova colonna ``tank_num_readings``.
        """
        return df.with_columns(pl.len().over("tank_id").alias("tank_num_readings"))

    def add_num_readings_per_grape_variety(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge ``grape_variety_num_readings`` con il numero di letture per vitigno.

        Esplode la lista dei vitigni conservata in ``self.tank_info`` (una riga per
        coppia cisterna-vitigno), unisce le informazioni alle letture tramite
        ``tank_id`` e conta le letture associate a ciascun vitigno. Un vitigno
        presente in più cisterne accumula le letture di tutte. L'operazione
        modifica il numero di righe: ogni lettura viene replicata per ciascun
        vitigno della propria cisterna.

        In assenza di informazioni sulle cisterne (``self.tank_info`` pari a
        ``None``) il metodo solleva ``AttributeError``, poiché opera direttamente
        sul DataFrame delle cisterne.

        :param df: DataFrame delle letture dei sensori.
        :returns: DataFrame unito e arricchito con ``grape_variety_num_readings``.
        """
        # Da una riga per cisterna con lista di vitigni a una riga per singolo vitigno.
        tank_info_per_variety = self.tank_info.explode("grape_variety")
        # Ogni lettura viene abbinata a tutti i vitigni della propria cisterna.
        readings_per_variety = df.join(tank_info_per_variety, on="tank_id", how="inner")
        # Conteggio delle letture per vitigno, riportato su ogni riga del gruppo.
        return readings_per_variety.with_columns(pl.len().over("grape_variety").alias("grape_variety_num_readings"))

    def add_temperature_deviation(self, df: pl.DataFrame) -> pl.DataFrame:
        """Aggiunge la deviazione di temperatura rispetto al valore standard.

        Calcola sempre ``temperature_deviation`` come scarto assoluto della
        temperatura dalla costante ``STANDARD_TEMPERATURE``. Quando la colonna
        ``quantity_liters`` è presente, aggiunge anche ``temperature_deviation_scaled``,
        pari alla deviazione rapportata a 1000 litri (``deviazione * 1000 / quantity_liters``).
        I valori mancanti di ``quantity_liters`` propagano il null nella colonna scalata.
        In assenza della colonna, produce la sola deviazione grezza.

        :param df: DataFrame delle letture dei sensori.
        :returns: DataFrame con ``temperature_deviation`` ed, eventualmente,
            ``temperature_deviation_scaled``.
        """
        # Scarto assoluto rispetto alla temperatura di riferimento.
        result = df.with_columns((pl.col("temp") - self.STANDARD_TEMPERATURE).abs().alias("temperature_deviation"))
        # La versione scalata richiede il volume di mosto della singola lettura.
        if "quantity_liters" in df.columns:
            result = result.with_columns(
                (pl.col("temperature_deviation") * 1000 / pl.col("quantity_liters")).alias(
                    "temperature_deviation_scaled"
                )
            )
        return result
