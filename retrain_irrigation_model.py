"""
Re-save the irrigation model with the scikit-learn version installed in this
environment, so the Random Forest, the encoder and the scaler all carry the
same version and the InconsistentVersionWarning disappears.

Run it from the project root, giving the project's PREPROCESSED dataset
(the zip or the folder that contains train_final.csv, validation_final.csv
and test_final.csv):

    python retrain_irrigation_model.py "C:\\path\\to\\Smart_Agriculture_Preprocessed.zip"
    python retrain_irrigation_model.py "C:\\path\\to\\Smart_Agriculture_Preprocessed"

What it does
    1. checks that the data matches the saved scaler and the feature order
    2. retrains the Random Forest with the documented configuration
       (GridSearchCV: n_estimators [50, 100], max_depth [5, 10], cv=3, accuracy,
       random_state=42; the documented best is n_estimators=100, max_depth=10)
    3. compares it with the current model on train / validation / test
    4. replaces the model only if it is not worse than the current one
    5. re-saves the existing encoder and scaler WITHOUT refitting them
       (the data was preprocessed with them, so they must not change)
    6. reloads everything and confirms there is no version warning
"""

import argparse
import shutil
import sys
import warnings
import zipfile
from pathlib import Path

import joblib
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestClassifier
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.model_selection import GridSearchCV


BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"

MODEL_PATH = ARTIFACTS_DIR / "random_forest_model.pkl"
ENCODER_PATH = ARTIFACTS_DIR / "encoder.pkl"
SCALER_PATH = ARTIFACTS_DIR / "scaler.pkl"
FEATURE_ORDER_PATH = ARTIFACTS_DIR / "feature_order.txt"
BACKUP_DIR = ARTIFACTS_DIR / "backup_before_retrain"

TARGET = "result"
NUMERICAL_FEATURES = ["MOI", "temp", "humidity"]

PARAM_GRID = {"n_estimators": [50, 100], "max_depth": [5, 10]}
DOCUMENTED_BEST = {"max_depth": 10, "n_estimators": 100}

# The new model may be at most this much worse than the current one (test accuracy)
ACCURACY_TOLERANCE = 0.005


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------

def read_split(source, name):
    """Read <name>.csv from a folder or from a zip file."""

    source = Path(source)
    filename = f"{name}.csv"

    if source.is_dir():
        path = source / filename
        if not path.exists():
            raise SystemExit(f"{filename} was not found in {source}")
        return pd.read_csv(path)

    if zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as archive:
            matches = [n for n in archive.namelist() if n.replace("\\", "/").split("/")[-1] == filename]
            if not matches:
                raise SystemExit(f"{filename} was not found inside {source}")
            with archive.open(matches[0]) as handle:
                return pd.read_csv(handle)

    raise SystemExit(f"{source} is neither a folder nor a zip file")


def load_current(path):
    """Load an existing artifact without printing version warnings."""

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return joblib.load(path)


def accuracy(model, X, y):
    return float((model.predict(X) == y).mean())


