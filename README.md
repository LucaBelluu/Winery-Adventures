# 🍷 Winery Adventures 🍇

## Benvenuti nel Progetto di Winery Adventures!

Winery Adventures è un affascinante progetto di data science incentrato sulla gestione e l'analisi di dati provenienti da una piccola cantina moderna. In un'epoca in cui la qualità del prodotto e l'efficienza produttiva diventano sempre più importanti, Winery Adventures offre strumenti avanzati per monitorare, analizzare e ottimizzare le condizioni delle cisterne di fermentazione del vino.

Questo progetto integra concetti di ingegneria del software, data science, e programmazione orientata agli oggetti per creare un sistema completo che permette di:

- Raccogliere e processare dati da sensori distribuiti nelle cisterne di fermentazione
- Analizzare parametri critici come pH, temperatura e volume del mosto
- Visualizzare trend e anomalie nei dati
- Generare reportistica avanzata sullo stato della fermentazione
- Prevedere potenziali problemi prima che diventino critici

Attraverso pipeline di dati efficienti e algoritmi ottimizzati, Winery Adventures trasforma semplici letture di sensori in informazioni preziose, contribuendo alla qualità del vino e all'efficienza operativa della cantina.

## 🎯 Obiettivi del Progetto

Il vostro compito è sviluppare un sistema software basato su pipeline di elaborazione dati che analizzi i dati provenienti dai sensori delle cisterne di fermentazione di una cantina di piccole dimensioni. **Importante**: Avrete accesso solo ai test e non alle implementazioni di riferimento. Dovrete interpretare i requisiti dai test forniti e implementare le classi e le funzioni necessarie seguendo le best practices di ingegneria del software, proprio come in un contesto reale in cui i test e le specifiche siano dati da un cliente o da un team di sviluppo.

## Specifiche del Progetto

### Informazioni Generali

- **Tipo di Progetto**: Bonus (non obbligatorio)
- **Valore**: Fino a 3 punti bonus
- **Composizione Gruppi**: Da 2 a 4 studenti

Il progetto integra tutti gli argomenti trattati durante il corso, sia nella parte pratica che in quella teorica, inclusa la progettazione UML.

### Tecnologie e Framework

Il progetto richiede l'uso delle seguenti tecnologie:
- **Python 3.10+**: Linguaggio di programmazione principale
- **Polars**: Libreria per manipolazione dati ad alte prestazioni (simile a Pandas)
- **Numba**: Per ottimizzazione di funzioni con codice compilato JIT
- **Weights & Biases (wandb)**: Per il logging e la visualizzazione dei risultati
- **Joblib**: Per parallelizzazione di task computazionali
- **Pytest**: Per i test automatizzati

### Come Partecipare

Per partecipare al progetto, è necessario:

1. Formare un gruppo di lavoro (da 2 a 4 studenti)
2. Inviare una email al docente e tutor con:
   - Nomi dei componenti del gruppo
   - Numeri di matricola
3. Creare un repository GitHub per il progetto
4. Invitare il tutor Giulio Casti (username GitHub: GiulioCasti) come collaboratore

### Tempistiche

- **Scadenza**: Il progetto deve essere completato entro settembre
- **Valutazione**: In presenza, con presentazione del lavoro svolto dal gruppo

## Criteri di Valutazione

La valutazione del progetto sarà basata sui seguenti criteri:

### Gestione del Progetto e Riproducibilità
- Gestione delle dipendenze
- Documentazione chiara dei file di progetto
- Facilità di setup e riproduzione dell'ambiente di sviluppo

### Qualità del Codice
- Configurazione adeguata per la formattazione del codice
- Corretto utilizzo della programmazione orientata agli oggetti
- Stile di codice conforme agli standard

### DevOps e Automazione
- Implementazione di workflow per continuous integration
- Automazione di processi (es. test)
- Controllo dello stato dei workflow nelle pull request

