import importlib
import importlib.util
import subprocess
import sys


def ensure_packages(pkgs):
    """Check packages by import spec; pip install if missing.

    Uses find_spec so we avoid importing heavy modules (transformers/tensorflow)
    during startup.

    Handles mapping between pip package names and import names (e.g. scikit-learn -> sklearn).
    """
    import_name_map = {
        "scikit-learn": "sklearn",
    }
    for pkg in pkgs:
        import_name = import_name_map.get(pkg, pkg)
        try:
            spec = importlib.util.find_spec(import_name)
            if spec is None:
                raise ModuleNotFoundError(import_name)
        except Exception:
            print(f"Package {pkg} (import as {import_name}) missing, attempting install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
            except subprocess.CalledProcessError as e:
                print(f"Failed to install {pkg}: {e}")
                raise


# Common entry point
REQUIRED = [
    "fastapi",
    "uvicorn",
    "streamlit",
    "kaggle",
    "scikit-learn",
    "pandas",
    "numpy",
    "pycaret",
    "transformers",
    "tensorflow",
    "torch",
    "joblib",
]

if __name__ == "__main__":
    ensure_packages(REQUIRED)
