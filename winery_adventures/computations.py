"""Calcoli ad alte prestazioni sui dati dei sensori delle cisterne."""

import polars as pl

from winery_adventures.base import BaseWineryAnalyzer


class WineryHPCComputations(BaseWineryAnalyzer):
    """Sottoclasse concreta dedicata ai calcoli ad alte prestazioni."""

    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        return df