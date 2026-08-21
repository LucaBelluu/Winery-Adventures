# Winery Adventures

Pipeline in Python per l'analisi dei dati dei sensori delle cisterne di
fermentazione di una cantina. Il sistema legge le letture dei sensori, le
arricchisce con statistiche per cisterna e per vitigno, calcola un indice di
stress di fermentazione e produce un insieme di dati pronto per il reporting.

Progetto sviluppato da Luca Bellu e Michele Sciarra nell'ambito del corso di
Ingegneria del Software.

---

## Indice

- [Panoramica e obiettivo](#panoramica-e-obiettivo)
- [Struttura del repository](#struttura-del-repository)
- [Architettura e funzionamento](#architettura-e-funzionamento)
  - [Il flusso della pipeline](#il-flusso-della-pipeline)
  - [La classe base astratta](#la-classe-base-astratta)
  - [Caricamento dei dati](#caricamento-dei-dati)
  - [Calcolo dello stress di fermentazione](#calcolo-dello-stress-di-fermentazione)
  - [Le trasformazioni](#le-trasformazioni)
  - [Orchestrazione e registrazione](#orchestrazione-e-registrazione)
- [Requisiti](#requisiti)
- [Installazione](#installazione)
- [Uso](#uso)
- [Formato dei dati](#formato-dei-dati)
- [Test](#test)
- [Documentazione](#documentazione)
- [Performance](#performance)
- [Diagrammi UML](#diagrammi-uml)
- [Qualità del codice](#qualità-del-codice)
- [Licenza](#licenza)
- [Autori](#autori)

---

## Panoramica e obiettivo

Una cantina moderna installa sensori nelle cisterne di fermentazione per
misurare nel tempo grandezze come pH, temperatura e volume di mosto. Da queste
misurazioni grezze non è immediato capire quali cisterne stiano fermentando in
modo regolare e quali mostrino segnali di rischio. Winery Adventures affronta
proprio questo problema: trasforma un flusso di letture in indicatori sintetici
e interpretabili, utili a monitorare lo stato della fermentazione.

L'obiettivo del sistema è ricevere due file di dati, le letture dei sensori e
le informazioni sulle cisterne, ed elaborarli lungo una pipeline che aggiunge
statistiche descrittive, calcola un indice di stress per ogni cisterna e salva
il risultato finale, registrandone una sintesi su uno strumento di tracciamento
degli esperimenti.

Il progetto nasce da un vincolo metodologico preciso: le specifiche non sono
fornite come descrizione, ma come una **suite di test** da soddisfare. Ogni
classe e ogni funzione derivano dall'interpretazione di quei test, trattati come
il contratto che il codice deve rispettare. Questo approccio, noto come sviluppo
guidato dai test, garantisce che ogni componente abbia un comportamento
verificabile e documentato dalle prove automatiche.

Le priorità di progettazione sono tre: correttezza rispetto ai test, chiarezza
del codice e delle sue responsabilità, ed efficienza sui grandi volumi di dati,
affrontata con la compilazione in codice macchina della parte di calcolo più
onerosa.

---

## Struttura del repository

L'organizzazione separa nettamente il codice sorgente, i test, i dati, gli
strumenti di misura delle prestazioni e la documentazione. Ogni modulo del
pacchetto ha una singola responsabilità.

```
Winery-Adventures/
├── winery_adventures/       Pacchetto principale con la logica della pipeline
│   ├── base.py              Classe base astratta: contratto comune degli analizzatori
│   ├── data_loading.py      Lettura dei due file TSV di ingresso
│   ├── transformations.py   Statistiche per cisterna e per vitigno
│   ├── computations.py      Indice di stress di fermentazione, ottimizzato con Numba
│   ├── pipeline.py          Orchestrazione degli analizzatori e registrazione dei risultati
│   └── main.py              Punto d'ingresso che collega caricamento, calcolo e scrittura
├── tests/
│   ├── unit/                Test unitari dei singoli componenti
│   ├── acceptance/          Test di accettazione dell'intera pipeline
│   └── conftest.py          Dati e oggetti condivisi tra i test
├── profiling/               Script di misura di tempi, memoria e parallelismo
├── docs/
│   ├── conf.py              Configurazione della documentazione Sphinx
│   ├── index.rst            Pagina indice della documentazione
│   ├── performance.md       Report di profilazione delle prestazioni
│   ├── consegna.md          Specifiche originali del progetto (riferimento)
│   └── uml/                 Diagrammi UML: sorgenti PlantUML e immagini
├── data/                    Dataset di esempio in formato TSV
├── data_generator.py        Generatore di dataset di grandi dimensioni
├── requirements.txt         Dipendenze con versioni fissate
├── pyproject.toml           Configurazione del progetto e degli strumenti
├── README.md
└── LICENSE
```

L'esecuzione della pipeline e la generazione della documentazione producono
cartelle non versionate, `wandb/` per le registrazioni offline, `docs/_build/`
per il sito della documentazione, oltre alle cartelle di cache `__pycache__/`,
escluse dal controllo di versione tramite `.gitignore`.

---

## Architettura e funzionamento

### Il flusso della pipeline

L'elaborazione attraversa quattro fasi concettuali: **caricamento** dei dati dai
file, **trasformazione** in nuove colonne descrittive, **analisi** con il calcolo
dello stress, **reporting** con la scrittura del risultato e la registrazione
della sintesi.

Il cuore del sistema è l'idea di *analizzatore*: un oggetto che riceve una
tabella di dati e ne restituisce una versione elaborata. La pipeline non conosce
i dettagli di ciascun analizzatore, ma li applica in sequenza, passando l'uscita
di uno come ingresso al successivo. Questa uniformità rende il sistema
estensibile: aggiungere una nuova elaborazione significa scrivere un nuovo
analizzatore, senza toccare l'orchestrazione.

Un dettaglio dell'ordine di esecuzione merita attenzione. Il calcolo dello
stress precede le trasformazioni. La ragione è che l'ultima trasformazione, il
conteggio per vitigno, duplica le righe (una copia per ogni vitigno della
cisterna); calcolare lo stress prima di quella duplicazione garantisce che la
formula operi sulle letture reali e non su copie ripetute, che ne falserebbero
il risultato.

I dati sono rappresentati con **Polars**, una libreria di manipolazione di
tabelle simile a Pandas ma progettata per l'alta velocità e per un uso efficiente
della memoria. L'unità di lavoro è il DataFrame, una tabella con righe e colonne.

### La classe base astratta

Il modulo `base.py` definisce `BaseWineryAnalyzer`, una **classe astratta**: una
classe che non può essere istanziata direttamente e che serve a fissare un
contratto per le sue sottoclassi. Il contratto è un unico metodo, `analyze_data`,
che riceve un DataFrame e ne restituisce uno elaborato.

Questa astrazione è il fondamento dell'estensibilità descritta sopra. Sia il
calcolo dello stress sia le trasformazioni sono sottoclassi concrete che
implementano `analyze_data` a modo loro: la pipeline le tratta in modo
intercambiabile, perché tutte rispettano lo stesso contratto. È un'applicazione
diretta del principio di programmazione orientata agli oggetti secondo cui il
codice dipende da un'interfaccia comune e non dalle singole implementazioni.

### Caricamento dei dati

Il modulo `data_loading.py` legge i due file di ingresso, entrambi in formato TSV
(valori separati da tabulazione). La funzione `load_sensor_data` carica le
letture dei sensori; `load_tank_info` carica le informazioni sulle cisterne e
compie un passaggio in più: la colonna dei vitigni, memorizzata come stringa con
i nomi separati da virgola, viene suddivisa in lista. Questa forma a lista è il
formato che la trasformazione per vitigno si aspetta di ricevere, e prepararlo
qui mantiene la responsabilità della lettura concentrata in un solo punto.

### Calcolo dello stress di fermentazione

È la parte computazionalmente più impegnativa, contenuta in `computations.py`.

L'indice di stress misura quanto le letture di una cisterna siano disomogenee.
L'idea di fondo: una fermentazione sana procede stabile, mentre forti variazioni
di pH e temperatura tra una lettura e l'altra segnalano un rischio di
fermentazione irregolare; inoltre le cisterne di volume ridotto, termicamente
meno stabili, sono più esposte. La formula confronta perciò **ogni coppia di
letture**, somma le differenze di pH e di temperatura (quest'ultima pesata
doppia) e le pondera con un fattore che cresce al diminuire del volume, per poi
normalizzare il totale.

Confrontare tutte le coppie significa che, con `n` letture, il numero di
confronti cresce con il quadrato di `n`: è una complessità O(n²), che su grandi
dataset diventa costosa. Il progetto interviene su due fronti.

Il primo è la **compilazione con Numba**. Il decoratore `@njit` traduce la
funzione da Python a codice macchina alla prima chiamata, avvicinandone la
velocità a quella di un linguaggio compilato. Tre opzioni ne aumentano l'efficacia:
il rilascio del blocco che serializza i thread di Python permette di calcolare più
cisterne davvero in parallelo; il salvataggio su disco del codice compilato evita
di ripagarne il costo agli avvii successivi; una modalità aritmetica più rapida
accelera i conti in virgola mobile, lecita qui perché i dati escludono divisioni
per zero.

Il secondo è un'**ottimizzazione algoritmica**. Il contributo della coppia
`(i, j)` è identico a quello della coppia `(j, i)`, e il confronto di una lettura
con sé stessa è nullo. Percorrere l'intera griglia delle coppie ripeterebbe
quindi ogni calcolo due volte. Il codice valuta solo metà delle coppie e
raddoppia il totale: il risultato è lo stesso, ma i confronti effettivi si
dimezzano.

Sopra la formula, la classe `WineryHPCComputations` partiziona le letture per
cisterna, calcola lo stress su ciascun gruppo, distribuendo il lavoro sui core
disponibili tramite **Joblib**, e riporta il punteggio, costante per cisterna,
su tutte le righe corrispondenti nella colonna `stress_score`.

### Le trasformazioni

Il modulo `transformations.py` definisce `WineryTransformer`, che aggiunge al
DataFrame colonne statistiche senza alterare quelle originali. Le trasformazioni
disponibili sono quattro:

- **pH medio per cisterna** (`avg_pH_per_tank`): media del pH calcolata per
  cisterna e riportata su ogni riga del gruppo.
- **Numero di letture per cisterna** (`tank_num_readings`): conteggio delle
  letture di ogni cisterna.
- **Deviazione di temperatura** (`temperature_deviation`): scarto assoluto della
  temperatura da un valore standard di riferimento. Quando il volume è noto,
  aggiunge anche una versione rapportata a mille litri, che rende confrontabili
  cisterne di dimensioni diverse.
- **Numero di letture per vitigno** (`grape_variety_num_readings`): unisce le
  informazioni sulle cisterne alle letture e conta quante letture competono a
  ciascun vitigno.

Le prime tre preservano il numero di righe; l'ultima lo modifica, perché ogni
lettura viene replicata per ciascun vitigno della sua cisterna. Per questo
motivo è applicata per ultima, ed è eseguita solo quando le informazioni sulle
cisterne sono disponibili: in loro assenza viene semplicemente omessa.

### Orchestrazione e registrazione

Il modulo `pipeline.py` definisce `WineryPipeline`, che riceve la lista degli
analizzatori e li esegue in ordine. Al termine, su richiesta, registra una
sintesi dei risultati su **Weights & Biases**, uno strumento di tracciamento
degli esperimenti: una voce per cisterna con il relativo punteggio di stress.

La registrazione avviene in modalità **offline** per impostazione predefinita:
i dati restano in una cartella locale e non richiedono né account né
autenticazione, così l'esecuzione è riproducibile da chiunque. Una variabile
d'ambiente permette di passare alla modalità online senza modificare il codice.

Il modulo `main.py` collega ogni pezzo: la funzione `run_full_pipeline` carica i
due file, costruisce gli analizzatori nell'ordine corretto, li affida alla
pipeline e scrive il DataFrame finale su file.

---

## Requisiti

- Python 3.10 o superiore
- [Polars](https://pola.rs/) — manipolazione dei DataFrame ad alte prestazioni
- [Numba](https://numba.pydata.org/) — compilazione in codice macchina del calcolo dello stress
- [NumPy](https://numpy.org/) — array numerici in ingresso al calcolo dello stress
- [Joblib](https://joblib.readthedocs.io/) — distribuzione del calcolo sui core disponibili
- [Weights & Biases](https://wandb.ai/) — registrazione dei risultati
- [Pytest](https://docs.pytest.org/) — esecuzione della suite di test

Le versioni esatte di ogni dipendenza sono fissate in `requirements.txt`, così
che l'ambiente sia ricostruibile in modo identico.

---

## Installazione

Le istruzioni ricreano un ambiente isolato con le dipendenze corrette. Un
ambiente dedicato evita conflitti con altri pacchetti già presenti sul sistema.

**1. Clonare il repository e spostarsi nella cartella di progetto.** Il comando
`git clone` scarica una copia locale del repository; `cd` entra nella cartella
appena creata.

```bash
git clone <URL-del-repository>
cd Winery-Adventures
```

**2. Creare e attivare un ambiente dedicato.** Il primo comando crea un ambiente
Conda di nome `winery` con la versione di Python richiesta; il secondo lo attiva,
in modo che le installazioni successive restino confinate al suo interno e non
tocchino il Python di sistema.

```bash
conda create -n winery python=3.12
conda activate winery
```

**3. Installare le dipendenze.** Il comando legge `requirements.txt` e installa
tutte le librerie alle versioni fissate, riproducendo l'ambiente di sviluppo.

```bash
pip install -r requirements.txt
```

**4. Verificare l'installazione.** L'esecuzione della suite di test conferma che
il codice e le dipendenze funzionano come atteso. Un esito completamente positivo
indica un ambiente pronto all'uso.

```bash
pytest
```

---

## Uso

La funzione `run_full_pipeline` esegue l'intero flusso, dai file di ingresso al
file di uscita:

```python
from winery_adventures.main import run_full_pipeline

result = run_full_pipeline(
    input_csv="data/sensors_sample.tsv",
    tank_info_csv="data/tank_info_sample.tsv",
    output_csv="output.csv",
)
```

Al termine, il DataFrame arricchito è disponibile come valore restituito e
salvato in `output.csv`. La sintesi dello stress per cisterna è registrata in
modalità offline nella cartella locale `wandb/`. Per inviare i dati a un progetto
remoto, impostare la variabile d'ambiente `WANDB_MODE=online` prima
dell'esecuzione.

I file in `data/` sono di piccole dimensioni, adatti allo sviluppo e alla
verifica rapida. Per misurare le prestazioni su volumi realistici, lo script
`data_generator.py` produce un dataset di grandi dimensioni.

---

## Formato dei dati

Il file delle letture dei sensori associa a ogni cisterna una serie di
misurazioni nel tempo:

```
tank_id	time	pH	temp	quantity_liters
1	2025-01-01 00:00	3.4	25.0	500
1	2025-01-01 01:00	3.5	26.0	500
```

Il file delle informazioni sulle cisterne descrive capacità e vitigni ospitati;
i vitigni sono elencati in un'unica stringa separata da virgole:

```
tank_id	grape_variety	capacity_liters
1	CannonauVellutato,BovaleBarricato	1344
2	VermentinoAromatico,NuragusIntenso	1279
```

---

## Test

La suite si esegue con Pytest dalla radice del progetto:

```bash
pytest
```

I test si dividono in due gruppi. I **test unitari**, in `tests/unit/`, verificano
il comportamento dei singoli componenti in isolamento: la classe base, le
trasformazioni, il calcolo dello stress e l'orchestrazione. I **test di
accettazione**, in `tests/acceptance/`, validano l'intera pipeline dai file di
ingresso al risultato finale, controllando che i componenti collaborino
correttamente. I test costituiscono anche la specifica del sistema: l'intera
implementazione è stata sviluppata per soddisfarli.

---

## Documentazione

La documentazione delle interfacce del codice è generata da Sphinx a partire
dalle docstring dei moduli. Per produrla, dalla radice del progetto:

```bash
sphinx-apidoc -o docs winery_adventures
sphinx-build -b html docs docs/_build/html
```

Il primo comando genera una pagina per ciascun modulo del pacchetto; il secondo
costruisce il sito HTML. Il manuale risultante è consultabile aprendo
`docs/_build/html/index.html`.

---

## Performance

Il report di profilazione, in `docs/performance.md`, analizza i tempi di
esecuzione e l'occupazione di memoria, con particolare attenzione al calcolo
dello stress. Gli script che producono le misure si trovano in `profiling/` e
coprono tre aspetti: il tempo del calcolo dello stress, l'impronta di memoria e
il comportamento in parallelo. Le due ottimizzazioni descritte
nell'[architettura](#calcolo-dello-stress-di-fermentazione), compilazione con
Numba e riduzione delle coppie valutate, sono l'oggetto principale dell'analisi.

---

## Diagrammi UML

I diagrammi di progettazione sono in `docs/uml/`, disponibili sia come sorgenti
PlantUML (`.puml`) sia come immagini (`.png`):

- **Diagramma delle classi**: la struttura statica del sistema, con la classe
  base astratta, le sue sottoclassi e le relazioni.
- **Diagramma di sequenza**: il flusso di esecuzione della pipeline nel tempo.
- **Diagramma dei casi d'uso**: le funzionalità dal punto di vista dell'utente.

---

## Qualità del codice

Il codice segue le convenzioni di stile PEP 8 ed è verificato con lo strumento
di analisi statica Ruff, configurato in `pyproject.toml`. L'architettura è
orientata agli oggetti attorno al contratto della classe base astratta, i moduli
hanno responsabilità separate, e ogni classe, funzione e metodo è corredato da
una docstring che ne descrive scopo, parametri e valore restituito.

---

## Licenza

Il progetto è distribuito secondo i termini indicati nel file `LICENSE`.

---

## Autori

Luca Bellu e Michele Sciarra.
