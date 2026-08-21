# Report di performance — Winery Adventures

Il documento raccoglie le misure di prestazione del sistema, con particolare
attenzione alla formula di stress da fermentazione (complessità O(n²)) e alla sua
esecuzione sull'intero dataset. Tre aspetti sono considerati: il tempo di
calcolo, la parallelizzazione e l'occupazione di memoria. Ogni misura è
riproducibile tramite gli script della cartella `profiling/`.

## Ambiente e dataset

| Voce | Valore |
| --- | --- |
| Sistema operativo | macOS (Apple Silicon) |
| Core disponibili | 10 |
| Python | 3.12 |
| Polars | 1.43.2 |
| NumPy | 2.5.2 |
| Numba | 0.67.0 |
| Joblib | 1.5.3 |
| Weights & Biases | 0.28.2 |
| Ruff | 0.16.3 |

Il dataset di riferimento è prodotto dallo script `data_generator.py`:
`data/full_sensors.tsv` contiene 100.000 letture su 100 cisterne, con circa il
10% di valori mancanti nella colonna `quantity_liters`; `data/full_tank_info.tsv`
contiene 100 cisterne con tre vitigni ciascuna. La formula di stress ha
complessità O(n²) per singola cisterna: con circa mille letture per cisterna il
costo per cisterna è dell'ordine del milione di coppie, per un totale dell'ordine
dei cento milioni di contributi sull'intero dataset.

## Metodologia

Le misure di tempo riportano il minimo su più ripetizioni, meno sensibile ai
disturbi del sistema operativo, e sono precedute da un riscaldamento che esclude
dal cronometraggio la compilazione JIT della prima chiamata. Tre script
autonomi, eseguibili come moduli dalla radice della repository, producono le
misure:

- `python -m profiling.benchmark_stress` — confronto della formula ottimizzata con l'implementazione a ciclo pieno di riferimento, su correttezza e tempo.
- `python -m profiling.benchmark_parallel` — confronto tra esecuzione seriale, a thread (con e senza `nogil`) e a processi.
- `python -m profiling.benchmark_memory` — memoria ausiliaria della formula e picco di memoria del processo.

## Tempo — ottimizzazione algoritmica della formula

La formula confronta ogni coppia di rilevazioni. Il contributo della coppia
`(i, j)` coincide con quello di `(j, i)` e la diagonale è nulla, quindi l'accumulo
percorre il solo triangolo superiore `i < j` e raddoppia il totale, valutando
circa la metà delle coppie a parità di risultato. La complessità resta O(n²): si
riduce la costante moltiplicativa, non la classe.

Misura sulla cisterna con più letture (n = 991):

| Implementazione | Tempo della funzione | Rapporto |
| --- | --- | --- |
| Ciclo pieno (riferimento) | 0,607 ms | 1,00x |
| Triangolo superiore (produzione) | 0,415 ms | 1,46x |

La differenza massima tra le due implementazioni su tutte le 100 cisterne è
7,89·10⁻¹³, entro la tolleranza `1e-7` dei test: il risultato è invariato. Il
guadagno reale, pari a circa 1,46x, resta inferiore al dimezzamento teorico
poiché il ciclo pieno è regolare e ben ottimizzato da compilatore e processore,
mentre il ciclo sul triangolo superiore compie meno iterazioni ma con efficienza
per iterazione inferiore. L'intera `analyze_data` sul dataset completo richiede
14,3 ms con la formula ottimizzata.

## Tempo — flag di compilazione Numba

La funzione è compilata con `@njit(fastmath=True, nogil=True, cache=True)`. Ogni
flag agisce su un aspetto distinto:

- `fastmath` concede aritmetica in virgola mobile più veloce e meno rigorosa. Il guadagno misurato è marginale, dell'ordine del 3%, poiché la funzione è dominata dalle divisioni per il volume, poco sensibili al flag; l'assunzione di assenza di valori infiniti è soddisfatta, dato che i volumi sono sempre positivi e i valori mancanti già esclusi.
- `nogil` rilascia il GIL durante l'esecuzione: il suo effetto non si osserva su un singolo thread, ma abilita il parallelismo effettivo dei thread, quantificato nella sezione seguente.
- `cache` salva su disco il codice compilato: il tempo della prima chiamata negli avvii successivi si riduce di circa un terzo, poiché il codice è letto da disco anziché ricompilato.

