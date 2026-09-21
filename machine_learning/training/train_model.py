"""
train_from_notebook.py

Same pipeline as Graduation_Final.ipynb (Cell 1 + Cell 2 + Cell 3), packaged as a
script. It writes final_delivery_delay_model.pkl and metadata.pkl next to this file.

"Delayed" follows the notebook's own rule (actual duration > distance*3.2 +
traffic*8) computed on orders that have a delivery duration. The Is_Delayed column
stored in the CSV is ignored unless USE_CSV_IS_DELAYED is set to True below.

Usage:
    python train_from_notebook.py
    python train_from_notebook.py "C:\\path\\to\\Order_delivery.csv"
"""

import sys
import warnings
from pathlib import Path

import joblib
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore", message="Parsing dates in")

# How "delayed" is defined:
#   False -> the notebook's own rule: actual duration > expected duration,
#            expected = distance * 3.2 + traffic_numeric * 8   (default)
#   True  -> use the Is_Delayed column that is stored in the CSV
USE_CSV_IS_DELAYED = False

HERE = Path(__file__).resolve().parent
MODEL_FILENAME = "final_delivery_delay_model.pkl"
META_FILENAME = "metadata.pkl"


def find_csv():
    """Path from the command line, else Order_delivery.csv(.csv) next to this file."""
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists():
            return p
        raise FileNotFoundError(f"CSV not found: {p}")
    for name in ("Order_delivery.csv", "Order_delivery.csv.csv"):
        p = HERE / name
        if p.exists():
            return p
    raise FileNotFoundError(f"Order_delivery.csv not found in {HERE}")


# ==============================================================================
# CELL 1: data preparation + feature engineering (same logic as the notebook)
# ==============================================================================
def prepare_data(csv_path):
    df = pd.read_csv(csv_path)

    # Order time features
    if "Order_Time" in df.columns:
        order_dt = pd.to_datetime(df["Order_Time"], dayfirst=True, errors="coerce")
        df["Order_Hour"] = order_dt.dt.hour.fillna(14).astype(int)
        df["Order_DayOfWeek_Num"] = order_dt.dt.dayofweek.fillna(0).astype(int)
    else:
        if "Order_Hour" not in df.columns:
            df["Order_Hour"] = 14
        if "Order_DayOfWeek_Num" not in df.columns:
            df["Order_DayOfWeek_Num"] = 0

    # Traffic numeric
    if "Traffic_Level" in df.columns:
        traffic_map = {"Low": 1, "Medium": 2, "High": 3}
        df["Traffic_Numeric"] = df["Traffic_Level"].map(traffic_map).fillna(2)
    else:
        df["Traffic_Numeric"] = 2

    # Composite features
    df["Distance_x_Traffic"] = df["Delivery_Distance_km"] * df["Traffic_Numeric"]
    df["Is_Peak_Hour"] = df["Order_Hour"].apply(
        lambda x: 1 if (12 <= x <= 15 or 18 <= x <= 22) else 0
    )
    df["Is_Weekend"] = df["Order_DayOfWeek_Num"].apply(lambda x: 1 if x in [4, 5] else 0)
    df["Traffic_Delay_Risk"] = df["Distance_x_Traffic"] * (1 + 0.5 * df["Is_Peak_Hour"])

    # Target
    target_col = "Is_Delayed"
    n_before = len(df)

    if USE_CSV_IS_DELAYED and target_col in df.columns:
        # label stored in the CSV; rows without a label cannot be used
        df = df.dropna(subset=[target_col]).reset_index(drop=True)
        print("Label source: Is_Delayed column of the CSV")
    else:
        # notebook rule. Orders without a duration (cancelled / in transit)
        # have no outcome, so they are left out.
        df = df.dropna(subset=["Delivery_Duration_Minutes"]).reset_index(drop=True)
        expected_dur = (df["Delivery_Distance_km"] * 3.2) + (df["Traffic_Numeric"] * 8.0)
        df[target_col] = (df["Delivery_Duration_Minutes"] > expected_dur).astype(int)
        print("Label source: notebook rule (duration > distance*3.2 + traffic*8)")

    print(f"Rows without an outcome removed: {n_before - len(df):,} (kept {len(df):,})")

    leakage_and_ids = [
        "Order_ID", "User_ID", "Restaurant_ID", "Driver_ID",
        "Order_Status", "Delivery_Time", "Delivery_Duration_Minutes",
        "Delivery_Speed_kmh", "Order_Time", "Order_Date", "Order_Day",
        "Expected_Duration", target_col,
    ]

    X = df.drop(columns=[c for c in leakage_and_ids if c in df.columns])
    y = df[target_col].astype(int)

    num_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()
    cat_features = X.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), num_features),
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_features),
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )
    return X, y, X_train, X_test, y_train, y_test, preprocessor, num_features, cat_features