def version_warnings(paths):
    """Number of InconsistentVersionWarning raised when loading the files."""

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        for path in paths:
            joblib.load(path)

    return sum(1 for w in caught if issubclass(w.category, InconsistentVersionWarning))


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Re-save the irrigation model with the installed scikit-learn.")
    parser.add_argument("data", help="Smart_Agriculture_Preprocessed zip or folder")
    parser.add_argument("--force", action="store_true",
                        help="replace the model even if it is worse than the current one")
    args = parser.parse_args()

    print(f"scikit-learn installed: {sklearn.__version__}")

    # ---- Data ------------------------------------------------------
    train = read_split(args.data, "train_final")
    validation = read_split(args.data, "validation_final")
    test = read_split(args.data, "test_final")

    with open(FEATURE_ORDER_PATH, "r", encoding="utf-8") as f:
        feature_order = [line.strip() for line in f if line.strip()]

    for name, frame in (("train", train), ("validation", validation), ("test", test)):
        columns = [c for c in frame.columns if c != TARGET]

        if columns != feature_order or TARGET not in frame.columns:
            raise SystemExit(
                f"The {name} file does not have the expected columns.\n"
                f"Expected: {feature_order} + '{TARGET}'\nFound:    {list(frame.columns)}\n"
                "Make sure you are using the Smart_Agriculture_Preprocessed dataset."
            )

        if sorted(frame[TARGET].unique()) != [0, 1]:
            raise SystemExit(f"The target in the {name} file must contain only 0 and 1.")

    print(f"Rows: train {len(train)}, validation {len(validation)}, test {len(test)}")

    X_train, y_train = train[feature_order], train[TARGET]
    X_val, y_val = validation[feature_order], validation[TARGET]
    X_test, y_test = test[feature_order], test[TARGET]

    # ---- Current artifacts ---------------------------------------------
    old_model = load_current(MODEL_PATH)
    encoder = load_current(ENCODER_PATH)
    scaler = load_current(SCALER_PATH)

    # ---- The data must match the saved scaler ----------------------------
    # The numeric columns are standardized, so they should have mean ~0 and std ~1,
    # and converting them back with the saved scaler must give real-world values.
    scaled = train[NUMERICAL_FEATURES]

    if not (scaled.mean().abs() < 0.05).all() or not ((scaled.std() - 1).abs() < 0.05).all():
        raise SystemExit("The numeric columns are not standardized: this is not the preprocessed dataset.")

    raw = pd.DataFrame(scaler.inverse_transform(scaled), columns=NUMERICAL_FEATURES)

    print("\nReal-world value ranges recovered with the saved scaler:")
    for column in NUMERICAL_FEATURES:
        print(f"  {column:9s} min {raw[column].min():7.1f}   max {raw[column].max():7.1f}")

    if raw["MOI"].min() < -1 or raw["MOI"].max() > 101 or raw["humidity"].min() < -1 or raw["humidity"].max() > 101:
        raise SystemExit(
            "Moisture / humidity fall outside 0-100 when converted back with the saved scaler:\n"
            "the data and the scaler do not belong together. Nothing was changed."
        )

    # ---- Train -----------------------------------------------------------
    print("\nTraining (GridSearchCV, cv=3) ...")

    search = GridSearchCV(
        RandomForestClassifier(random_state=42),
        PARAM_GRID,
        cv=3,
        scoring="accuracy",
        n_jobs=-1,
    )
    search.fit(X_train, y_train)

    new_model = search.best_estimator_

    print(f"Best parameters: {search.best_params_}")
    if search.best_params_ != DOCUMENTED_BEST:
        print(f"  (the documented best was {DOCUMENTED_BEST}: results differ slightly from the original run)")

    # ---- Compare with the current model ---------------------------------------
    rows = []
    for label, X, y in (("train", X_train, y_train), ("validation", X_val, y_val), ("test", X_test, y_test)):
        rows.append((label, accuracy(old_model, X, y), accuracy(new_model, X, y)))

    agreement = float((old_model.predict(X_test) == new_model.predict(X_test)).mean())

    print("\nAccuracy        current      new")
    for label, old_acc, new_acc in rows:
        print(f"  {label:10s}   {old_acc:.4f}    {new_acc:.4f}")
    print(f"Predictions in agreement on the test set: {agreement * 100:.2f}%")

    old_test, new_test = rows[2][1], rows[2][2]

    if new_test < old_test - ACCURACY_TOLERANCE and not args.force:
        raise SystemExit(
            f"\nThe new model is worse on the test set ({new_test:.4f} vs {old_test:.4f}). Nothing was changed.\n"
            "Use --force only if you understand why."
        )

    # ---- Back up, then save -------------------------------------------------------
    BACKUP_DIR.mkdir(exist_ok=True)

    for path in (MODEL_PATH, ENCODER_PATH, SCALER_PATH):
        target = BACKUP_DIR / path.name
        if not target.exists():           # keep the very first backup
            shutil.copy2(path, target)

    joblib.dump(new_model, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)    # same object, not refitted: only re-saved
    joblib.dump(scaler, SCALER_PATH)

    print(f"\nSaved the model, encoder and scaler with scikit-learn {sklearn.__version__}.")
    print(f"The previous files were backed up in: {BACKUP_DIR}")

    # ---- Verify -----------------------------------------------------------------------
    count = version_warnings([MODEL_PATH, ENCODER_PATH, SCALER_PATH])
    print(f"\nVersion warnings when loading the saved files: {count}")

    sys.path.insert(0, str(BASE_DIR))

    from models.irrigation_model import predict_ml_irrigation_need

    stage = "Vegetative Growth / Root or Tuber Development"
    dry = predict_ml_irrigation_need("Tomato", "Loam Soil", stage, 15, 32, 40)
    wet = predict_ml_irrigation_need("Tomato", "Loam Soil", stage, 85, 22, 80)

    print(f"Smoke test, dry field (MOI 15):  {dry['status']} ({dry['confidence']}%)")
    print(f"Smoke test, wet field (MOI 85):  {wet['status']} ({wet['confidence']}%)")

    if count != 0 or dry["prediction"] != 1 or wet["prediction"] != 0:
        raise SystemExit("\nVerification FAILED. Restore the files from the backup folder and report this.")

    print("\nVerification passed. Restart the API and the Streamlit app to use the new files.")


if __name__ == "__main__":
    main()
