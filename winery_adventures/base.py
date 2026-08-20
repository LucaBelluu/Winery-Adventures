"""Classe base astratta degli analizzatori della pipeline.

Definisce il contratto comune a trasformazioni e calcoli HPC: ricevere un
DataFrame Polars e restituirne uno elaborato.
"""

from abc import ABC, abstractmethod

import polars as pl


class BaseWineryAnalyzer(ABC):
    """Analizzatore astratto: non istanziabile finché ``analyze_data`` non è implementato."""

    @abstractmethod
    def analyze_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """Elabora il DataFrame di ingresso e restituisce quello risultante."""