### Performance e Ottimizzazione
- Report di profilazione delle performance
- Analisi dei tempi di esecuzione
- Utilizzo appropriato di librerie avanzate per l'ottimizzazione

### Documentazione
- Docstring complete per funzioni e classi
- Commenti chiari nel codice
- Documentazione utente e sviluppatore

### Modellazione
- Correttezza dei diagrammi UML
- Aderenza dell'implementazione ai diagrammi
- Appropriata astrazione e modellazione delle entità

### Testing
- Superamento dei test di accettazione
- Superamento dei test unitari
- Copertura adeguata dei test (aggiungere test se ritenuto necessario)

### Collaborazione e Uso degli Strumenti GitHub
- Comunicazione efficace tra i membri del team
- Utilizzo appropriato di commit, pull request e branch
- Revisione del codice tra pari
- Gestione delle issues

## Struttura del Repository

Il repository contiene già alcuni file e strutture che serviranno come punto di partenza:

- Test unitari e di accettazione nella cartella `tests/`
- Dataset di esempio nella cartella `data/`

Gli studenti dovranno completare l'implementazione seguendo i requisiti e facendo passare tutti i test.

## 🧩 Architettura del Sistema e Dettagli di Implementazione

### Panoramica dell'Architettura

Il sistema Winery Adventures è composto da diverse componenti che lavorano insieme in una pipeline di elaborazione dati:

1. **Data Loading**: Caricamento dei dati dai file sorgente (formato TSV)
2. **Data Transformation**: Trasformazioni dei dati (filtri, normalizzazioni, aggregazioni)
3. **Data Analysis**: Analisi computazionali avanzate sui dati trasformati
4. **Reporting**: Generazione di report e visualizzazioni

### Componenti da Implementare

#### 1. Base Class
- Classe astratta che prende in input un DataFrame Polars e restituisce un DataFrame trasformato
- Le sottoclassi devono implementare questo metodo con le loro specifiche analisi

#### 2. Pipeline di Elaborazione
- Gestisce il flusso di dati tra le varie componenti del sistema
- Carica dati da file TSV
- Applica trasformazioni in sequenza
- Esegue analisi sui dati trasformati

#### 3. Trasformazioni
- Implementare diverse trasformazioni sui dati
- Vanno applicate in sequenza tutte le trasformazioni e restituito il DataFrame trasformato
- Trasformazioni da implementare:
  - `add_avg_ph_per_tank`: Calcola il pH medio per ogni cisterna
  - `add_num_readings_per_tank`: Calcola il numero di rilevazioni per ogni cisterna
  - `add_num_readings_per_grape_variety`: Se fornite informazioni sui vitigni, calcola il numero di rilevazioni per ogni vitigno
  - `add_temperature_deviation`: Calcola la deviazione di temperatura rispetto a quella standard. Se la quantità in litri nella cisterna è disponibile, calcola la deviazione su 1000 litri

#### 4. Computazioni HPC
- Implementazione di funzioni di calcolo ottimizzate con Numba
- **Formula di Stress da Fermentazione**: Una formula O(n²) che valuta lo stress complessivo della fermentazione nelle cisterne, da implementare come segue:

> Input:
> - pH_vals: array NumPy con valori di pH per ogni rilevazione
> - temp_vals: array NumPy con valori di temperatura per ogni rilevazione
> - quantity_vals: array NumPy con valori di volume di mosto in litri per ogni rilevazione
>
> Algoritmo:
> 1. n = numero di rilevazioni (lunghezza degli array)
> 2. Se n = 0, restituisci 0.0
> 3. Inizializza stress_sum = 0.0
> 4. Per ogni coppia di rilevazioni (i, j) da 0 a n-1:\
>    a. pH_dev = |pH_vals[i] - pH_vals[j]| (deviazione assoluta dei valori di pH)\
>    b. t_dev = |temp_vals[i] - temp_vals[j]| * 2.0 (deviazione assoluta di temperatura moltiplicata per 2)\
>    c. quantity_factor = (500.0 / quantity_vals[i]) + (500.0 / quantity_vals[j])\
>    d. stress_sum += (pH_dev + t_dev) * quantity_factor\
> 5. Stress finale = stress_sum / (n * n)
>
> Output:
> - Un singolo valore floating point che rappresenta lo stress complessivo

