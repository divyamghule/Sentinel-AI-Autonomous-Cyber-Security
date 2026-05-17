import joblib
from pathlib import Path
import numpy as np
import re
from urllib.parse import urlparse

# Store models inside sentinel_ai/models/models_store
MODEL_DIR = Path(__file__).resolve().parent / "models_store"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


class PhishingDetector:
    """Uses transformer to create embeddings, then a sklearn classifier.

    This is a lightweight, modular implementation that can be replaced
    with a fully fine-tuned transformer model for production.
    """

    def __init__(self, clf_path=MODEL_DIR / "phishing_clf.joblib"):
        self.clf_path = Path(clf_path)
        self.clf = None
        self.feature_columns = None
        self._load()

    def _load(self):
        if self.clf_path.exists():
            loaded = joblib.load(self.clf_path)
            # Support both plain estimator and artifact dict format
            if isinstance(loaded, dict) and "model" in loaded:
                self.clf = loaded["model"]
                self.feature_columns = loaded.get("feature_columns")
            else:
                self.clf = loaded

    def train(self, X_emb, y):
        from sklearn.ensemble import RandomForestClassifier

        clf = RandomForestClassifier(n_estimators=100, n_jobs=-1)
        clf.fit(X_emb, y)
        joblib.dump(clf, self.clf_path)
        self.clf = clf
        return clf

    def embed(self, texts):
        # Transformer embeddings using a sentence-transformers style model
        try:
            from transformers import AutoTokenizer, TFAutoModel
            import tensorflow as tf
        except Exception:
            # fallback: simple char-level counts
            return np.array([[len(t), t.count(".")] for t in texts], dtype=float)

        tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
        model = TFAutoModel.from_pretrained("distilbert-base-uncased")
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors="tf")
        outputs = model(**inputs)
        # mean pooling
        emb = tf.reduce_mean(outputs.last_hidden_state, axis=1).numpy()
        return emb

    def predict(self, texts):
        if self.clf is None:
            raise RuntimeError("No classifier trained yet")

        # If model expects tabular engineered features but we only have raw URLs,
        # use heuristic scoring so the scanner still works reliably.
        if self.feature_columns:
            return np.array([self._heuristic_url_score(t) for t in texts], dtype=float)

        emb = self.embed(texts)
        return self.clf.predict_proba(emb)[:, 1]

    def _heuristic_url_score(self, url: str) -> float:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path or ""
        query = parsed.query or ""
        url_l = url.lower()

        score = 0.05
        if parsed.scheme != "https":
            score += 0.15
        if re.search(r"\d+\.\d+\.\d+\.\d+", host):
            score += 0.25
        if "@" in url:
            score += 0.20
        if len(url) > 90:
            score += 0.10
        if host.count("-") >= 2:
            score += 0.08
        if host.count(".") >= 3:
            score += 0.08
        if any(k in url_l for k in ["verify", "login", "update", "account", "secure", "bank", "gift", "reward"]):
            score += 0.20
        if len(query) > 25:
            score += 0.07
        if "//" in path:
            score += 0.07
        return float(min(score, 0.99))


if __name__ == "__main__":
    print("Phishing model module")
