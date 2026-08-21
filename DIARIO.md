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

### 14-08-2026 — Fase 2: Classe base astratta e stub degli analizzatori

**Attività**
- Implementato `winery_adventures/base.py` con la classe astratta `BaseWineryAnalyzer` (ereditarietà da `ABC`, unico metodo astratto `analyze_data`).
- Aggiunti gli stub minimi `winery_adventures/transformations.py` (`WineryTransformer`) e `winery_adventures/computations.py` (`WineryHPCComputations`), sottoclassi concrete con `analyze_data` che restituisce il DataFrame invariato, necessari a chiudere la catena di import di `test_base.py` e a soddisfare la verifica di ereditarietà.

**Decisioni**
- Ereditarietà da `ABC` preferita alla forma `metaclass=ABCMeta`, equivalente ma più verbosa.
- Corpo del metodo astratto ridotto alla sola docstring: `@abstractmethod` impedisce già l'istanziazione, pertanto `raise NotImplementedError` risulterebbe ridondante.
- Docstring in stile reStructuredText per compatibilità con Sphinx, mantenute all'essenziale (intestazione breve di modulo, una riga per classe e metodo).
- Stub introdotti come impalcatura minima in coerenza con l'approccio test-driven, con `analyze_data` identità sufficiente alla verifica di ereditarietà.

**Verifica**
- `test_base.py` verde: 3 test superati (`test_base_class_is_abstract`, `test_base_class_abstract_method`, `test_subclasses`).

**File toccati**
- Aggiunta di `winery_adventures/base.py`, `winery_adventures/transformations.py`, `winery_adventures/computations.py`. Aggiornamento di `DIARIO.md`.

### 14-08-2026 — Fase 2: Configurazione di formatter e linter

**Attività**
- Aggiunto `pyproject.toml` nella radice della repository con la configurazione di Ruff come formatter e linter.
- Impostati `line-length = 120` e `target-version = "py310"` (versione minima richiesta dalla consegna).
- Attivati gli insiemi di regole `E`, `W` (stile PEP 8), `F` (errori e import inutilizzati), `I` (ordinamento import), `UP` (ammodernamento), `B` (insidie comuni).

**Decisioni**
- Ruff preferito al combo Black + isort + Flake8: strumento unico per formattazione e analisi statica, con ordinamento degli import incluso, a fronte di una configurazione più semplice.
- Configurazione raccolta in `pyproject.toml`, file standard di progetto letto da Ruff senza opzioni aggiuntive.

**Verifica**
- `ruff check winery_adventures/` senza segnalazioni; `ruff format --check winery_adventures/` conferma i file già formattati.

**File toccati**
- Aggiunta di `pyproject.toml`. Aggiornamento di `DIARIO.md`.

### 17-08-2026 — Fase 3: Pipeline di orchestrazione

**Attività**
- Implementato `winery_adventures/pipeline.py` con la classe `WineryPipeline`: costruttore `(analyzers, project_name="winery-adventures")`, metodo `run(df, log_to_wandb=False)` e metodo `log_to_wandb(df)`.
- `run` concatena gli analizzatori applicando `analyze_data` in sequenza e restituisce il DataFrame finale, senza copie: una catena che non modifica i dati restituisce l'oggetto originale (identità preservata, verificata da `test_null_analyzers_run` tramite `is`).
- `log_to_wandb` inizializza l'esperimento con `wandb.init(project=...)`, registra una voce per cisterna con chiave `stress_score` e chiude con `wandb.finish()`.

**Decisioni**
- Analizzatori gestiti per duck typing, senza controllo di tipo né vincolo di ereditarietà dalla base: `run` richiede soltanto la presenza del metodo `analyze_data`, coerentemente con la `MockAnalyzer` del test che non eredita dalla base.
- Logging su wandb ridotto a una voce per cisterna tramite `unique(subset="tank_id")`, anziché riga per riga. Il punteggio di stress è costante all'interno del gruppo, quindi le repliche risultano ridondanti; la riduzione contiene il numero di chiamate a `wandb.log` sui dataset di grandi dimensioni. Scartate le alternative del logging per riga (ridondante e oneroso) e del solo aggregato medio (privo del dettaglio per cisterna).
- Blocco del logging dietro il flag `log_to_wandb`, con default `False`, per evitare dipendenze da wandb nei percorsi che non lo richiedono.

**Verifica**
- `test_pipeline.py`: superati `test_null_analyzers_run` e `test_log_wandb`, dipendenti unicamente dalla pipeline. `test_analyzers_run` e `test_pipeline_chain` risultano rossi perché richiedono le colonne `avg_pH_per_tank` e `stress_score`, prodotte dagli analizzatori concreti (trasformazioni e calcoli HPC).
- `ruff check` e `ruff format --check` su `winery_adventures/pipeline.py` senza segnalazioni.

**File toccati**
- Aggiunta di `winery_adventures/pipeline.py`. Aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 3: Sistemazioni di configurazione e versionamento

**Attività**
- Aggiunta della regola `.DS_Store` al `.gitignore` per escludere i file generati da macOS in ogni sottocartella.
- Correzione del nome del file di configurazione di Ruff da `Pyproject.toml` a `pyproject.toml` (minuscolo) e sua aggiunta al versionamento: il file, previsto in fase di configurazione di Ruff, non risultava tracciato.

