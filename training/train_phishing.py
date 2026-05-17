"""
Train the phishing detection model from the phishing dataset.

This script is intentionally standalone so it can be run with:
    python -m sentinel_ai.training.train_phishing
"""

from __future__ import annotations

from pathlib import Path
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score, precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = PROJECT_ROOT / "datasets" / "phishing" / "Phishing_Legitimate_full.csv"
MODEL_DIR = PROJECT_ROOT / "sentinel_ai" / "models" / "models_store"
MODEL_DIR.mkdir(parents=True, exist_ok=True)
MODEL_PATH = MODEL_DIR / "phishing_clf.joblib"


def load_phishing_data() -> tuple[pd.DataFrame, pd.Series]:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Phishing dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH, low_memory=False)
    df.columns = [str(column).strip() for column in df.columns]

    target_candidates = ["CLASS_LABEL", "class_label", "label", "Label", "Result", "result"]
    target_col = next((column for column in target_candidates if column in df.columns), None)
    if target_col is None:
        raise ValueError(f"Could not find target column in phishing CSV. Found columns: {list(df.columns)}")

    feature_cols = [column for column in df.columns if column.lower() not in {"id", target_col.lower()}]
    if not feature_cols:
        raise ValueError("No usable feature columns found in phishing dataset.")

    features = df[feature_cols].apply(pd.to_numeric, errors="coerce")
    target = pd.to_numeric(df[target_col], errors="coerce")

    valid_rows = target.notna()
    features = features.loc[valid_rows].reset_index(drop=True)
    target = target.loc[valid_rows].astype(int).reset_index(drop=True)

    return features, target


def train_phishing_model() -> None:
    print("--- Training Phishing Detection Model ---")
    print(f"Found phishing dataset: {DATA_PATH}")

    features, target = load_phishing_data()
    print(f"Loaded {len(features)} rows with {features.shape[1]} feature columns.")

    if len(features) > 50000:
        sample = features.sample(n=50000, random_state=42)
        target = target.loc[sample.index].reset_index(drop=True)
        features = sample.reset_index(drop=True)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=42,
        stratify=target,
    )

    pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "classifier",
                RandomForestClassifier(
                    n_estimators=200,
                    random_state=42,
                    n_jobs=-1,
                    class_weight="balanced_subsample",
                ),
            ),
        ]
    )

    print("Training phishing classifier...")
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    probabilities = pipeline.predict_proba(x_test)[:, 1]

    accuracy = accuracy_score(y_test, predictions)
    try:
        auc = roc_auc_score(y_test, probabilities)
    except ValueError:
        auc = None

    print(f"Phishing accuracy: {accuracy:.4f}")
    if auc is not None:
        print(f"Phishing ROC-AUC: {auc:.4f}")

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="binary",
        pos_label=1,
        zero_division=0,
    )
    print(f"Phishing precision (class=1): {precision:.4f}")
    print(f"Phishing recall (class=1): {recall:.4f}")
    print(f"Phishing F1 (class=1): {f1:.4f}")
    print(classification_report(y_test, predictions, digits=4))

    artifact = {
        "model": pipeline,
        "feature_columns": list(features.columns),
        "target_column": "CLASS_LABEL",
        "source_dataset": str(DATA_PATH),
    }
    joblib.dump(artifact, MODEL_PATH)
    print(f"Saved phishing model to {MODEL_PATH}")


if __name__ == "__main__":
    try:
        train_phishing_model()
    except Exception as exc:
        print(f"Phishing training failed: {exc}")
        raise