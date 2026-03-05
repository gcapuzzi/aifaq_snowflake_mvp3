-- ============================================================
-- SETUP SNOWFLAKE per DocMind RAG Chatbot
-- Esegui questi comandi una sola volta nel tuo Snowflake worksheet
-- ============================================================

-- 1. Crea il database e lo schema dedicati
CREATE DATABASE IF NOT EXISTS RAG_DB;
USE DATABASE RAG_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- 2. Crea il warehouse (puoi usarne uno esistente)
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

USE WAREHOUSE COMPUTE_WH;

-- 3. Crea la tabella vettoriale
--    VECTOR(FLOAT, 1024) corrisponde all'output di e5-base-v2
CREATE TABLE IF NOT EXISTS DOCUMENTS (
    id          VARCHAR(64)    PRIMARY KEY,
    filename    VARCHAR(500),
    chunk_index INTEGER,
    content     TEXT,
    embedding   VECTOR(FLOAT, 1024),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- 4. Verifica che Cortex sia disponibile nella tua region
--    (deve restituire un risultato senza errori)
SELECT SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', 'Say hello') AS test;

-- 5. (Opzionale) Crea un utente dedicato per l'app
-- CREATE USER rag_app_user
--     PASSWORD = 'StrongPassword123!'
--     DEFAULT_WAREHOUSE = 'COMPUTE_WH'
--     DEFAULT_ROLE = 'SYSADMIN';
-- GRANT ROLE SYSADMIN TO USER rag_app_user;

-- ============================================================
-- MODELS USATI:
--   Embedding : SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-base-v2', ...)
--   LLM       : SNOWFLAKE.CORTEX.COMPLETE('mistral-7b', ...)
--
-- Puoi sostituire 'mistral-7b' con:
--   'mixtral-8x7b', 'llama3-70b', 'snowflake-arctic' ecc.
-- ============================================================