**Decisioni**
- Nome del file di progetto mantenuto in minuscolo (`pyproject.toml`), forma standard cercata dagli strumenti Python e necessaria su filesystem case-sensitive come quelli della futura integrazione continua.

**File toccati**
- Modifica di `.gitignore`. Aggiunta di `pyproject.toml`.

### 19-08-2026 — Fase 3: Sistemazioni di configurazione e versionamento

**Attività**
- Aggiunta della regola `.DS_Store` al `.gitignore` per escludere i file generati da macOS in ogni sottocartella.
- Correzione del nome del file di configurazione di Ruff da `Pyproject.toml` a `pyproject.toml` (minuscolo) e sua aggiunta al versionamento: il file, previsto in fase di configurazione di Ruff, non risultava tracciato.

**Decisioni**
- Nome del file di progetto mantenuto in minuscolo (`pyproject.toml`), forma standard cercata dagli strumenti Python e necessaria su filesystem case-sensitive come quelli della futura integrazione continua.

**File toccati**
- Modifica di `.gitignore`. Aggiunta di `pyproject.toml`.

### 19-08-2026 — Fase 3: Caricamento dei dati da file TSV

**Attività**
- Implementato `winery_adventures/data_loading.py` con due funzioni: `load_sensor_data` legge le letture dei sensori da TSV; `load_tank_info` legge le informazioni sulle cisterne da TSV e suddivide la colonna `grape_variety` da stringa separata da virgole a lista di stringhe.

**Decisioni**
- Funzioni separate per i due file sorgente, in ragione del diverso trattamento: le letture dei sensori vengono restituite invariate, mentre le informazioni sulle cisterne richiedono la suddivisione dei vitigni.
- Suddivisione della stringa dei vitigni collocata nel caricamento e non nelle trasformazioni, poiché attiene al formato del dato in ingresso e non all'analisi: la trasformazione riceve il dato già nella forma attesa, coerente con le fixture dei test.
- Modulo di caricamento distinto da pipeline e trasformazioni, in applicazione del principio di singola responsabilità per modulo.

**Verifica**
- Caricamento verificato sui file di esempio `sensors_sample.tsv` e `tank_info_sample.tsv`: la colonna `grape_variety` risulta di tipo lista dopo la suddivisione.
- `ruff check` e `ruff format --check` su `winery_adventures/data_loading.py` senza segnalazioni.

**File toccati**
- Aggiunta di `winery_adventures/data_loading.py`. Aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 4: Trasformazioni dei dati dei sensori

**Attività**
- Implementata la classe `WineryTransformer` in `winery_adventures/transformations.py`, sostituendo lo stub identità. Aggiunti: costruttore `WineryTransformer(tank_info=None)` che conserva le informazioni sulle cisterne, costante di classe `STANDARD_TEMPERATURE = 26.0`, le quattro trasformazioni e il metodo `analyze_data` di concatenazione.
- `add_avg_ph_per_tank`: media del pH per cisterna tramite finestra `mean().over("tank_id")`, riportata su ogni riga → `avg_pH_per_tank`.
- `add_num_readings_per_tank`: conteggio delle letture per cisterna tramite finestra `pl.len().over("tank_id")` → `tank_num_readings`.
- `add_num_readings_per_grape_variety`: esplosione della lista dei vitigni (`explode`), unione alle letture su `tank_id` (`join` interno), conteggio per vitigno tramite finestra `pl.len().over("grape_variety")` → `grape_variety_num_readings`. Modifica il numero di righe. Con `tank_info` pari a `None` solleva `AttributeError`, operando direttamente sul DataFrame delle cisterne.
- `add_temperature_deviation`: scarto assoluto dalla temperatura standard → `temperature_deviation`; in presenza di `quantity_liters` aggiunge `temperature_deviation_scaled = deviazione * 1000 / quantity_liters` con propagazione dei null; in assenza della colonna omette la versione scalata.
- `analyze_data`: applica in sequenza media del pH, conteggio letture e deviazione di temperatura (trasformazioni che preservano la grana), e per ultima, solo con `tank_info` presente, la trasformazione per vitigno che esplode le righe.

**Decisioni**
- Finestra `.over()` preferita a `group_by().agg()` seguito da join: la statistica per cisterna viene affiancata a ogni lettura in un solo passaggio, senza ridurre e poi riunire le righe.
- Ordine di concatenazione in `analyze_data` con la trasformazione per vitigno in coda, per non gonfiare i conteggi per cisterna con le righe duplicate dall'esplosione ed evitare `AttributeError` quando `tank_info` manca. Controllo esplicito su `tank_info is not None` anziché cattura dell'eccezione, per esplicitare l'intenzione.
- Colonna grezza `temperature_deviation` mantenuta accanto a `temperature_deviation_scaled` nel ramo con quantità: utile all'analisi e non in conflitto con i test.
- Errore su `tank_info` assente lasciato propagare naturalmente in `add_num_readings_per_grape_variety`, in quanto comportamento atteso dai test.

**Verifica**
- `tests/unit/test_transformations.py`: 6 test superati. Verificata l'uguaglianza esatta dei float per `avg_pH_per_tank` (il test usa il confronto stretto). Confermato che `analyze_data` con `tank_info` produce 9 righe e le quattro colonne attese, e che con `tank_info=None` non esplode e produce `avg_pH_per_tank`.
- `ruff check` e `ruff format --check` su `winery_adventures/transformations.py` senza segnalazioni.

