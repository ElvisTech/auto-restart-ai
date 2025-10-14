# RAG runbook helper (build and query FAISS index)
# Requires sentence-transformers and faiss-cpu.
from pathlib import Path
import os, pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss

RUNBOOK_DIR = Path(__file__).parent / "runbooks"
INDEX_DIR = RUNBOOK_DIR / "index"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
EMBED_DIM = 384

def _load_runbooks():
    docs = []
    if not RUNBOOK_DIR.exists():
        return docs
    for p in RUNBOOK_DIR.glob("**/*"):
        if p.is_file() and p.suffix.lower() in {".txt", ".md"}:
            t = p.read_text(encoding='utf-8', errors='ignore')
            docs.append({"text": t, "source": str(p)})
    return docs

def build_runbook_index(chunk_size=500, chunk_overlap=50):
    docs = _load_runbooks()
    if not docs:
        print("No runbook files found in runbooks/")
        return
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = []
    for d in docs:
        parts = splitter.split_text(d['text'])
        for i, p in enumerate(parts):
            chunks.append({'text': p, 'source': d['source'], 'chunk': i})
    model = SentenceTransformer(EMBED_MODEL_NAME)
    texts = [c['text'] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(EMBED_DIM)
    index.add(embeddings)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(INDEX_DIR / "runbook.index"))
    with open(INDEX_DIR / "docs.pkl", "wb") as f:
        pickle.dump(chunks, f)
    print(f"Built runbook index with {len(chunks)} chunks.")

def query_runbook(entity_name, log_line, top_k=3):
    idx_path = INDEX_DIR / "runbook.index"
    docs_path = INDEX_DIR / "docs.pkl"
    if not idx_path.exists() or not docs_path.exists():
        return []
    index = faiss.read_index(str(idx_path))
    with open(docs_path, "rb") as f:
        docs = pickle.load(f)
    model = SentenceTransformer(EMBED_MODEL_NAME)
    q = f"Service {entity_name}. Context: {log_line}"
    q_emb = model.encode([q], convert_to_numpy=True)
    faiss.normalize_L2(q_emb)
    D, I = index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0: continue
        results.append({'score': float(score), 'text': docs[idx]['text'], 'source': docs[idx]['source']})
    return results
