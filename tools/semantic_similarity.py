import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

DATABASE_PATH = "database/truth.db"
model = SentenceTransformer("all-MiniLM-L6-v2")


def connect_db():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def check_database_similarity(incoming_claim: str, similarity_threshold: float = 0.65) -> dict:
    result = {
        "match_found": False,
        "type": "NEW",
        "matched_record": None,
        "score": 0.0
    }

    if not incoming_claim or not incoming_claim.strip():
        return result

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, claim, status, confidence, evidence FROM claims")
    records = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if not records:
        return result

    existing_claims = [r["claim"] for r in records if r.get("claim")]

    if not existing_claims:
        return result
    
    existing_embeddings = model.encode(existing_claims, convert_to_numpy=True)
    incoming_embedding = model.encode([incoming_claim], convert_to_numpy=True)
   
    scores = cosine_similarity(incoming_embedding, existing_embeddings)[0]

    best_idx = int(np.argmax(scores))
    best_score = float(scores[best_idx])

    result["score"] = round(best_score, 3)

    if best_score >= similarity_threshold:
        result["match_found"] = True
        result["type"] = "REDUNDANT"
        result["matched_record"] = records[best_idx]

    return result