**File toccati**
- Modifica di `winery_adventures/transformations.py`. Aggiornamento di `DIARIO.md`.

**Elementi in sospeso**
- I test `test_pipeline_chain` e `test_analyzers_run` restano rossi finché i calcoli HPC non producono `stress_score` (Fase 5): la Fase 4 fornisce la sola colonna `avg_pH_per_tank`.
- `DeprecationWarning` di Polars 2.0 sul parametro `empty_as_null` di `str.split`, originato dalla suddivisione dei vitigni nel modulo di caricamento (`data_loading.py`): valutare l'impostazione esplicita del parametro in quel modulo.
- Dichiarazione del marcatore `slow` di pytest nella configurazione, da affrontare ai test di accettazione.

### 19-08-2026 — Fase 5: Formula di stress, calcoli HPC e punto d'ingresso

**Attività**
- Aggiunta in `winery_adventures/computations.py` della funzione libera `pairwise_stress_function`, compilata con Numba (`@njit`): doppio ciclo pieno O(n²) da 0 a n−1, somma dei contributi di deviazione di pH, deviazione di temperatura (pesata due volte) e fattore inverso al volume, normalizzata su `n²`. Restituisce `0.0` per array vuoti; sui dati di prova restituisce 2.2.
- Aggiunta della classe `WineryHPCComputations` con `analyze_data`: partizione delle letture per `tank_id`, calcolo dello stress su ciascun gruppo e inserimento della colonna `stress_score`, costante nel gruppo e riportata su ogni riga tramite `replace_strict`.
- Parallelizzazione del calcolo per cisterna con Joblib (`Parallel`/`delayed`), backend a thread, con accumulo degli esiti in una lista condivisa per effetto collaterale.
- Aggiunta di `winery_adventures/main.py` con `run_full_pipeline`: caricamento dei due TSV, costruzione di `WineryHPCComputations` e `WineryTransformer`, orchestrazione in `WineryPipeline`, esecuzione con registrazione su wandb e scrittura del DataFrame finale su file.
- Dichiarazione del marcatore `slow` di pytest nella sezione `[tool.pytest.ini_options]` di `pyproject.toml`.

**Decisioni**
- Formula implementata nella forma piena e fedele al README, non nella variante che sfrutta la simmetria dei contributi. La compilazione `@njit` soddisfa il requisito di ottimizzazione della fase; la riduzione basata sulla simmetria, che dimezza il lavoro mantenendo la complessità O(n²), è rimandata alla profilazione della Fase 6.
- Esclusione delle rilevazioni prive di `quantity_liters` dal calcolo dello stress all'interno del gruppo, poiché un volume ignoto non alimenta un fattore che divide per il volume. La funzione compilata resta puramente numerica; la gestione dei nulli è delegata al livello di orchestrazione in Polars.
- Ordine degli analizzatori in `run_full_pipeline`: calcoli HPC prima delle trasformazioni. L'esplosione dei vitigni duplica le righe; anticipare il calcolo dello stress garantisce la valutazione sulle letture effettive. Lo `stress_score`, costante per cisterna, è replicato senza alterazione dalla successiva esplosione.
- Parallelizzazione con backend a thread e accumulo per effetto collaterale, in luogo della raccolta del valore di ritorno di `Parallel`: il backend a thread condivide la memoria del processo, quindi l'accodamento resta visibile al termine.
- Calcolo dello stress collocato in `WineryHPCComputations.analyze_data`, unico punto responsabile sia della logica sia della sua parallelizzazione, in coerenza con la responsabilità singola del modulo.

**Verifica**
- Suite completa verde: 17 test superati, inclusi `tests/unit/test_computations.py`, i due test di pipeline in precedenza rossi (`test_pipeline_chain`, `test_analyzers_run`) e `tests/acceptance/test_winery_acceptance.py` (9 righe finali, colonne `avg_pH_per_tank` e `stress_score`, chiamate a `Parallel`/`delayed`, registrazione su wandb).
- Marcatore `slow` riconosciuto: `-m slow` seleziona la sola accettazione, `-m "not slow"` la esclude, nessun avviso di marcatore sconosciuto.
- `ruff check` e `ruff format --check` su `computations.py` e `main.py` senza segnalazioni.
- Verifica end-to-end sui campioni `sensors_sample.tsv` e `tank_info_sample.tsv`: 300 righe finali, valori di `stress_score` distinti e coerenti per cisterna.

**File toccati**
- Aggiunta di `winery_adventures/computations.py` e `winery_adventures/main.py`; modifica di `pyproject.toml` (marcatore `slow`); aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 6: Generazione del dataset grande e correzione di riproducibilità

**Attività**
- Esecuzione di `data_generator.py` per il dataset di dimensioni maggiori: 100 cisterne e 100.000 letture dei sensori, scritte in `data/full_sensors.tsv` e `data/full_tank_info.tsv`.
- Individuazione di una dipendenza mancante: `data_generator.py` importa `tqdm` (barra di avanzamento della generazione), pacchetto assente da `requirements.txt`. La ricostruzione dell'ambiente dal solo `requirements.txt`, seguita dall'esecuzione del generatore, terminava con `ModuleNotFoundError: No module named 'tqdm'`.
- Aggiunta di `tqdm==4.70.0` a `requirements.txt`, nella posizione alfabetica coerente con l'ordine esistente.
- Aggiunta al `.gitignore` dell'esclusione dei dataset generati di grandi dimensioni (`data/full_*.tsv`), artefatti derivati e rigenerabili tramite lo script.

