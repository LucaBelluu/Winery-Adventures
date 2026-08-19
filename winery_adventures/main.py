"""Punto d'ingresso della pipeline completa di Winery Adventures.

Il modulo collega tra loro caricamento dei dati, trasformazioni, calcoli ad alte
prestazioni e registrazione dei risultati. La funzione ``run_full_pipeline``
carica i due file TSV, costruisce gli analizzatori, li orchestra tramite
``WineryPipeline`` e scrive il DataFrame finale su file.
"""

import polars as pl

from winery_adventures.computations import WineryHPCComputations
from winery_adventures.data_loading import load_sensor_data, load_tank_info
from winery_adventures.pipeline import WineryPipeline
from winery_adventures.transformations import WineryTransformer


def run_full_pipeline(
    input_csv: str,
    tank_info_csv: str,
    output_csv: str,
    project_name: str = "winery-adventures",
) -> pl.DataFrame:
    """Esegue l'intera pipeline dai file di ingresso al file di uscita.

    Carica le letture dei sensori e le informazioni sulle cisterne, calcola lo
    stress di fermentazione per cisterna, arricchisce i dati con le
    trasformazioni e registra i risultati su Weights & Biases; il DataFrame
    finale è scritto su ``output_csv``.

    :param input_csv: percorso del file TSV delle letture dei sensori.
    :param tank_info_csv: percorso del file TSV delle informazioni sulle cisterne.
    :param output_csv: percorso del file su cui scrivere il risultato.
    :param project_name: nome del progetto usato per la registrazione su wandb.
    :returns: il DataFrame finale arricchito.
    """
    sensors = load_sensor_data(input_csv)
    tank_info = load_tank_info(tank_info_csv)

    # Ordine degli analizzatori: il calcolo dello stress precede le
    # trasformazioni. L'esplosione dei vitigni, ultima trasformazione, duplica le
    # righe per ogni vitigno; anticipare i calcoli HPC garantisce che lo stress
    # sia valutato sulle letture effettive e non sui duplicati. Lo ``stress_score``
    # è costante per cisterna, quindi la successiva duplicazione lo replica senza
    # alterarne il valore.
    analyzers = [WineryHPCComputations(), WineryTransformer(tank_info)]
    pipeline = WineryPipeline(analyzers, project_name=project_name)

    result = pipeline.run(sensors, log_to_wandb=True)
    result.write_csv(output_csv)
    return result