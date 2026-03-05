# ◈ DocMind — RAG Chatbot su Snowflake

Chatbot AI con pipeline RAG completa: upload di documenti `.txt` → embedding vettoriale su Snowflake Cortex → risposta contestuale via LLM.

---

## Stack

| Componente | Tecnologia |
|---|---|
| Frontend / UI | Streamlit |
| Vector DB | Snowflake (VECTOR type) |
| Embedding model | `e5-base-v2` via Snowflake Cortex |
| LLM | `mistral-7b` via Snowflake Cortex |
| Deploy | Streamlit Cloud |

---

## Setup in 4 passi

### 1. Prepara Snowflake

Apri un worksheet sul tuo account Snowflake ed esegui tutto il contenuto di `setup_snowflake.sql`.

### 2. Clona il repo e configura i secrets

```bash
git clone <TUO_REPO_URL>
cd rag_chatbot

# Crea la cartella secrets (non tracciata da git)
mkdir -p .streamlit
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edita .streamlit/secrets.toml con i tuoi dati Snowflake
```

### 3. Testa in locale

```bash
pip install -r requirements.txt
streamlit run app.py
```

Apri `http://localhost:8501`

### 4. Pubblica su Streamlit Cloud

1. Pusha il codice su GitHub (`.gitignore` esclude già i secrets)
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Clicca **New app** → seleziona il tuo repo → `app.py`
4. Vai su **Advanced settings → Secrets** e incolla il contenuto di `secrets.toml`
5. Clicca **Deploy** — ottieni un URL pubblico da condividere con i co-founders

---

## Come usare il chatbot

1. **Sidebar → Upload .txt** — carica uno o più file di testo
2. **Clicca "Start Ingestion"** — i documenti vengono chunkizzati, embeddati e salvati su Snowflake
3. **Chat input** — fai domande sui documenti caricati
4. Le risposte mostrano le sorgenti e i punteggi di rilevanza

---

## Parametri configurabili (in `app.py`)

| Parametro | Default | Dove |
|---|---|---|
| Chunk size | 1000 parole | `chunk_text()` |
| Chunk overlap | 150 parole | `chunk_text()` |
| Top-K retrieval | 5 chunks | `retrieve_context()` |
| LLM model | `mistral-7b` | `generate_answer()` |

---

## Struttura file

```
rag_chatbot/
├── app.py                          # App Streamlit principale
├── requirements.txt                # Dipendenze Python
├── setup_snowflake.sql             # Script SQL setup iniziale
├── .gitignore
└── .streamlit/
    └── secrets.toml.example        # Template credenziali (non fare commit del vero secrets.toml)
```