**Caratteristiche del dataset generato**
- Letture dei sensori: 100.000 righe, colonne `tank_id`, `time`, `pH`, `temp`, `quantity_liters`. Valori mancanti in `quantity_liters` pari a circa il 10% delle righe.
- Distribuzione per cisterna: 100 cisterne distinte, tra circa 900 e circa 1100 letture ciascuna. Informazioni sulle cisterne: 100 righe, tre vitigni per cisterna.
- Rilievo per la profilazione: la formula di stress è O(n²) per singola cisterna; con circa mille letture per cisterna il costo per cisterna è dell'ordine del milione di contributi, per un totale dell'ordine di cento milioni sull'intero dataset.

**Decisioni**
- Dipendenza `tqdm` dichiarata in `requirements.txt` anziché rimossa da `data_generator.py`: lo script è impalcatura fornita con il progetto e la correzione meno invasiva consiste nel dichiarare la dipendenza, non nel modificare il file.
- Dataset di grandi dimensioni escluso dal versionamento: file derivato, rigenerabile dallo script, di dimensione non trascurabile. I dataset di esempio restano versionati per lo sviluppo rapido.

**File toccati**
- Modifica di `requirements.txt` e `.gitignore`. Aggiornamento di `DIARIO.md`. Generazione locale (non versionata) di `data/full_sensors.tsv` e `data/full_tank_info.tsv`.

### 19-08-2026 — Fase 6: Ottimizzazione della formula di stress per simmetria dei contributi

**Attività**
- Sostituzione del ciclo pieno O(n²) di `pairwise_stress_function` con l'accumulo sul solo triangolo superiore `i < j`, seguito dal raddoppio del totale. Fondamento: il contributo della coppia `(i, j)` coincide con quello di `(j, i)` — differenze in valore assoluto e somma dei fattori di volume simmetriche — e la diagonale è nulla; la somma piena sulle n² coppie equivale al doppio della somma sul triangolo superiore. Le coppie valutate scendono a circa la metà, la complessità resta O(n²), la normalizzazione su `n * n` è invariata.
- Aggiornamento della docstring e del commento interno della funzione, allineati alla nuova logica.
- Aggiunta di `profiling/benchmark_stress.py`: confronto riproducibile tra la funzione di produzione e un'implementazione di riferimento a ciclo pieno, definita nel solo script, su correttezza e tempo. Lo script si esegue dalla radice della repository come modulo (`python -m profiling.benchmark_stress`), affinché il pacchetto `winery_adventures` risulti importabile.

**Verifica**
- Correttezza sul dataset da 100.000 letture: differenza massima tra ciclo pieno e variante ottimizzata dell'ordine di 10⁻¹³ su tutte le 100 cisterne, entro la tolleranza `1e-7` dei test.
- Tempo sulla macchina di riferimento (macOS, Apple Silicon): sulla cisterna con più letture la variante risulta circa 1.9 volte più veloce del ciclo pieno (0.32 ms contro 0.61 ms); l'intera `analyze_data` sul dataset completo richiede circa 34 ms. Il fattore di accelerazione della sola funzione dipende dalla macchina — circa 1.4x in un ambiente Linux di verifica, circa 1.9x sulla macchina di riferimento — per effetto delle diverse ottimizzazioni di compilatore e architettura.
- Suite completa dei test verde con la funzione ottimizzata: il valore 2.2 e la natura di Dispatcher Numba della funzione restano invariati.

**Decisioni**
- Guadagno reale inferiore al dimezzamento teorico: il ciclo pieno è regolare e ben ottimizzato da compilatore e CPU, mentre il ciclo sul triangolo superiore compie meno iterazioni ma con efficienza per iterazione inferiore. La riduzione del lavoro algoritmico non si traduce in un dimezzamento del tempo a parete.
- Implementazione di riferimento a ciclo pieno collocata nel solo script di benchmark e non in produzione, per mantenere un'unica funzione di stress nel modulo e disporre al contempo del termine di paragone per il report.
- Codice di profilazione separato dal pacchetto sorgente in una cartella `profiling/` dedicata, in quanto strumento di analisi e non componente di produzione.

**File toccati**
- Modifica di `winery_adventures/computations.py`. Aggiunta di `profiling/benchmark_stress.py`. Aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 6: Configurazione del percorso di import per l'esecuzione dei test

**Attività**
- Aggiunta di `pythonpath = ["."]` alla sezione `[tool.pytest.ini_options]` di `pyproject.toml`, che pone la radice della repository sul percorso di ricerca dei moduli durante l'esecuzione dei test.

**Motivazione**
- Il comando `pytest` diretto non aggiunge la cartella corrente al percorso di ricerca dei moduli, a differenza di `python -m pytest`. Con le cartelle dei test prive di file `__init__.py` che le colleghino alla radice, il comando diretto non individuava il pacchetto `winery_adventures` e interrompeva la raccolta con `ModuleNotFoundError`. L'impostazione esplicita di `pythonpath` rende la suite eseguibile con il comando diretto, condizione necessaria anche alla futura integrazione continua.

**Verifica**
- Il comando `pytest`, senza variabili d'ambiente aggiuntive, individua il pacchetto, raccoglie tutti i moduli di test e li supera.