def compute_metrics(y_true, y_pred, y_proba):
    return {
        "Accuracy": float(accuracy_score(y_true, y_pred)),
        "Precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "Recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "F1-Score": float(f1_score(y_true, y_pred, zero_division=0)),
        "ROC-AUC": float(roc_auc_score(y_true, y_proba)),
    }


# ==============================================================================
# CELL 2: candidate models + comparison table
# ==============================================================================
def compare_models(preprocessor, X_train, X_test, y_train, y_test):
    models = {
        "Logistic Regression (Baseline)": LogisticRegression(random_state=42, max_iter=1000),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=6),
        "Random Forest (Final Candidate)": RandomForestClassifier(
            random_state=42, n_estimators=150, max_depth=12
        ),
    }
    rows, pipelines = [], {}
    for name, model in models.items():
        pipe = Pipeline([("preprocessor", clone(preprocessor)), ("classifier", model)])
        pipe.fit(X_train, y_train)
        m = compute_metrics(y_test, pipe.predict(X_test), pipe.predict_proba(X_test)[:, 1])
        rows.append({"Model": name, **{k: f"{v * 100:.2f}%" for k, v in m.items()}})
        pipelines[name] = pipe
    print(pd.DataFrame(rows).to_string(index=False))
    return pipelines["Random Forest (Final Candidate)"]


# ==============================================================================
# CELL 3: final model + metadata for Streamlit
# ==============================================================================
def build_metadata(X, num_features, cat_features, metrics, n_train, n_test, baseline):
    defaults = {}
    for col in X.columns:
        if col in num_features:
            defaults[col] = float(X[col].median())
        elif col in cat_features:
            mode = X[col].mode()
            defaults[col] = str(mode.iloc[0]) if len(mode) else "Unknown"
        else:
            defaults[col] = 0

    return {
        "model_file": MODEL_FILENAME,
        "feature_names": X.columns.tolist(),
        "numerical_features": num_features,
        "categorical_features": cat_features,
        "defaults": defaults,
        "categorical_values": {
            c: [str(v) for v in X[c].dropna().unique().tolist()] for c in cat_features
        },
        # (min, max, median) per numeric feature - same shape as the old metadata.pkl
        "numerical_ranges": {
            c: (float(X[c].min()), float(X[c].max()), float(X[c].median()))
            for c in num_features
        },
        "metrics": metrics,
        "baseline_accuracy": float(baseline),
        "n_train": int(n_train),
        "n_test": int(n_test),
    }


def main():
    csv_path = find_csv()
    print(f"Reading: {csv_path}")
    X, y, X_train, X_test, y_train, y_test, pre, num_f, cat_f = prepare_data(csv_path)
    print(f"Train samples: {len(X_train):,} | Test samples: {len(X_test):,} | "
          f"Features: {X.shape[1]}")
    baseline = max(y.mean(), 1 - y.mean())
    print(f"Delayed share in data: {y.mean() * 100:.2f}% "
          f"(always predicting the majority class gives {baseline * 100:.2f}% accuracy)\n")

    final_pipeline = compare_models(pre, X_train, X_test, y_train, y_test)

    metrics = compute_metrics(
        y_test, final_pipeline.predict(X_test), final_pipeline.predict_proba(X_test)[:, 1]
    )

    joblib.dump(final_pipeline, HERE / MODEL_FILENAME)
    meta = build_metadata(X, num_f, cat_f, metrics, len(X_train), len(X_test), baseline)
    joblib.dump(meta, HERE / META_FILENAME)

    # Sanity check: reload the saved files and score again. These two numbers
    # must be identical, otherwise the pkl files and the metadata disagree.
    reloaded = joblib.load(HERE / MODEL_FILENAME)
    reloaded_acc = accuracy_score(y_test, reloaded.predict(X_test))
    saved_acc = joblib.load(HERE / META_FILENAME)["metrics"]["Accuracy"]

    print("\n" + "=" * 60)
    print(f"Saved: {MODEL_FILENAME} and {META_FILENAME} in {HERE}")
    print(f"Accuracy stored in metadata.pkl : {saved_acc * 100:.2f}%")
    print(f"Accuracy of the reloaded model  : {reloaded_acc * 100:.2f}%")
    print("MATCH" if abs(saved_acc - reloaded_acc) < 1e-12 else "MISMATCH - do not deploy")
    print("=" * 60)


if __name__ == "__main__":
    main()