L'idea è che una maggiore variabilità di pH e temperatura tra le rilevazioni (e cisterne di volume ridotto, quindi termicamente meno stabili) indichi un rischio più alto di fermentazione irregolare o bloccata.

- Ottimizzazione delle performance per grandi volumi di dati (particolare attenzione all'efficienza algoritmica e alla gestione della memoria)

### Dataset

I dataset forniti contengono:
- **sensors_*.tsv**: Dati dei sensori con misurazioni di pH, temperatura, volume del mosto, ecc.
- **tank_info_*.tsv**: Informazioni sulle varie cisterne della cantina (capacità, vitigni ospitati, ecc.)

Esempio di formato del dataset dei sensori (`sensors_*.tsv`):
```
tank_id	time	pH	temp	quantity_liters
1	2025-01-01 00:00	3.4	25.0	500
1	2025-01-01 01:00	3.5	26.0	500
2	2025-01-01 00:30	3.7	24.5	1000
```

Esempio di formato delle informazioni sulle cisterne (`tank_info_*.tsv`):
```
tank_id	grape_variety	capacity_liters
1	CannonauVellutato,BovaleBarricato,CarignanoNobile	1344
2	VermentinoAromatico,NuragusIntenso,NascoSapido	1279
```

Si consiglia di iniziare con i file di esempio più piccoli per lo sviluppo e il testing, e poi verificare la scalabilità con i dataset più grandi.
Successivamente, sarà necessario creare il dataset più grande tramite lo script `data_generator.py`, che restituirà un dataset di dimensioni maggiori.
I report di performance sulla memoria e sui tempi di computazione dovranno essere generati utilizzando questi dataset.

### Requisiti di Performance

- Le implementazioni devono essere efficienti e scalare bene con grandi volumi di dati
- È richiesta l'ottimizzazione della formula di stress tramite Numba
- Il sistema deve gestire correttamente i dataset di grandi dimensioni (>100,000 righe)

### Documentazione e Design UML Richiesti

Una parte fondamentale del progetto è la creazione della documentazione e dei diagrammi UML appropriati:

#### Diagrammi UML Richiesti
1. **Diagramma delle Classi**: Mostrare la struttura completa del sistema, incluse tutte le classi, interfacce, relazioni ed ereditarietà
2. **Diagramma di Sequenza**: Illustrare il flusso di esecuzione della pipeline di elaborazione dati
3. **Diagramma dei Casi d'Uso**: Rappresentare le principali funzionalità del sistema dal punto di vista dell'utente

#### Documentazione
- **README aggiornato**: Con istruzioni complete per l'installazione, configurazione e uso
- **Docstrings**: Ogni classe, funzione e metodo deve avere una docstring completa con descrizione, parametri e valori di ritorno
- **Commenti nel codice**: Per le sezioni più complesse o algoritmi non immediatamente comprensibili
- **Report di Performance**: Analisi delle performance delle implementazioni, specialmente per la funzione di stress da fermentazione

Assicuratevi di inserire la documentazione in formato compatibile con strumenti di generazione di documentazione come Sphinx.

### Requisiti di Qualità del Codice

- Il codice deve seguire le convenzioni PEP 8, sfruttando formatter e linter adeguati
- L'intero progetto deve essere strutturato secondo i principi della programmazione orientata agli oggetti
- Gestione degli errori robusta
- Implementazione di logging adeguato

---

Buon lavoro e buon divertimento con Winery Adventures! 🍷 🍇 🥂