**Decisioni**
- Configurazione esplicita in `pyproject.toml` preferita all'aggiunta di file `__init__.py` nelle cartelle dei test o alla dipendenza dal comando `python -m pytest`: soluzione unica, dichiarata nel file di configurazione, indipendente dal modo di invocazione e adatta all'integrazione continua.

**File toccati**
- Modifica di `pyproject.toml`. Aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 6: Analisi thread contro processi per la parallelizzazione

**Attività**
- Analisi del backend di parallelizzazione di `WineryHPCComputations.analyze_data`, che distribuisce il calcolo dello stress per cisterna con Joblib.
- Aggiunta di `profiling/benchmark_parallel.py`: misura riproducibile dell'esecuzione seriale, a thread (con e senza `nogil`) e a processi, sul dataset di grandi dimensioni, con controllo di coerenza dei risultati tra le strategie.
- Allineamento della formattazione di `profiling/benchmark_stress.py` a `ruff format` con line-length 120: interruzioni di riga manuali sostituite dalla formattazione canonica.

**Constatazioni**
- Il finto `Parallel` del banco di prova (`monkey_joblib` in `conftest.py`) esegue i task ma restituisce `None`: la raccolta dei risultati avviene per il solo effetto collaterale delle chiamate. Il codice di produzione deve quindi accumulare in una struttura condivisa, non affidarsi al valore restituito da `Parallel`.
- L'accumulo per effetto collaterale in una lista condivisa produce risultati corretti solo con il backend a thread, che condivide la memoria del processo. Con il backend a processi la lista del processo padre resta vuota (verifica diretta: 100 risultati su 100 con i thread, 0 su 100 con i processi), poiché ogni processo dispone di una propria memoria.
- Il flag `nogil` rende effettivo il parallelismo dei thread sul calcolo compilato: in sua assenza il GIL serializza l'esecuzione della funzione anche tra thread distinti.

**Misure sulla macchina di riferimento (macOS, Apple Silicon, 10 core; dataset da 100.000 letture, 100 cisterne)**
- Tempi di `analyze_data` per strategia: seriale 41.9 ms (riferimento); thread con `nogil` 13.2 ms, accelerazione 3.17x; thread senza `nogil` 40.5 ms, accelerazione 1.03x, in pratica pari al seriale; processi (loky) 18.5 ms, accelerazione 2.26x.
- Il confronto tra thread con e senza `nogil` isola il contributo del flag: senza il rilascio del GIL i thread non accelerano il calcolo compilato. I processi accelerano rispetto al seriale ma restano sotto i thread, per il costo di avvio e di serializzazione dei dati. L'accelerazione dei thread, pari a circa 3x su 10 core anziché prossima a 10x, riflette la frazione di lavoro non parallelizzabile (preparazione dei dati e composizione del risultato) e il costo di distribuzione dei task, secondo la legge di Amdahl.

**Decisioni**
- Backend a thread confermato per `analyze_data`, come già in essere. La scelta non è arbitraria: è l'unica coerente con lo schema di accumulo imposto dal banco di prova e con la correttezza a runtime, ed è anche la più veloce sulla macchina di riferimento. Il backend a processi, oltre a non condividere la lista dei risultati, aggiunge il costo di avvio e di serializzazione dei dati, non giustificato per compiti numerici brevi e indipendenti.

**File toccati**
- Aggiunta di `profiling/benchmark_parallel.py`. Modifica di `profiling/benchmark_stress.py` (formattazione). Aggiornamento di `DIARIO.md`.

### 19-08-2026 — Fase 6: Installazione e fissaggio di Ruff, formattazione del sorgente

**Attività**
- Installazione di Ruff nella macchina di riferimento e fissaggio della versione in `requirements.txt` (`ruff==0.16.3`), in precedenza assente.
- Esecuzione di `ruff check --fix` e `ruff format` sul codice sorgente (`winery_adventures/`) e sugli script di profilazione (`profiling/`). Correzione principale: aggiunta dell'a-capo finale mancante ai moduli del pacchetto (regola `W292`), oltre alla formattazione canonica.

**Motivazione**
- Ruff risultava configurato in `pyproject.toml` ma né installato né dichiarato tra le dipendenze: i controlli di stile non erano di fatto eseguibili. Il fissaggio della versione rende la formattazione deterministica e riproducibile, presupposto per l'integrazione continua, dove l'esito dipende dalla versione dello strumento.

**Verifica**
- `ruff check` e `ruff format --check` su `winery_adventures/` e `profiling/` senza segnalazioni. Suite dei test invariata: la formattazione non altera la logica.

**Decisioni**
- Ruff dichiarato in `requirements.txt` accanto agli altri strumenti di sviluppo già presenti (pytest), coerentemente con l'impostazione esistente a file unico di dipendenze.
- Ambito della formattazione limitato al codice proprio (`winery_adventures/`, `profiling/`); i file forniti con il progetto (`tests/`, `data_generator.py`) lasciati invariati. La scelta di includerli e la relativa configurazione di Ruff sono rimandate alla fase di integrazione continua.

**File toccati**
- Modifica di `requirements.txt` e dei moduli in `winery_adventures/` e `profiling/` (a-capo finale e formattazione). Aggiornamento di `DIARIO.md`.

### 20-08-2026 — Fase 6: Profilazione della memoria

