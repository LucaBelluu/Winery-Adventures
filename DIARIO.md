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