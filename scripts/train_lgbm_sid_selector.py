#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, sort_keys=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=Path, default=Path("/root/gsm8k_single_language_experiment/swh_Latn"))
    ap.add_argument("--num-boost-round", type=int, default=600)
    ap.add_argument("--learning-rate", type=float, default=0.03)
    ap.add_argument("--num-leaves", type=int, default=64)
    ap.add_argument("--min-data-in-leaf", type=int, default=200)
    ap.add_argument("--feature-fraction", type=float, default=0.85)
    ap.add_argument("--bagging-fraction", type=float, default=0.85)
    ap.add_argument("--bagging-freq", type=int, default=1)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--num-threads", type=int, default=16)
    ap.add_argument("--exclude-level0", action="store_true")
    args = ap.parse_args()

    out_dir = args.out_dir
    variants = pd.read_parquet(out_dir / "variants" / "variants.parquet")
    eval_df = pd.read_parquet(out_dir / "eval" / "eval_results.parquet")
    merged = variants[["variant_row", "variant_id", "split", "source_idx", "variant_idx"]].merge(
        eval_df[["variant_row", "correct"]], on="variant_row", how="left"
    )
    if merged["correct"].isna().any():
        raise RuntimeError("eval correctness is missing; run merge-eval first")

    sids_meta = json.loads((out_dir / "rqvae" / "sids_meta.json").read_text())
    sid_shape = tuple(sids_meta["shape"])
    sids = np.memmap(sids_meta["memmap"], dtype=np.uint16, mode="r", shape=sid_shape)
    x_all = np.asarray(sids, dtype=np.int16).reshape(sid_shape[0], sid_shape[1] * sid_shape[2])

    feature_names = []
    keep_cols = []
    col = 0
    for layer in range(sid_shape[1]):
        for level in range(sid_shape[2]):
            name = f"L{layer}_K{level}"
            if args.exclude_level0 and level == 0:
                col += 1
                continue
            feature_names.append(name)
            keep_cols.append(col)
            col += 1
    x_all = x_all[:, keep_cols]

    y_all = merged["correct"].astype(np.int8).to_numpy()
    train_mask = merged["split"].to_numpy() == "train"
    test_mask = merged["split"].to_numpy() == "test"

    x_train = x_all[train_mask]
    y_train = y_all[train_mask]
    x_test = x_all[test_mask]
    y_test = y_all[test_mask]
    test_meta = merged[test_mask].reset_index(drop=True)

    cat_features = list(range(x_all.shape[1]))
    train_data = lgb.Dataset(
        x_train,
        label=y_train,
        feature_name=feature_names,
        categorical_feature=cat_features,
        free_raw_data=False,
    )
    params = {
        "objective": "binary",
        "metric": ["binary_logloss", "auc"],
        "learning_rate": args.learning_rate,
        "num_leaves": args.num_leaves,
        "min_data_in_leaf": args.min_data_in_leaf,
        "feature_fraction": args.feature_fraction,
        "bagging_fraction": args.bagging_fraction,
        "bagging_freq": args.bagging_freq,
        "seed": args.seed,
        "num_threads": args.num_threads,
        "verbosity": -1,
        "force_col_wise": True,
    }
    booster = lgb.train(params, train_data, num_boost_round=args.num_boost_round)

    train_pred = booster.predict(x_train)
    test_pred = booster.predict(x_test)
    train_auc = None
    test_auc = None
    try:
        from sklearn.metrics import roc_auc_score

        train_auc = float(roc_auc_score(y_train, train_pred))
        test_auc = float(roc_auc_score(y_test, test_pred))
    except Exception:
        pass

    pred_df = test_meta.copy()
    pred_df["lgbm_score"] = test_pred
    selected_rows = []
    for source_idx, group in pred_df.groupby("source_idx", sort=True):
        best = group.sort_values(["lgbm_score", "variant_idx"], ascending=[False, True]).iloc[0]
        selected_rows.append(
            {
                "source_idx": int(source_idx),
                "selected_variant_row": int(best["variant_row"]),
                "selected_variant_idx": int(best["variant_idx"]),
                "lgbm_score": float(best["lgbm_score"]),
                "correct": bool(best["correct"]),
            }
        )
    selected = pd.DataFrame(selected_rows)

    original = pred_df[pred_df["variant_idx"] == 0]
    analysis_dir = out_dir / ("analysis_lgbm_no_level0" if args.exclude_level0 else "analysis_lgbm")
    analysis_dir.mkdir(parents=True, exist_ok=True)
    pred_df.to_parquet(analysis_dir / "test_variant_scores.parquet", index=False)
    pred_df.to_csv(analysis_dir / "test_variant_scores.csv", index=False)
    selected.to_parquet(analysis_dir / "test_selection_lgbm.parquet", index=False)
    selected.to_csv(analysis_dir / "test_selection_lgbm.csv", index=False)

    importance = pd.DataFrame(
        {
            "feature": feature_names,
            "gain": booster.feature_importance(importance_type="gain"),
            "split": booster.feature_importance(importance_type="split"),
        }
    ).sort_values(["gain", "split"], ascending=False)
    importance.to_csv(analysis_dir / "feature_importance.csv", index=False)

    summary = {
        "exclude_level0": bool(args.exclude_level0),
        "num_features": int(x_all.shape[1]),
        "train_rows": int(x_train.shape[0]),
        "test_variant_rows": int(x_test.shape[0]),
        "test_source_rows": int(selected.shape[0]),
        "train_accuracy_at_0_5": float(((train_pred >= 0.5).astype(np.int8) == y_train).mean()),
        "test_variant_accuracy_at_0_5": float(((test_pred >= 0.5).astype(np.int8) == y_test).mean()),
        "train_auc": train_auc,
        "test_auc": test_auc,
        "test_all_variant_accuracy": float(y_test.mean()),
        "test_original_accuracy": float(original["correct"].mean()),
        "test_selected_accuracy": float(selected["correct"].mean()),
        "params": params,
        "num_boost_round": int(args.num_boost_round),
        "outputs": {
            "test_variant_scores": str(analysis_dir / "test_variant_scores.parquet"),
            "test_selection_lgbm": str(analysis_dir / "test_selection_lgbm.parquet"),
            "feature_importance": str(analysis_dir / "feature_importance.csv"),
        },
    }
    write_json(analysis_dir / "analysis_lgbm_summary.json", summary)
    booster.save_model(str(analysis_dir / "model.txt"))
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
