"""Pipeline di orchestrazione degli analizzatori della cantina.

Il modulo definisce :class:`WineryPipeline`, l'orchestratrice che concatena una
sequenza di analizzatori sui dati dei sensori e, opzionalmente, registra i
risultati su Weights & Biases. Ogni analizzatore espone il metodo
``analyze_data`` (contratto stabilito dalla classe base nel modulo delle basi):
la pipeline lo invoca in ordine, passando l'uscita di un analizzatore in
ingresso al successivo.
"""

import polars as pl
import wandb


class WineryPipeline:
    """Concatena analizzatori sui dati dei sensori e ne registra i risultati.

    La pipeline conserva una lista di analizzatori e un nome di progetto. Gli
    analizzatori vengono trattati per duck typing: qualunque oggetto dotato del
    metodo ``analyze_data`` risulta accettato, senza vincolo di ereditarietà
    dalla classe base.

    :param analyzers: sequenza di analizzatori applicati in ordine; ciascuno
        espone ``analyze_data(df) -> df``.
    :param project_name: nome del progetto associato alle registrazioni su
        Weights & Biases.
    """

    def __init__(self, analyzers, project_name: str = "winery-adventures"):
        # Stato della pipeline: gli analizzatori da eseguire e il nome del
        # progetto a cui associare le registrazioni su wandb.
        self.analyzers = analyzers
        self.project_name = project_name

    def run(self, df: pl.DataFrame, log_to_wandb: bool = False) -> pl.DataFrame:
        """Applica in sequenza gli analizzatori e restituisce il DataFrame finale.

        L'uscita di ogni analizzatore diventa l'ingresso del successivo. Una
        catena che non modifica il DataFrame restituisce lo stesso oggetto
        ricevuto in ingresso: l'identità in memoria viene preservata perché il
        metodo non effettua copie.

        :param df: DataFrame Polars di partenza.
        :param log_to_wandb: se ``True`` registra il risultato finale su wandb;
            con ``False`` (default) nessuna interazione con wandb.
        :returns: il DataFrame prodotto dall'ultimo analizzatore della catena.
        """
        # Concatenazione: il risultato parte dal df in ingresso e viene
        # aggiornato a ogni passaggio. L'assenza di copie esplicite garantisce
        # che una catena "neutra" restituisca l'oggetto originale.
        result = df
        for analyzer in self.analyzers:
            result = analyzer.analyze_data(result)

        # Logging opzionale, disattivato per default per non introdurre una
        # dipendenza da wandb nei percorsi che non lo richiedono.
        if log_to_wandb:
            self.log_to_wandb(result)

        return result

    def log_to_wandb(self, df: pl.DataFrame) -> None:
        """Registra su Weights & Biases lo stress di fermentazione per cisterna.

        Inizializza un esperimento associato a ``project_name`` e registra una
        voce per ciascuna cisterna, contenente identificativo e punteggio di
        stress. La riduzione a una voce per cisterna evita registrazioni
        ridondanti quando il punteggio risulta replicato su tutte le righe del
        gruppo.

        :param df: DataFrame contenente almeno le colonne ``tank_id`` e
            ``stress_score``.
        """
        # Avvio dell'esperimento: da questo punto wandb.run risulta attivo.
        wandb.init(project=self.project_name)

        # Riduzione a una riga per cisterna: il punteggio di stress è costante
        # all'interno dello stesso gruppo, quindi le repliche non aggiungono
        # informazione utile al reporting.
        summary = df.select("tank_id", "stress_score").unique(subset="tank_id", maintain_order=True)

        # Registrazione di una voce per cisterna, con la chiave stress_score
        # attesa dagli strumenti di reporting.
        for record in summary.iter_rows(named=True):
            wandb.log({"tank_id": record["tank_id"], "stress_score": record["stress_score"]})

        # Chiusura ordinata dell'esperimento.
        wandb.finish()