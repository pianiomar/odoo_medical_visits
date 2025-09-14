# Modulo Visite Mediche ASD per Odoo

## Descrizione
Modulo personalizzato per Odoo 17 per la gestione delle visite mediche sportive degli atleti di un'Associazione Sportiva Dilettantistica (ASD).

## Caratteristiche Principali

### 🏃‍♂️ Gestione Atleti
- Anagrafica completa degli atleti
- Dati anagrafici, contatti e informazioni sportive
- Categorie e discipline sportive
- Contatti di emergenza
- Stato del certificato medico

### 🩺 Gestione Visite Mediche
- Registrazione completa delle visite
- Diversi tipi di visite (iniziale, rinnovo, controllo, ecc.)
- Gestione esiti e limitazioni
- Parametri fisici e vitali
- Upload documenti e certificati
- Calcolo automatico scadenze

### 📊 Dashboard e Controlli
- Vista dashboard con statistiche
- Monitoraggio scadenze automatico
- Notifiche per certificati in scadenza
- Report e filtri avanzati
- Vista calendario delle visite

### ⚙️ Configurazione
- Tipi di visita personalizzabili
- Centri medici convenzionati
- Template email per notifiche
- Cron job automatici

## Struttura del Modulo

```
medical_visits/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── athlete.py          # Modello Atleta
│   └── medical_visit.py    # Modello Visita Medica
├── views/
│   ├── athlete_views.xml   # Viste atleti
│   ├── medical_visit_views.xml  # Viste visite
│   ├── menu_views.xml      # Menu principale
│   └── config_views.xml    # Viste configurazione
├── security/
│   └── ir.model.access.csv # Permessi accesso
└── data/
    └── medical_visit_data.xml  # Dati iniziali
```

## Installazione

### Prerequisiti
- Odoo 17.0
- Dipendenze: `base`, `mail`, `web`

### Passi di installazione
1. Copiare la cartella del modulo in `addons/`
2. Riavviare il server Odoo
3. Aggiornare la lista delle app
4. Installare il modulo "Visite Mediche Atleti ASD"

## Configurazione Iniziale

### 1. Tipi di Visita
Vai su **Configurazione > Tipi di Visita** per configurare:
- Visita Iniziale (12 mesi validità)
- Rinnovo Certificato (12 mesi)
- Visita di Controllo (6 mesi)
- Visita Post-Infortunio
- Visita Specialistica

### 2. Centri Medici
Configura i centri medici convenzionati in **Configurazione > Centri Medici**

### 3. Sequenze
Le sequenze per i codici atleta e numeri visita sono create automaticamente

## Utilizzo

### Gestione Atleti
1. Vai su **Atleti > Tutti gli Atleti**
2. Clicca "Crea" per aggiungere un nuovo atleta
3. Compila i dati anagrafici e sportivi
4. Salva per generare automaticamente il codice atleta

### Registrazione Visite
1. Dalla scheda atleta, clicca "Nuova Visita"
2. Oppure vai su **Visite Mediche > Tutte le Visite**
3. Compila i dati della visita
4. La data di scadenza viene calcolata automaticamente
5. Carica i documenti necessari

### Monitoraggio Scadenze
- **Dashboard**: Panoramica generale
- **In Scadenza**: Certificati che scadono in 30 giorni
- **Scaduti**: Certificati da rinnovare urgentemente

## Funzionalità Avanzate

### Calcoli Automatici
- **Età**: Calcolata automaticamente dalla data di nascita
- **BMI**: Calcolato da altezza e peso
- **Giorni alla scadenza**: Aggiornati in tempo reale
- **Stato medico**: Valido/In scadenza/Scaduto/Nessuno

### Notifiche e Promemoria
- Cron job giornaliero per controllo scadenze
- Template email per notifiche
- Badge colorati per stati critici

### Viste Multiple
- **Tree**: Lista tabellare
- **Form**: Moduli dettagliati
- **Kanban**: Carte visuali
- **Calendar**: Vista calendario
- **Gantt**: Timeline delle scadenze

## Personalizzazioni

### Aggiungere nuove discipline sportive
Modifica il campo `sport_discipline` in `models/athlete.py`:

```python
sport_discipline = fields.Selection([
    ('football', 'Calcio'),
    ('basketball', 'Pallacanestro'),
    # Aggiungi qui le tue discipline
    ('your_sport', 'Tuo Sport'),
], string='Disciplina Sportiva', required=True)
```

### Modificare la validità dei certificati
Cambia il valore default in `models/medical_visit.py`:

```python
validity_months = fields.Integer(string='Mesi di Validità', default=12)  # Cambia qui
```

## Sicurezza
- Permessi configurati per utenti standard
- Accesso di sola lettura per utenti portale
- Configurazione ristretta agli amministratori di sistema

## Supporto e Manutenzione

### Log degli errori
Controlla i log di Odoo per eventuali errori:
```bash
tail -f /var/log/odoo/odoo-server.log
```

### Backup dei dati
Ricorda di fare backup regolari del database, specialmente dei documenti caricati.

### Aggiornamenti
Per aggiornare il modulo:
1. Sostituire i file
2. Riavviare Odoo
3. Aggiornare il modulo dal menu Apps

## Licenza
LGPL-3 - Vedi il file `__manifest__.py` per i dettagli

## Contatti
- Autore: [Il tuo nome]
- Email: [La tua email]
- Sito ASD: [www.tuaasd.it]

---

*Modulo sviluppato per la gestione efficiente delle visite mediche sportive in conformità alle normative italiane per le ASD.*