**Attività**
- Aggiunta di `profiling/benchmark_memory.py`: misura la memoria ausiliaria della formula di stress e il picco di memoria del processo durante `analyze_data`, con due strumenti distinti (`tracemalloc` per le allocazioni lato Python, `resource` per il picco RSS dell'intero processo).

**Constatazioni**
- La formula compilata occupa memoria ausiliaria O(1): accumula uno scalare e non materializza la matrice delle coppie. Sulla cisterna con più letture (n circa 970) il picco lato Python del ciclo è dell'ordine del centinaio di byte, contro i circa 29 MB di una variante vettorizzata equivalente che costruisce matrici n×n (memoria O(n²)). Il ciclo è quindi ottimale non solo nel tempo (compilazione Numba) ma anche nella memoria.
- `tracemalloc` non osserva la memoria nativa di Polars (Arrow/Rust): il picco reale dell'intera `analyze_data` va misurato sul processo (RSS). Il picco RSS dell'intero processo, dataset da 100.000 letture incluso, è dell'ordine di alcune centinaia di MB, dovuti in buona parte a Python, alle librerie, alla compilazione JIT una tantum e alla duplicazione dei dati operata da `partition_by`, non al calcolo O(n²), che non alloca memoria.

**Decisioni**
- Due strumenti mantenuti insieme, ciascuno con il proprio ambito dichiarato: la profilazione lato Python isola il comportamento della formula, il picco RSS del processo fornisce il dato di sistema comprensivo di Polars. Nessuna dipendenza aggiuntiva: `tracemalloc` e `resource` appartengono alla libreria standard.
- L'unità di `ru_maxrss` dipende dalla piattaforma (byte su macOS, kilobyte su Linux): lo script normalizza in base a `sys.platform`.

**File toccati**
- Aggiunta di `profiling/benchmark_memory.py`. Aggiornamento di `DIARIO.md`.

### 20-08-2026 — Fase 6: Registrazione su Weights & Biases in modalità offline

**Attività**
- Impostazione della modalità offline come default in `WineryPipeline.log_to_wandb`: `wandb.init` riceve `mode=os.getenv("WANDB_MODE", "offline")`. La registrazione resta locale nella cartella `wandb/` e non richiede account né autenticazione. La variabile d'ambiente `WANDB_MODE` consente di forzare un'altra modalità, ad esempio `online`, senza modificare il codice.

**Motivazione**
- La modalità predefinita di wandb è online e, in assenza di autenticazione, interrompe l'esecuzione con una richiesta di login. L'offline come default rende la pipeline eseguibile da chiunque senza configurazione, coerentemente con il requisito di riproducibilità. Le run offline restano sincronizzabili in seguito con `wandb sync`, qualora serva una dashboard online per la presentazione.

**Verifica**
- Registrazione offline eseguita attraverso `WineryPipeline.log_to_wandb` su dati reali: creazione della run locale in `wandb/offline-run-...` e registrazione di una voce di `stress_score` per cisterna, senza login. La cartella `wandb/` è già esclusa dal versionamento.
- `test_log_wandb` verde: il finto `wandb.init` del banco di prova ignora il nuovo parametro. Suite completa da riconfermare sulla macchina di riferimento, dove sono presenti tutti i moduli sorgente.
- `ruff check` e `ruff format --check` su `pipeline.py` senza segnalazioni.

**Decisioni**
- Modalità offline scelta come default per la riproducibilità, con override tramite `WANDB_MODE` per non precludere la modalità online. Scartata l'alternativa di codificare rigidamente l'offline, che avrebbe richiesto una modifica al codice per passare all'online.

**File toccati**
- Modifica di `winery_adventures/pipeline.py`. Aggiornamento di `DIARIO.md`.

### 20-08-2026 — Fase 6: Report di performance

**Attività**
- Stesura di `docs/performance.md`, report che raccoglie le misure di tempo, parallelizzazione e memoria della macchina di riferimento, con la metodologia e i comandi di riproduzione tramite gli script di `profiling/`.

**Contenuto**
- Ambiente e dataset di riferimento. Ottimizzazione algoritmica della formula: ciclo pieno 0,607 ms contro triangolo superiore 0,415 ms sulla cisterna con 991 letture (1,46x), risultato invariato entro 1e-7. Flag di compilazione Numba e loro effetto. Parallelizzazione su 10 core: seriale 42,2 ms, thread con `nogil` 12,0 ms (3,53x), thread senza `nogil` 41,9 ms (1,01x), processi 17,9 ms (2,36x). Memoria della formula: ciclo O(1) 0,1 KB contro variante vettorizzata O(n²) 29,97 MB; picco RSS del processo circa 230 MB. Registrazione offline su wandb.

**Decisioni**
- Report collocato in `docs/`, cartella convenzionale della documentazione e compatibile con Sphinx (Fase 8); formato Markdown per leggibilità e versionabilità. La cartella `docs/_build/` è già esclusa dal versionamento, il sorgente del report resta tracciato.
- Conclusione documentata: la configurazione di produzione (triangolo superiore, `@njit(fastmath, nogil, cache)`, parallelizzazione a thread) è ottimale nel tempo e nella memoria, e il backend a thread è l'unico coerente con lo schema di raccolta dei risultati imposto dal banco di prova.

**File toccati**
- Aggiunta di `docs/performance.md`. Aggiornamento di `DIARIO.md`.

## 21-08-2026 — Fase 7: diagrammi UML
Adozione di PlantUML come strumento per i diagrammi UML, con sorgenti testuali in `docs/uml/`. Motivazione: PlantUML copre nativamente e con notazione UML corretta tutti e tre i diagrammi richiesti, casi d'uso compresi; resta testuale e versionabile su Git e si integra con Sphinx, già adottato per la documentazione. Realizzazione del diagramma delle classi, fedele all'implementazione: classe base astratta `BaseWineryAnalyzer`, sottoclassi concrete `WineryTransformer` e `WineryHPCComputations`, orchestratrice `WineryPipeline` legata agli analizzatori per aggregazione (duck typing sul metodo `analyze_data`), funzione libera `pairwise_stress_function` con stereotipo di funzione compilata, moduli procedurali `data_loading` e `main`. Sorgente e PNG generati in `docs/uml/`. File toccati: `docs/uml/class_diagram.puml`, `docs/uml/class_diagram.png`. In sospeso: diagramma di sequenza, diagramma dei casi d'uso.

## 21-08-2026 — Fase 7: diagramma di sequenza
Realizzazione del diagramma di sequenza, fedele al flusso di `run_full_pipeline`. Il diagramma traccia, nell'ordine temporale, il caricamento dei due file TSV tramite `data_loading`, l'avvio di `WineryPipeline.run`, l'applicazione in sequenza dei due analizzatori — prima `WineryHPCComputations` (con esecuzione parallela per cisterna via Joblib, passaggio da `_stress_for_group` alla funzione libera `pairwise_stress_function`), poi `WineryTransformer` (quattro trasformazioni, l'ultima per vitigno subordinata alla presenza di `tank_info`) — la registrazione opzionale su Weights & Biases e la scrittura del risultato su file. I due rami condizionali del codice sono resi con frammenti `opt`, le ripetizioni con frammenti `loop`. File toccati: `docs/uml/sequence_diagram.puml`, `docs/uml/sequence_diagram.png`. In sospeso: diagramma dei casi d'uso.

