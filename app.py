import streamlit as st
import snowflake.connector
import os
import hashlib
import time
from typing import List, Tuple

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocMind · AI Knowledge Base",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=Syne:wght@400;600;700;800&display=swap');

/* Reset & base */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e4dc;
    font-family: 'DM Mono', monospace;
}

/* Hide default Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0f0f18 !important;
    border-right: 1px solid #1e1e2e;
}
[data-testid="stSidebar"] * { font-family: 'DM Mono', monospace !important; }

/* Main area padding */
.main .block-container { padding: 2rem 2.5rem 4rem; max-width: 900px; margin: 0 auto; }

/* Logo / header */
.app-logo {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.7rem;
    letter-spacing: -0.03em;
    color: #e8e4dc;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.2rem;
}
.app-logo span { color: #7c6af7; }
.app-tagline {
    font-size: 0.72rem;
    color: #555570;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 2rem;
}

/* Section labels */
.section-label {
    font-size: 0.65rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #555570;
    margin: 1.5rem 0 0.6rem;
    border-bottom: 1px solid #1e1e2e;
    padding-bottom: 0.4rem;
}

/* Status badge */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.7rem;
    padding: 0.3rem 0.7rem;
    border-radius: 2px;
    background: #141420;
    border: 1px solid #2a2a3e;
    color: #8888aa;
    margin-bottom: 0.5rem;
}
.status-badge.ok { border-color: #2a4a2a; color: #5a9a5a; background: #0f1a0f; }
.status-badge.err { border-color: #4a2a2a; color: #9a5a5a; background: #1a0f0f; }
.dot { width: 6px; height: 6px; border-radius: 50%; background: currentColor; }

/* Doc list in sidebar */
.doc-item {
    font-size: 0.72rem;
    color: #888899;
    padding: 0.4rem 0.6rem;
    background: #141420;
    border: 1px solid #1e1e2e;
    border-radius: 2px;
    margin-bottom: 0.3rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.doc-item::before { content: "◈"; color: #7c6af7; font-size: 0.6rem; }

/* Chat container */
.chat-wrapper {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
}

/* Messages */
.msg {
    padding: 1rem 1.2rem;
    border-radius: 3px;
    line-height: 1.65;
    font-size: 0.85rem;
}
.msg-user {
    background: #13131f;
    border: 1px solid #2a2a3e;
    border-left: 3px solid #7c6af7;
    margin-left: 3rem;
}
.msg-assistant {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-left: 3px solid #3a8a6a;
    margin-right: 3rem;
}
.msg-role {
    font-size: 0.62rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    opacity: 0.5;
}
.msg-user .msg-role { color: #7c6af7; }
.msg-assistant .msg-role { color: #3a8a6a; }

/* Sources */
.sources-box {
    margin-top: 0.8rem;
    padding: 0.6rem 0.8rem;
    background: #0a0a12;
    border: 1px solid #1a1a28;
    border-radius: 2px;
    font-size: 0.7rem;
    color: #555570;
}
.sources-box strong { color: #7c6af7; font-weight: 500; letter-spacing: 0.05em; }

/* Input area */
[data-testid="stChatInput"] {
    background: #0f0f1a !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 3px !important;
    color: #e8e4dc !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #7c6af7 !important;
    box-shadow: 0 0 0 1px #7c6af720 !important;
}

/* Buttons */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.08em !important;
    background: #13131f !important;
    color: #e8e4dc !important;
    border: 1px solid #2a2a3e !important;
    border-radius: 2px !important;
    padding: 0.5rem 1.2rem !important;
    transition: all 0.15s ease !important;
}
.stButton > button:hover {
    background: #1e1e30 !important;
    border-color: #7c6af7 !important;
    color: #a89ff7 !important;
}
.stButton > button[kind="primary"] {
    background: #7c6af7 !important;
    border-color: #7c6af7 !important;
    color: #fff !important;
}
.stButton > button[kind="primary"]:hover {
    background: #9080ff !important;
    border-color: #9080ff !important;
}

/* File uploader */
[data-testid="stFileUploader"] {
    background: #0f0f1a !important;
    border: 1px dashed #2a2a3e !important;
    border-radius: 3px !important;
}

/* Alerts */
.stAlert { border-radius: 2px !important; font-family: 'DM Mono', monospace !important; font-size: 0.8rem !important; }

/* Metric */
[data-testid="stMetric"] {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    padding: 0.8rem 1rem;
    border-radius: 2px;
}
[data-testid="stMetricLabel"] { font-size: 0.65rem !important; color: #555570 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; }
[data-testid="stMetricValue"] { font-family: 'Syne', sans-serif !important; color: #e8e4dc !important; font-size: 1.6rem !important; font-weight: 700 !important; }

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2a2a3e; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #7c6af7; }

/* Progress */
.stProgress > div > div { background: #7c6af7 !important; }

/* Spinner */
.stSpinner > div { border-top-color: #7c6af7 !important; }
</style>
""", unsafe_allow_html=True)

# ── Snowflake connection ──────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_snowflake_connection():
    """Create a Snowflake connection using st.secrets."""
    try:
        conn = snowflake.connector.connect(
            account=st.secrets["snowflake"]["account"],
            user=st.secrets["snowflake"]["user"],
            password=st.secrets["snowflake"]["password"],
            warehouse=st.secrets["snowflake"]["warehouse"],
            database=st.secrets["snowflake"]["database"],
            schema=st.secrets["snowflake"]["schema"],
            role=st.secrets.get("snowflake", {}).get("role", ""),
        )
        return conn
    except Exception as e:
        return None

def run_query(conn, query: str, params=None):
    """Execute a query and return results."""
    cur = conn.cursor()
    cur.execute(query, params or [])
    return cur

# ── Database setup ────────────────────────────────────────────────────────────
def setup_database(conn):
    """Create tables if they don't exist."""
    run_query(conn, """
        CREATE TABLE IF NOT EXISTS DOCUMENTS (
            id VARCHAR(64) PRIMARY KEY,
            filename VARCHAR(500),
            chunk_index INTEGER,
            content TEXT,
            embedding VECTOR(FLOAT, 1024),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
        )
    """)

def get_doc_stats(conn) -> dict:
    """Get document statistics."""
    cur = run_query(conn, "SELECT COUNT(DISTINCT filename) as docs, COUNT(*) as chunks FROM DOCUMENTS")
    row = cur.fetchone()
    return {"docs": row[0] if row else 0, "chunks": row[1] if row else 0}

def get_doc_list(conn) -> List[str]:
    """Get list of ingested documents."""
    cur = run_query(conn, "SELECT DISTINCT filename FROM DOCUMENTS ORDER BY filename")
    return [row[0] for row in cur.fetchall()]

# ── Text chunking ─────────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 150) -> List[str]:
    """Split text into overlapping chunks."""
    if not text.strip():
        return []
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return [c for c in chunks if c.strip()]

# ── Ingestion ─────────────────────────────────────────────────────────────────
def ingest_document(conn, filename: str, content: str, progress_cb=None) -> int:
    """Chunk, embed and store a document. Returns number of chunks inserted."""
    chunks = chunk_text(content)
    if not chunks:
        return 0

    # Delete existing chunks for this file (upsert behaviour)
    run_query(conn, "DELETE FROM DOCUMENTS WHERE filename = %s", [filename])

    inserted = 0
    for i, chunk in enumerate(chunks):
        chunk_id = hashlib.sha256(f"{filename}:{i}:{chunk[:50]}".encode()).hexdigest()
        # Generate embedding via Snowflake Cortex
        run_query(conn, """
            INSERT INTO DOCUMENTS (id, filename, chunk_index, content, embedding)
            SELECT
                %s, %s, %s, %s,
                SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-base-v2', %s)
        """, [chunk_id, filename, i, chunk, chunk])
        inserted += 1
        if progress_cb:
            progress_cb(inserted / len(chunks))

    return inserted

# ── Retrieval ─────────────────────────────────────────────────────────────────
def retrieve_context(conn, question: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
    """Vector similarity search. Returns list of (filename, content, score)."""
    cur = run_query(conn, """
        WITH query_embed AS (
            SELECT SNOWFLAKE.CORTEX.EMBED_TEXT_1024('e5-base-v2', %s) AS emb
        )
        SELECT
            d.filename,
            d.content,
            VECTOR_COSINE_SIMILARITY(d.embedding, q.emb) AS score
        FROM DOCUMENTS d, query_embed q
        ORDER BY score DESC
        LIMIT %s
    """, [question, top_k])
    return [(row[0], row[1], row[2]) for row in cur.fetchall()]

# ── LLM answer ────────────────────────────────────────────────────────────────
def generate_answer(conn, question: str, context_chunks: List[Tuple[str, str, float]]) -> str:
    """Call Snowflake Cortex LLM with RAG context."""
    if not context_chunks:
        context_str = "No relevant context found in the knowledge base."
    else:
        context_str = "\n\n---\n\n".join([
            f"[Source: {fname}, relevance: {score:.2f}]\n{content}"
            for fname, content, score in context_chunks
        ])

    prompt = f"""You are a precise technical assistant. Answer the user's question using ONLY the provided context.
If the answer is not in the context, say so clearly. Be concise and accurate.

CONTEXT:
{context_str}

QUESTION: {question}

ANSWER:"""

    # Escape single quotes for SQL
    safe_prompt = prompt.replace("'", "\\'")

    cur = run_query(conn, f"""
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            'mistral-7b',
            '{safe_prompt}'
        )
    """)
    row = cur.fetchone()
    return row[0] if row else "Unable to generate a response."

# ── Session state init ────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conn" not in st.session_state:
    st.session_state.conn = None
if "db_ready" not in st.session_state:
    st.session_state.db_ready = False

# ── Connection bootstrap ──────────────────────────────────────────────────────
conn = get_snowflake_connection()
if conn and not st.session_state.db_ready:
    try:
        setup_database(conn)
        st.session_state.db_ready = True
    except Exception:
        pass

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="app-logo">◈ <span>DocMind</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="app-tagline">AI · Knowledge Base · RAG</div>', unsafe_allow_html=True)

    # Connection status
    if conn and st.session_state.db_ready:
        st.markdown('<div class="status-badge ok"><span class="dot"></span>Snowflake connected</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge err"><span class="dot"></span>Connection error</div>', unsafe_allow_html=True)
        st.error("Check your secrets.toml configuration.")

    # Stats
    if conn and st.session_state.db_ready:
        stats = get_doc_stats(conn)
        col1, col2 = st.columns(2)
        col1.metric("Docs", stats["docs"])
        col2.metric("Chunks", stats["chunks"])

    # Upload section
    st.markdown('<div class="section-label">Ingest Documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Upload .txt files",
        type=["txt"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected")
        if st.button("◈  Start Ingestion", type="primary", use_container_width=True):
            if conn and st.session_state.db_ready:
                total_chunks = 0
                progress = st.progress(0.0)
                status = st.empty()
                for idx, uf in enumerate(uploaded_files):
                    status.markdown(f"<small>Processing **{uf.name}**…</small>", unsafe_allow_html=True)
                    content = uf.read().decode("utf-8", errors="replace")
                    def prog(p, _idx=idx, _total=len(uploaded_files)):
                        progress.progress((_idx + p) / _total)
                    n = ingest_document(conn, uf.name, content, prog)
                    total_chunks += n
                progress.progress(1.0)
                time.sleep(0.3)
                progress.empty()
                status.empty()
                st.success(f"✓ Ingestion complete — {total_chunks} chunks stored")
                st.rerun()
            else:
                st.error("No active Snowflake connection.")

    # Document list
    if conn and st.session_state.db_ready:
        doc_list = get_doc_list(conn)
        if doc_list:
            st.markdown('<div class="section-label">Knowledge Base</div>', unsafe_allow_html=True)
            for doc in doc_list:
                st.markdown(f'<div class="doc-item">{doc}</div>', unsafe_allow_html=True)

    # Clear chat
    st.markdown('<div class="section-label">Session</div>', unsafe_allow_html=True)
    if st.button("Clear chat history", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ── MAIN AREA ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-bottom:0.5rem;">
  <div style="font-family:'Syne',sans-serif;font-weight:800;font-size:2.2rem;letter-spacing:-0.04em;color:#e8e4dc;line-height:1.1;">
    Ask your<br><span style="color:#7c6af7;">documentation.</span>
  </div>
  <div style="font-size:0.72rem;color:#555570;letter-spacing:0.1em;text-transform:uppercase;margin-top:0.6rem;">
    Powered by Snowflake Cortex · RAG Pipeline
  </div>
</div>
<hr style="border:none;border-top:1px solid #1e1e2e;margin:1.2rem 0;">
""", unsafe_allow_html=True)

# Render chat history
if not st.session_state.messages:
    st.markdown("""
    <div style="text-align:center;padding:3rem 1rem;color:#333348;">
        <div style="font-size:2rem;margin-bottom:0.5rem;">◈</div>
        <div style="font-size:0.8rem;letter-spacing:0.08em;">Upload documents in the sidebar, then ask anything.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role_label = "you" if msg["role"] == "user" else "docmind"
        css_class = "msg-user" if msg["role"] == "user" else "msg-assistant"
        sources_html = ""
        if msg.get("sources"):
            srcs = ", ".join(set(s[0] for s in msg["sources"]))
            scores = " · ".join(f"{s[0].split('/')[-1]} ({s[2]:.2f})" for s in msg["sources"][:3])
            sources_html = f"""
            <div class="sources-box">
                <strong>SOURCES</strong> · {scores}
            </div>"""
        st.markdown(f"""
        <div class="msg {css_class}">
            <div class="msg-role">{role_label}</div>
            {msg["content"]}
            {sources_html}
        </div>
        """, unsafe_allow_html=True)

# Chat input
if prompt := st.chat_input("Ask something about your documents…"):
    if not conn or not st.session_state.db_ready:
        st.error("Snowflake is not connected. Check your configuration.")
    else:
        stats = get_doc_stats(conn)
        if stats["chunks"] == 0:
            st.warning("The knowledge base is empty. Upload and ingest documents first.")
        else:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            with st.spinner("Searching knowledge base…"):
                sources = retrieve_context(conn, prompt, top_k=5)
                answer = generate_answer(conn, prompt, sources)

            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "sources": sources,
            })
            st.rerun()