## Tempo — parallelizzazione

`WineryHPCComputations.analyze_data` distribuisce il calcolo per cisterna con
Joblib, backend a thread. Confronto su 10 core:

| Strategia | Tempo | Accelerazione |
| --- | --- | --- |
| Seriale (1 job) | 42,2 ms | 1,00x |
| Thread + `nogil` (produzione) | 12,0 ms | 3,53x |
| Thread senza `nogil` | 41,9 ms | 1,01x |
| Processi (loky) | 17,9 ms | 2,36x |

Il confronto tra thread con e senza `nogil` isola il contributo del flag: senza
il rilascio del GIL i thread non accelerano il calcolo compilato e il tempo resta
pari al seriale; con `nogil` i thread calcolano davvero in parallelo. I processi
aggirano il GIL e quindi accelerano rispetto al seriale, ma restano sotto i
thread per il costo di avvio dei processi e di serializzazione dei dati verso i
processi figli.

L'accelerazione dei thread, pari a circa 3,5x su 10 core anziché prossima a 10x,
riflette la frazione di lavoro non parallelizzabile (preparazione dei dati con
Polars e composizione del risultato) e il costo di distribuzione dei cento task,
secondo la legge di Amdahl.

Il backend a thread non è soltanto il più veloce: è l'unico compatibile con lo
schema di raccolta dei risultati adottato. Il banco di prova sostituisce
`joblib.Parallel` con un finto che esegue i task ma restituisce `None`, quindi il
codice raccoglie i risultati per effetto collaterale in una lista condivisa. Tale
schema produce risultati corretti solo con i thread, che condividono la memoria
del processo; con i processi la lista del processo padre resterebbe vuota. Thread
e `nogil` sono pertanto la scelta coerente sia con la correttezza sia con la
prestazione.

## Memoria

La formula compilata occupa memoria ausiliaria O(1): accumula uno scalare e non
materializza la matrice delle coppie. Una variante vettorizzata equivalente, che
costruisce matrici n×n, occupa invece memoria O(n²). Misura sulla cisterna con più
letture (n = 991), picco lato Python rilevato con `tracemalloc`:

| Elemento | Memoria |
| --- | --- |
| Array di ingresso (3 × n × 8 byte) | 23,2 KB |
| Ciclo compilato (produzione) | 0,1 KB — memoria O(1) |
| Variante vettorizzata | 29,97 MB — memoria O(n²) |

Il ciclo compilato è quindi ottimale non solo nel tempo ma anche nella memoria: a
parità di risultato occupa oltre cinque ordini di grandezza in meno rispetto alla
variante vettorizzata.

Il picco di memoria residente dell'intero processo durante `analyze_data` sul
dataset da 100.000 letture è di circa 230 MB. La misura comprende l'interprete
Python, le librerie, il dataset in memoria, la compilazione JIT una tantum e la
duplicazione dei dati operata da `partition_by`; il calcolo O(n²) in sé non
contribuisce, poiché non alloca memoria. La misura del processo è ottenuta con il
picco RSS letto da `resource`, non con `tracemalloc`, che non osserva la memoria
nativa di Polars (Arrow/Rust).

## Registrazione dei risultati

La pipeline registra su Weights & Biases una voce di `stress_score` per cisterna.
La registrazione avviene in modalità offline per default: i dati restano locali
nella cartella `wandb/` e non richiedono account né autenticazione, a garanzia
della riproducibilità. La variabile d'ambiente `WANDB_MODE` consente la modalità
online senza modificare il codice; le run offline sono sincronizzabili in seguito
con `wandb sync`.

## Conclusioni

La configurazione di produzione — accumulo sul triangolo superiore, compilazione
`@njit(fastmath=True, nogil=True, cache=True)` e parallelizzazione a thread —
risulta ottimale sia nel tempo sia nella memoria. L'ottimizzazione algoritmica
dimezza le coppie valutate; i flag di compilazione, in particolare `nogil`,
abilitano un'accelerazione di circa 3,5x su 10 core; la formula mantiene memoria
ausiliaria costante, evitando la materializzazione della matrice delle coppie. Il
backend a thread è al contempo il più veloce e l'unico coerente con lo schema di
raccolta dei risultati imposto dal banco di prova.