"""Trasformazioni sui dati dei sensori delle cisterne."""

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


class WineryTransformer(BaseWineryAnalyzer):
    """Sottoclasse concreta dedicata alle trasformazioni dei dati dei sensori."""

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        return df