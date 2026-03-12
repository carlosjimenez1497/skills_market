from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import sqlite3
import fasttext

MODEL_URL = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"

@dataclass(frozen=True)
class LangResult:
    code: str
    confidence: float

_WS_RE = re.compile(r"\s+")

def preprocess_for_lang(text: str, max_chars: int = 6000) -> str:
    t = (text or "").strip()
    t = _WS_RE.sub(" ", t)
    return t[:max_chars]

def ensure_model(model_path: Path) -> None:
    if model_path.exists():
        return
    model_path.parent.mkdir(parents=True, exist_ok=True)
    # download without extra deps
    import urllib.request
    urllib.request.urlretrieve(MODEL_URL, model_path)

class FastTextLangDetector:
    def __init__(self, model_path: str | Path):
        self.model = fasttext.load_model(str(model_path))

    def detect_top2(self, text: str) -> tuple[LangResult, LangResult | None]:
        t = preprocess_for_lang(text)
        if len(t) < 30:
            return LangResult("und", 0.0), None

        labels, probs = self.model.predict(t, k=2)
        r1 = LangResult(labels[0].replace("__label__", ""), float(probs[0]))
        r2 = LangResult(labels[1].replace("__label__", ""), float(probs[1]))
        return r1, r2

def is_mixed_language(r1: LangResult, r2: LangResult | None, threshold: float = 0.15) -> int:
    # 1 if second language is close to first, else 0
    if not r2:
        return 0
    return 1 if (r1.confidence - r2.confidence) < threshold else 0

def enrich_job_languages(
    db_path: str,
    model_path: str = "lang_models/lid.176.ftz",
    batch_size: int = 500,
    only_missing: bool = True,
) -> int:
    model_path_p = Path(model_path)
    ensure_model(model_path_p)
    detector = FastTextLangDetector(model_path_p)
    print("model found")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    where = "WHERE description IS NOT NULL AND TRIM(description) <> ''"
    if only_missing:
        where += " AND (language_code IS NULL OR language_code = '')"

    # NOTE: requires you already added the language columns
    cur.execute(f"""
        SELECT id, description
        FROM jobs
        {where}
        ORDER BY id
    """)

    updated = 0
    rows_buffer = []

    for row in cur:
        job_id = row["id"]
        desc = row["description"]

        r1, r2 = detector.detect_top2(desc)
        mixed = is_mixed_language(r1, r2)

        rows_buffer.append((
            r1.code, r1.confidence,
            # (r2.code if r2 else None),
            # (r2.confidence if r2 else None),
            # mixed,
            job_id
        ))

        if len(rows_buffer) >= batch_size:
            print("executing batch")
            cur.executemany("""
                UPDATE jobs
                SET language_code=?,
                    language_confidence=?,
                    updated_at=CURRENT_TIMESTAMP
                WHERE id=?
            """, rows_buffer)
            conn.commit()
            updated += len(rows_buffer)
            rows_buffer.clear()

    if rows_buffer:
        print("executing Last batch")
        cur.executemany("""
            UPDATE jobs
            SET language_code=?,
                language_confidence=?,
                updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, rows_buffer)
        conn.commit()
        updated += len(rows_buffer)

    conn.close()
    return updated

if __name__ == "__main__":
    n = enrich_job_languages(db_path="db/jobs.db")
    print("Updated rows:", n)