## 21-08-2026 — Fase 7: diagramma dei casi d'uso e chiusura fase
Realizzazione del diagramma dei casi d'uso: attore primario `Operatore di cantina` collegato all'obiettivo "Analizzare i dati di fermentazione", quattro passi in relazione `«include»` (caricamento, calcolo dello stress, arricchimento statistico, esportazione su file), registrazione su Weights & Biases in relazione `«extend»` in quanto subordinata al flag `log_to_wandb`, con l'attore-sistema esterno `Weights & Biases`. Completati i tre diagrammi UML richiesti (classi, sequenza, casi d'uso), tutti fedeli all'implementazione e generati con PlantUML in `docs/uml/`. File toccati: `docs/uml/use_case_diagram.puml`, `docs/uml/use_case_diagram.png`. Fase 7 conclusa. In sospeso per la Fase 8: documentare in README il comando di rigenerazione delle immagini dai sorgenti `.puml`.

## 21-08-2026 — Fase 8 (Documentazione): configurazione di Sphinx
Configurazione della generazione automatica della documentazione API con Sphinx 9.1.0. Aggiunta di `sphinx` a `requirements.txt` con versione fissata, per riproducibilità e coerenza con la CI. Creazione di `docs/conf.py`: percorso di importazione verso la radice del progetto (necessario perché autodoc importa i moduli per estrarne le docstring), estensioni `sphinx.ext.autodoc` e `sphinx.ext.viewcode`, impostazione di lingua, tema e copyright del piè di pagina. Esclusione deliberata dell'estensione `napoleon`, superflua in presenza di docstring già redatte in reStructuredText nativo. Creazione della pagina indice `docs/index.rst`. Generazione delle pagine dei moduli tramite `sphinx-apidoc` (`docs/modules.rst`, `docs/winery_adventures.rst`). La generazione dell'HTML tramite `sphinx-build` produce il manuale in `docs/_build/html/` senza avvisi, con docstring estratte comprensive di firme, parametri e valori restituiti. Motivazione della scelta: il requisito di consegna richiede la documentazione tramite docstring con Sphinx, e l'approccio con autodoc evita la duplicazione delle descrizioni tra codice e documentazione. File toccati: requirements.txt, docs/conf.py, docs/index.rst, docs/modules.rst, docs/winery_adventures.rst. In sospeso: eventuale scelta di un tema grafico più ricco e inserimento dei diagrammi UML nella documentazione; stesura del README come secondo troncone della Fase 8.

## 21-08-2026 — Fase 8 (Documentazione): README di progetto e archiviazione della traccia
Riscrittura del README come documentazione portante dell'intero progetto, in sostituzione del testo della traccia originale. Il README è organizzato in capitoli con indice di navigazione e copre: panoramica e obiettivo del sistema, struttura del repository con il ruolo di ogni file, architettura e funzionamento dettagliati di ciascun componente (classe base astratta, caricamento dati, calcolo dello stress con le ottimizzazioni Numba e algoritmica, trasformazioni, orchestrazione e registrazione), requisiti, procedura di installazione con spiegazione di ogni comando, uso della pipeline, formato dei dati, esecuzione dei test, generazione della documentazione Sphinx, performance, diagrammi UML, qualità del codice, licenza e autori. Il livello di dettaglio è intermedio: superiore alla sintesi, inferiore alla documentazione interna dei singoli file, con spiegazione dei termini tecnici per la leggibilità. La traccia originale del docente è spostata in docs/consegna.md, riportata invariata e preceduta da una nota che ne dichiara la natura, come riferimento per la tracciabilità dei requisiti. File toccati: README.md, docs/consegna.md, DIARIO.md. In sospeso: eventuale aggiunta di un entry-point da riga di comando per la pipeline.

