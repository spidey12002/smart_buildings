"""
rule_engine.py
===========================================================
Evaluates domain rules against precomputed ML results for
each primary_use category and generates:
  - alerts.json    (triggered rule alerts)
  - insights.json  (all rule evaluations with scores)
===========================================================
"""

import os, json
import pandas as pd
import numpy as np

PRECOMPUTED_DIR = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\precomputed_results"
RULES_DIR       = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin\rules"
RESULTS_DIR     = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin\rule_results"
os.makedirs(RESULTS_DIR, exist_ok=True)


def load_category_data(cat: str) -> dict:
    """Load all precomputed files for a category."""
    base = os.path.join(PRECOMPUTED_DIR, cat)
    data = {}
    try:
        data["summary"]     = json.load(open(os.path.join(base, "summary_stats.json"), encoding="utf-8"))
        data["metrics"]     = json.load(open(os.path.join(base, "model_metrics.json"), encoding="utf-8"))
        data["predictions"] = pd.read_csv(os.path.join(base, "predictions.csv"), parse_dates=["timestamp"])
        data["correlations"]= pd.read_csv(os.path.join(base, "correlations.csv"))
        data["feature_imp"] = pd.read_csv(os.path.join(base, "feature_importance.csv"))
        data["cleaned"]     = pd.read_csv(os.path.join(base, "cleaned_data.csv"), parse_dates=["timestamp"])
    except Exception as e:
        print(f"  Warning loading {cat}: {e}")
    return data


def compute_stats(data: dict) -> dict:
    """Extract behavioural statistics from predictions + cleaned sample."""
    stats = {}
    pred  = data.get("predictions", pd.DataFrame())
    clean = data.get("cleaned",     pd.DataFrame())
    summ  = data.get("summary",     {})
    corrs = data.get("correlations", pd.DataFrame())

    if pred.empty and clean.empty:
        return stats

    df = pred if not pred.empty else clean

    if "timestamp" in df.columns:
        df = df.copy()
        df["hour"]      = df["timestamp"].dt.hour
        df["dayofweek"] = df["timestamp"].dt.dayofweek
        df["month"]     = df["timestamp"].dt.month
        df["is_weekend"]= (df["dayofweek"] >= 5).astype(int)
        df["is_night"]  = df["hour"].apply(lambda h: 1 if h < 6 or h >= 22 else 0)
        df["is_business"]= df.apply(
            lambda r: 1 if r["dayofweek"] < 5 and 8 <= r["hour"] < 18 else 0, axis=1)

        col = "meter_reading" if "meter_reading" in df.columns else "actual"
        if col in df.columns:
            avg   = df[col].mean()
            stats["avg_reading"]          = round(float(avg), 4)
            stats["max_reading"]          = round(float(df[col].max()), 4)
            stats["min_reading"]          = round(float(df[col].min()), 4)
            stats["peak_to_mean_ratio"]   = round(float(df[col].max() / avg) if avg else 0, 3)

            night  = df[df["is_night"] == 1][col].mean()
            day    = df[df["is_night"] == 0][col].mean()
            stats["night_to_day_ratio"]   = round(float(night / day) if day else 0, 3)

            wkend  = df[df["is_weekend"] == 1][col].mean()
            wkday  = df[df["is_weekend"] == 0][col].mean()
            stats["weekend_to_weekday_ratio"] = round(float(wkend / wkday) if wkday else 0, 3)

            biz   = df[df["is_business"] == 1][col].mean()
            total_biz = df[df["is_business"] == 1][col].sum()
            total_all = df[col].sum()
            stats["business_hours_pct"]   = round(float(total_biz / total_all) if total_all else 0, 3)

            # Hourly avg — find peak hour
            hourly = df.groupby("hour")[col].mean()
            stats["peak_hour"]            = int(hourly.idxmax())
            stats["peak_hour_value"]      = round(float(hourly.max()), 4)

            # Monthly
            monthly = df.groupby("month")[col].mean()
            if 7 in monthly.index and 8 in monthly.index:
                summer = (monthly.get(7, 0) + monthly.get(8, 0)) / 2
                winter_months = [m for m in [12, 1, 2] if m in monthly.index]
                winter = np.mean([monthly[m] for m in winter_months]) if winter_months else summer
                stats["summer_to_winter_ratio"] = round(float(summer / winter) if winter else 1.0, 3)

    # Temperature correlation from correlations.csv
    if not corrs.empty and "feature" in corrs.columns:
        corr_col = "correlation_with_meter_reading"
        air_row  = corrs[corrs["feature"] == "air_temperature"]
        if not air_row.empty:
            stats["air_temperature_correlation"] = round(
                float(air_row[corr_col].values[0]), 4)
        dew_row  = corrs[corrs["feature"] == "dew_temperature"]
        if not dew_row.empty:
            stats["dew_temperature_correlation"] = round(
                float(dew_row[corr_col].values[0]), 4)

    # Best model from metrics
    metrics = data.get("metrics", [])
    if metrics:
        valid = [m for m in metrics if m.get("RMSE") is not None]
        if valid:
            best = min(valid, key=lambda m: m["RMSE"])
            stats["best_model"]      = best["model"]
            stats["best_model_rmse"] = best["RMSE"]
            stats["best_model_r2"]   = best.get("R2")

    # From summary_stats
    stats["row_count"]           = summ.get("row_count")
    stats["unique_buildings"]    = summ.get("unique_buildings")
    stats["mean_meter_reading"]  = summ.get("mean_meter_reading")
    stats["max_meter_reading"]   = summ.get("max_meter_reading")
    stats["avg_air_temperature"] = summ.get("avg_air_temperature")

    return stats


