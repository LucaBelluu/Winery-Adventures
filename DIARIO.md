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