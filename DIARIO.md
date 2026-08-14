# DIARIO DI PROGETTO — Winery Adventures

Memoria condivisa del progetto. Raccoglie in ordine cronologico ogni decisione e ogni passo svolto, con dettaglio sufficiente a ricostruire e ripetere il lavoro. Ogni voce riporta data, fase, attività, motivazione, comandi e file rilevanti, elementi in sospeso.

---

## STORICO

### 14-08-2026 — Fase 0: Setup dell'ambiente, delle dipendenze e della repository

**Ambiente Python**
- Sistema operativo macOS (Apple Silicon). Gestore di ambienti Conda, distribuzione Miniforge.
- Creazione di un ambiente dedicato `winery` su Python 3.12 (predisposto il 13-08-2026): `conda create --name winery python=3.12`, seguito da `conda activate winery`. Versione verificata nell'ambiente: 3.12.13. La consegna richiede Python 3.10+, requisito soddisfatto.

**Repository**
- Fork della repository di riferimento `GiulioCasti/Winery-Adventures` nell'account `LucaBelluu`, con nome invariato (predisposto il 13-08-2026).
- Clonazione in locale da `/Users/lucabellu`: `git clone https://github.com/LucaBelluu/Winery-Adventures.git`.
- Invito alla repository del collega di progetto e del tutor. La repository personale non espone la selezione granulare dei ruoli, pertanto entrambi risultano con permesso di scrittura.

**Dipendenze**
- Installazione delle librerie richieste dalla consegna nell'ambiente `winery` tramite pip: `pip install polars numba wandb joblib pytest`.
- Verifica dell'importazione delle librerie: `python -c "import polars, numba, wandb, joblib, pytest; print('OK dipendenze')"`.
- Registrazione delle versioni esatte in `requirements.txt` tramite `pip freeze`, con fissaggio delle versioni tramite `==` per garantire riproducibilità.
- Normalizzazione della riga relativa al pacchetto `packaging`, generata da `pip freeze` con un percorso locale non portabile, sostituita con `packaging==26.3`. Aggiunta di un'intestazione descrittiva dell'ambiente di riferimento.

**Adeguamento del .gitignore**
- Rimozione delle righe finali ereditate dalla repository di partenza (`pyproject.toml`, `.pre-commit-config.yaml`, `src/`, `winery_adventures/*`). La regola `winery_adventures/*` avrebbe escluso dal versionamento l'intero codice sorgente del progetto.
- Aggiunta dell'esclusione della cartella di log locali `wandb/`.
- Verifica del corretto tracciamento del pacchetto sorgente tramite `git check-ignore winery_adventures/__init__.py`, che non produce output a conferma della non esclusione.

**Struttura di partenza**
- `data/`: dataset di esempio TSV, `sensors_sample.tsv` (letture dei sensori) e `tank_info_sample.tsv` (informazioni sulle cisterne).
- `data_generator.py`: script per la generazione di dataset di dimensioni maggiori.
- `tests/unit/`: test unitari con file corrispondenti ai moduli da sviluppare (`test_base.py`, `test_transformations.py`, `test_pipeline.py`, `test_computations.py`).
- `tests/acceptance/`: test di accettazione dell'intera pipeline (`test_winery_acceptance.py`).
- `tests/conftest.py`: configurazione condivisa dei test.
- `winery_adventures/`: pacchetto del codice sorgente, contenente il solo `__init__.py` privo di contenuto applicativo.

**Decisioni**
- Ambiente dedicato per isolamento delle dipendenze e riproducibilità.
- Python 3.12 per compatibilità con le librerie del progetto, in particolare con la compilazione richiesta da Numba.
- Gestione delle dipendenze tramite pip e `requirements.txt`, in previsione della futura integrazione continua.
- Moduli del codice sorgente introdotti fase per fase, con denominazione allineata ai file di test (ad esempio `base.py` per `test_base.py`).
- Configurazione di formatter e linter e file `pyproject.toml` rimandati all'avvio della scrittura del codice.

