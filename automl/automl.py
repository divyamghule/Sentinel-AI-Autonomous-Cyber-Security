import os
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MODEL_DIR = Path(__file__).resolve().parents[2] / "sentinel_ai" / "models" / "models_store"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def run_pycaret_classification(df, target_col, model_name="best_model"):
    try:
        from pycaret.classification import setup, compare_models, save_model
    except Exception as e:
        raise RuntimeError("PyCaret not available: " + str(e))

    exp = setup(data=df, target=target_col, html=False)
    best = compare_models()
    save_model(best, MODEL_DIR / model_name)
    return best


if __name__ == "__main__":
    print("AutoML helper")