def evaluate_rule(rule: dict, stats: dict) -> dict:
    """Evaluate a single rule against computed stats. Returns evaluation result."""
    rule_id   = rule["rule_id"]
    metric    = rule.get("metric")
    threshold = rule.get("threshold")
    severity  = rule.get("severity", "info")
    result    = {
        "rule_id"    : rule_id,
        "name"       : rule["name"],
        "severity"   : severity,
        "tier"       : rule.get("tier", "RULES_DT"),
        "triggered"  : False,
        "value"      : None,
        "threshold"  : threshold,
        "message"    : "",
        "recommendation": rule.get("recommendation", ""),
    }

    if metric not in stats or stats[metric] is None:
        result["message"] = f"Metric '{metric}' not available in data."
        return result

    value     = stats[metric]
    result["value"] = value

    # Evaluate trigger
    triggered = False
    if isinstance(threshold, dict):
        # Range check
        lo, hi = threshold.get("min", -np.inf), threshold.get("max", np.inf)
        triggered = not (lo <= value <= hi)
    elif threshold is not None:
        triggered = value > threshold

    result["triggered"] = triggered

    # Build message from demo_alert template
    alert_tmpl = rule.get("demo_alert", "")
    try:
        msg = alert_tmpl.format(
            value=value,
            threshold_pct=int(threshold * 100) if isinstance(threshold, float) else threshold
        )
    except Exception:
        msg = alert_tmpl
    result["message"] = msg

    return result


def evaluate_category(cat: str) -> dict:
    """Run all rules for a category, return full evaluation results."""
    print(f"  Evaluating: {cat}")

    # Load rules
    rules_path = os.path.join(RULES_DIR, f"{cat}_rules.json")
    if not os.path.exists(rules_path):
        return {"error": f"Rules file not found: {rules_path}"}
    rules_def = json.load(open(rules_path, encoding="utf-8"))

    # Load data + compute stats
    data  = load_category_data(cat)
    stats = compute_stats(data)

    # Flatten all rules
    all_rules = []
    for section in ["behavioral_rules","efficiency_rules","weather_sensitivity_rules","alert_rules"]:
        all_rules.extend(rules_def.get(section, []))

    evaluations = [evaluate_rule(r, stats) for r in all_rules]
    alerts      = [e for e in evaluations if e["triggered"]]

    result = {
        "category"          : cat,
        "primary_use_label" : rules_def.get("primary_use", cat),
        "operating_hours"   : rules_def.get("operating_hours", ""),
        "stats"             : stats,
        "total_rules"       : len(evaluations),
        "triggered_count"   : len(alerts),
        "critical_count"    : sum(1 for a in alerts if a["severity"] == "critical"),
        "warning_count"     : sum(1 for a in alerts if a["severity"] == "warning"),
        "info_count"        : sum(1 for a in alerts if a["severity"] == "info"),
        "evaluations"       : evaluations,
        "alerts"            : alerts,
    }

    # Save
    cat_results_dir = os.path.join(RESULTS_DIR, cat)
    os.makedirs(cat_results_dir, exist_ok=True)

    with open(os.path.join(cat_results_dir, "insights.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False, default=str)

    alert_summary = [{
        "rule_id"       : a["rule_id"],
        "name"          : a["name"],
        "severity"      : a["severity"],
        "tier"          : a["tier"],
        "value"         : a["value"],
        "threshold"     : a["threshold"],
        "message"       : a["message"],
        "recommendation": a["recommendation"],
    } for a in alerts]

    with open(os.path.join(cat_results_dir, "alerts.json"), "w", encoding="utf-8") as f:
        json.dump(alert_summary, f, indent=2, ensure_ascii=False, default=str)

    print(f"    -> {len(evaluations)} rules | {len(alerts)} triggered "
          f"({result['critical_count']} critical, {result['warning_count']} warning)")
    return result


def run_all(categories: list) -> dict:
    """Evaluate rules for all categories. Returns summary."""
    print("Running Rule Engine...\n")
    all_results = {}
    for cat in categories:
        all_results[cat] = evaluate_category(cat)

    # Master summary
    import pandas as pd
    rows = []
    for cat, r in all_results.items():
        if "error" in r: continue
        s = r.get("stats", {})
        rows.append({
            "category"              : cat,
            "total_rules"           : r["total_rules"],
            "triggered"             : r["triggered_count"],
            "critical"              : r["critical_count"],
            "warnings"              : r["warning_count"],
            "best_model"            : s.get("best_model"),
            "best_rmse"             : s.get("best_model_rmse"),
            "peak_to_mean_ratio"    : s.get("peak_to_mean_ratio"),
            "night_to_day_ratio"    : s.get("night_to_day_ratio"),
            "weekend_weekday_ratio" : s.get("weekend_to_weekday_ratio"),
            "air_temp_correlation"  : s.get("air_temperature_correlation"),
        })
    df = pd.DataFrame(rows)
    summary_path = os.path.join(RESULTS_DIR, "rule_engine_summary.csv")
    df.to_csv(summary_path, index=False)
    print(f"\nMaster summary saved: {summary_path}")
    print(df.to_string(index=False))
    return all_results


CATEGORIES = [
    "education","office","healthcare","retail","parking",
    "lodging_residential","food_sales_and_service",
    "entertainment_public_assembly","public_services",
]

if __name__ == "__main__":
    run_all(CATEGORIES)