### 21-08-2026 — Fase 9: Integrazione continua con GitHub Actions

**Attività**
- Aggiunta del workflow `.github/workflows/ci.yml`. A ogni push e pull request configura Python 3.12 su runner Ubuntu, installa le dipendenze fissate in `requirements.txt`, esegue linter e controllo di formattazione Ruff sul codice sorgente e sugli script di profilazione, ed esegue l'intera suite Pytest (unitari e accettazione).
- Normalizzazione con Ruff di `winery_adventures/pipeline.py` e `profiling/benchmark_memory.py`, non allineati alla formattazione canonica: a-capo finale mancante (regola `W292`) in entrambi e ordinamento degli import (regola `I001`) in `pipeline.py`. Lo scostamento deriva da modifiche successive alla passata di formattazione del 19-08: aggiunta di `benchmark_memory.py` e introduzione dell'import `os` in `pipeline.py` per la modalità wandb offline.

**Verifica (ambiente di riferimento, macOS, Python 3.12)**
- `ruff check` e `ruff format --check` su `winery_adventures/` e `profiling/` senza segnalazioni dopo la normalizzazione. Suite Pytest completa verde: 17 test superati.
- Risoluzione a secco di `requirements.txt` su Linux/Python 3.12: tutte le versioni fissate dispongono di distribuzione per Linux x86_64, inclusi `polars`, `polars-runtime-32`, `numba` e `llvmlite`; l'installazione in CI riproduce l'ambiente di riferimento senza adattamenti. La compatibilità è vincolata a Python 3.12.

**Decisioni**
- Job unico con step in sequenza (installazione, linting, formattazione, test): impianto lineare, adeguato alla dimensione del progetto e agevole da esporre.
- Python 3.12 in CI, coerente con l'ambiente di riferimento e con le dipendenze bloccate; matrice multi-versione non adottata per non entrare in conflitto con le versioni fissate.
- Ambito di Ruff limitato al codice proprio (`winery_adventures/`, `profiling/`), coerente con la Fase 6. I file forniti col progetto (`tests/`, `data_generator.py`) restano non ristilizzati: costituiscono specifiche e vengono validati dall'esecuzione con Pytest.
- Trigger su push e pull request come da obiettivo di fase; l'esito compare in automatico nelle pull request.

**File toccati**
- Aggiunta di `.github/workflows/ci.yml`. Modifica di `winery_adventures/pipeline.py` e `profiling/benchmark_memory.py` (normalizzazione). Aggiornamento di `DIARIO.md`.

### 21-08-2026 — Fase 9: Correzione di una divergenza di linting tra locale e integrazione continua

**Problema**
- La prima esecuzione del workflow è fallita sullo step di linting con la regola `I001` su `winery_adventures/pipeline.py`, pur risultando il controllo verde in locale con la stessa versione di Ruff e la stessa configurazione.

**Causa**
- L'ordinamento degli import di Ruff classifica i moduli in gruppi (libreria standard, terze parti, interni). La classificazione del modulo `wandb` dipende dalla presenza della cartella locale `wandb/`, creata dalle esecuzioni offline e esclusa dal versionamento: in locale la cartella induce la classificazione di `wandb` come modulo interno, con una riga vuota di separazione da `polars`; in integrazione continua, dove la cartella è assente, `wandb` risulta di terze parti e va raggruppato con `polars` senza riga vuota. La divergenza deriva quindi dallo stato locale del filesystem, non dal codice. Riproduzione confermata: con la cartella `wandb/` il controllo passa, senza la cartella segnala `I001`.

**Soluzione**
- Dichiarazione esplicita di `wandb` tra le dipendenze esterne nell'ordinamento degli import, tramite `[tool.ruff.lint.isort] known-third-party = ["wandb"]` in `pyproject.toml`. La classificazione diventa deterministica e indipendente dalle cartelle locali. Riformattazione conseguente di `pipeline.py` con `ruff check --fix`.

**Verifica**
- Con la configurazione aggiornata il file in forma canonica passa il controllo anche in presenza della cartella `wandb/`; `ruff check --fix` produce l'ordinamento canonico. Linting, formattazione e suite Pytest verdi in locale.

**File toccati**
- Modifica di `pyproject.toml` e `winery_adventures/pipeline.py`. Aggiornamento di `DIARIO.md`.

### 21-08-2026 — Fase 9: Badge di stato della CI nel README

**Attività**
- Aggiunta del badge di stato dell'integrazione continua in testa al `README.md`, subito sotto il titolo. Il badge riflette l'esito dell'ultima esecuzione del workflow sul ramo predefinito e rimanda alla scheda Actions della repository.

**Motivazione**
- Il badge comunica a colpo d'occhio, a chiunque apra la repository, lo stato dei controlli automatici, e collega la documentazione all'infrastruttura di integrazione continua.

**File toccati**
- Modifica di `README.md`. Aggiornamento di `DIARIO.md`.