**File toccati**
- Aggiunta di `DIARIO.md` e `requirements.txt`. Modifica di `.gitignore`.

**Elementi in sospeso**
- Configurazione di formatter e linter e del file `pyproject.toml`.
- Definizione dei moduli del codice sorgente, rimandata alle fasi di sviluppo.

### 14-08-2026 — Fase 1: Comprensione dei test come specifiche

**Attività**
- Lettura e interpretazione dei file di test come specifiche del progetto (approccio test-driven), senza introduzione di codice di produzione. File esaminati: `tests/unit/test_base.py`, `tests/conftest.py`, `tests/unit/test_transformations.py`, `tests/unit/test_pipeline.py`, `tests/unit/test_computations.py`, `tests/acceptance/test_winery_acceptance.py`.

**Moduli e classi imposti dai test**
- `winery_adventures/base.py`: classe astratta `BaseWineryAnalyzer`.
- `winery_adventures/transformations.py`: `WineryTransformer`, sottoclasse della base.
- `winery_adventures/computations.py`: `WineryHPCComputations` (sottoclasse della base) e funzione libera `pairwise_stress_function`.
- `winery_adventures/pipeline.py`: `WineryPipeline`.
- `winery_adventures/main.py`: funzione d'ingresso `run_full_pipeline`.

**Contratto della classe base**
- `BaseWineryAnalyzer` astratta (ABC), non istanziabile: l'istanziazione diretta solleva `TypeError`.
- Unico metodo astratto `analyze_data(df: pl.DataFrame) -> pl.DataFrame`. Una sottoclasse che non implementa esattamente questo nome resta astratta.
- `WineryTransformer` e `WineryHPCComputations` ereditano dalla base.

**Struttura dei dati (ricavata dalle fixture)**
- Letture dei sensori: colonne `tank_id`, `time` (stringa), `pH`, `temp`, `quantity_liters`. La colonna `quantity_liters` può contenere valori mancanti (null).
- Esiste lo scenario privo di `quantity_liters`, che verifica il ramo di calcolo alternativo.
- Informazioni sulle cisterne: `tank_id`, `capacity_liters`, `grape_variety` (stringa di vitigni separati da virgola, da dividere in lista tramite `str.split(",")`). Uno stesso vitigno può appartenere a più cisterne.
- `capacity_liters` (capacità della cisterna) è concetto distinto da `quantity_liters` (volume di mosto in una singola lettura).

**Requisiti delle trasformazioni**
- Costruttore `WineryTransformer(tank_info=None)`: conserva le informazioni sulle cisterne, con default `None`.
- `analyze_data`: applica in sequenza le trasformazioni e restituisce il DataFrame arricchito con `avg_pH_per_tank`, `tank_num_readings`, `grape_variety_num_readings`, `temperature_deviation_scaled`.
- `add_avg_ph_per_tank`: media del pH per cisterna (finestra su `tank_id`) riportata su ogni riga → `avg_pH_per_tank`.
- `add_num_readings_per_tank`: conteggio delle letture per cisterna (finestra su `tank_id`) riportato su ogni riga → `tank_num_readings`.
- `add_num_readings_per_grape_variety`: esplode i vitigni, unisce le informazioni alle letture tramite `tank_id`, conta le letture per vitigno → `grape_variety_num_readings`. Modifica il numero di righe. Con `tank_info` pari a `None` solleva `AttributeError`.
- `STANDARD_TEMPERATURE = 26.0`: costante di classe.
- `add_temperature_deviation`: deviazione grezza `|temp − STANDARD_TEMPERATURE|` → `temperature_deviation`. In presenza di `quantity_liters` aggiunge `temperature_deviation_scaled = deviazione × 1000 / quantity_liters`, con propagazione dei null. In assenza della colonna produce solo la deviazione grezza e omette la versione scalata.

**Requisiti della pipeline**
- Costruttore `WineryPipeline(analyzers, project_name=<default>)`: riceve una lista di analizzatori (usati per duck typing, senza vincolo di ereditarietà dalla base) e un nome di progetto opzionale, entrambi conservati come stato.
- `run(df, log_to_wandb=False)`: applica in sequenza `analyze_data` di ogni analizzatore e restituisce il DataFrame finale; con catena che non modifica nulla restituisce lo stesso oggetto ricevuto in ingresso. Con `log_to_wandb=True` registra su wandb; con `False` (default) non interagisce con wandb.
- `log_to_wandb(df)`: inizializza l'esperimento con `wandb.init` usando il nome di progetto e registra i dati con `stress_score` come chiave.
- I costruttori di `WineryTransformer` e `WineryHPCComputations` sono chiamabili senza argomenti.

**Requisiti delle computazioni HPC**
- `pairwise_stress_function(pH, temp, quantity)`: riceve tre array NumPy e restituisce un singolo float. Implementa fedelmente l'algoritmo O(n²) del README (doppio ciclo pieno da 0 a n−1, somma divisa per n²). Sui dati di prova restituisce 2.2.
- La funzione deve essere compilata con Numba (decoratore `@njit`); il test la verifica come istanza di `Dispatcher`.
- `WineryHPCComputations.analyze_data`: calcola lo stress per cisterna (raggruppamento su `tank_id`, uso di `pairwise_stress_function`) e aggiunge `stress_score` riportato su ogni riga del gruppo. Costruttore senza argomenti.

**Requisiti del punto d'ingresso e dell'accettazione**
- `run_full_pipeline(input_csv, tank_info_csv, output_csv, project_name)`: carica i due file TSV (separatore tab), divide la stringa dei vitigni in lista, costruisce transformer (con le informazioni sulle cisterne) e computazioni HPC, li inserisce in una `WineryPipeline` con il nome di progetto, esegue `run` con logging wandb attivo e scrive il DataFrame finale su `output_csv`.
- Il caricamento dei dati da TSV è parte del sistema, non coperto dai test unitari.
- Il flusso deve usare Joblib (`Parallel` e `delayed`); candidato naturale il calcolo dello stress per cisterna.
- Il marcatore `slow` va dichiarato nella configurazione di pytest.
- Sui dati delle fixture il risultato finale ha 9 righe (2 letture × 3 vitigni per la cisterna 1, più 1 lettura × 3 vitigni per la cisterna 2), effetto dell'esplosione dei vitigni.

**Decisioni**
- `analyze_data` del transformer applica prima le trasformazioni che preservano la grana dei dati (media del pH, conteggio letture, deviazione di temperatura) e per ultima, soltanto in presenza di `tank_info`, la trasformazione per vitigno che esplode le righe. L'ordine evita di falsare i conteggi per cisterna e impedisce il sollevamento di `AttributeError` quando `tank_info` è `None`. Preferito un controllo esplicito sulla presenza di `tank_info` rispetto alla cattura dell'eccezione con `try/except`, per rendere l'intenzione esplicita e non mascherare errori reali.

**File toccati**
- Aggiornamento di `DIARIO.md` con i requisiti ricavati dai test. Nessun codice di produzione introdotto.

**Elementi in sospeso**
- Gestione dei valori mancanti o nulli in `quantity_liters` nella formula di stress (divisione per la quantità) — Fase 5.
- Calcolo dello stress sulle letture effettive e non sui duplicati generati dall'esplosione dei vitigni nel flusso completo — Fase 5.
- Dichiarazione del marcatore `slow` nella configurazione di pytest.
- Scelta sul mantenimento della colonna `temperature_deviation` grezza accanto a `temperature_deviation_scaled` nel ramo con quantità.
- Ordine definitivo di concatenazione delle trasformazioni in `analyze_data`, da confermare in fase di implementazione (Fase 4).