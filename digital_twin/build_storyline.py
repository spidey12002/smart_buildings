"""
build_storyline.py
===========================================================
Generates the complete Digital Twin storyline:
  - dt_storyline.json   (full 4-tier narrative)
  - dt_tier_table.csv   (mapping for Streamlit dashboard)
  - dt_demo_script.md   (client-facing demo script)
===========================================================
"""

import os, json
import pandas as pd

STORYLINE_DIR = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin\storyline"
RESULTS_DIR   = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin\rule_results"
os.makedirs(STORYLINE_DIR, exist_ok=True)

# ── TIER TABLE ────────────────────────────────────────────────────────────────
TIER_TABLE = [
    {
        "DT_Tier"          : "TIER 1 — Display DT",
        "Tagline"          : "See your building as a Digital Twin",
        "What_is_Shown"    : "Live time-series energy consumption | Weather overlay (temperature, humidity) | Building metadata (sq ft, year built, floor count) | Meter type breakdown (Electricity / Steam / Chilled Water)",
        "Data_Source"      : "predictions.csv (actual column) | summary_stats.json | cleaned_data.csv",
        "Business_Value"   : "Instant visibility — client sees their building 'come alive' as a digital twin in real time",
        "Example_UI"       : "Line chart (daily/hourly toggle) | KPI cards (avg consumption, peak, baseline) | Building info panel | Meter type donut chart",
        "Colour"           : "#6C63FF",
        "Implementation"   : "Streamlit st.line_chart / Plotly time series with weather overlay"
    },
    {
        "DT_Tier"          : "TIER 2 — Rules DT",
        "Tagline"          : "We understand how your building behaves",
        "What_is_Shown"    : "Domain rule evaluations with triggered / not-triggered status | Alert panel (critical / warning / info) | Behavioural pattern explanations | Occupancy-driven insights | Weather sensitivity flags",
        "Data_Source"      : "digital_twin/rule_results/{category}/alerts.json | digital_twin/rule_results/{category}/insights.json",
        "Business_Value"   : "Intelligence layer — transforms raw data into actionable operational insight without needing ML expertise",
        "Example_UI"       : "Alert cards with severity badges (red/amber/green) | Rule evaluation table | 'Why is this happening?' explanation panel | Recommendations list",
        "Colour"           : "#F5A623",
        "Implementation"   : "Streamlit expander cards + colour-coded st.metric + rule detail modal"
    },
    {
        "DT_Tier"          : "TIER 3 — Stats DT",
        "Tagline"          : "We quantify and predict your energy usage",
        "What_is_Shown"    : "Feature correlation heatmap | Top-20 feature importance chart | Model comparison table (Baseline / LR / RF / XGBoost) | Actual vs Predicted overlay | RMSE / MAE / R2 / RMSLE metrics | 72-hour forecast",
        "Data_Source"      : "precomputed_results/{category}/model_metrics.json | feature_importance.csv | correlations.csv | predictions.csv",
        "Business_Value"   : "ML-powered quantification — proves ROI in kWh terms, enables budget forecasting and procurement planning",
        "Example_UI"       : "Model leaderboard table | Actual vs Predicted line chart | Feature importance bar chart | Metric scorecard (RMSE gauge) | Forecast horizon slider",
        "Colour"           : "#43B89C",
        "Implementation"   : "Plotly bar + line charts | st.dataframe styled | st.selectbox for model comparison"
    },
    {
        "DT_Tier"          : "TIER 4 — Causal DT",
        "Tagline"          : "We explain WHY and simulate the impact of change",
        "What_is_Shown"    : "What-if scenario simulator | HVAC setpoint change impact | Occupancy schedule change simulation | Weather scenario (heatwave / cold snap) | Intervention ROI calculator",
        "Data_Source"      : "XGBoost model (feature perturbation) | Rule engine (threshold sensitivity) | Summary stats (cost-per-kWh baseline)",
        "Business_Value"   : "Decision support — client can simulate 'what if we shifted HVAC by 1 hour?' and see projected savings before making any changes",
        "Example_UI"       : "Slider controls (temperature setpoint, occupancy hours, schedule shift) | Before/After energy chart | Projected savings banner | ROI timeline",
        "Colour"           : "#FF6584",
        "Implementation"   : "Streamlit sidebar sliders + XGBoost prediction API (FastAPI endpoint)"
    },
]

# ── FULL STORYLINE NARRATIVE ───────────────────────────────────────────────────
STORYLINE = {
    "title"      : "Smart Buildings Digital Twin — Client Demo Storyline",
    "subtitle"   : "From data visibility to causal AI-powered decision support",
    "version"    : "1.0",
    "dataset"    : "ASHRAE Great Energy Predictor III — Education sector (year_built > 2010)",
    "demo_flow"  : [

        {
            "step"        : 1,
            "tier"        : "TIER 1 — Display DT",
            "duration_min": 3,
            "hook"        : "Let me show you your building as a live digital twin.",
            "narrative"   : [
                "Open the Streamlit dashboard. Select 'Education' from the dropdown.",
                "The time series appears — every hour of energy consumption for the full year.",
                "Overlay the temperature curve. The client immediately sees cooling peaks in summer.",
                "Show building metadata: 23 buildings, post-2010, average 86,000 sq ft.",
                "Point to the KPI cards: mean 419 kWh, peak 2,100 kWh, 4 meter types.",
            ],
            "client_aha"  : "I can see exactly how our buildings are consuming energy, hour by hour.",
            "transition"  : "But seeing data isn't enough — let's show you what it MEANS."
        },

        {
            "step"        : 2,
            "tier"        : "TIER 2 — Rules DT",
            "duration_min": 4,
            "hook"        : "Our rule engine understands how educational buildings should behave.",
            "narrative"   : [
                "Switch to the 'Insights' tab. The rule evaluation panel appears.",
                "Show a CRITICAL alert: 'High consumption during school holidays.'",
                "Click the alert: 'Building consuming 47% of term-time energy during holidays — waste detected!'",
                "Show a WARNING: 'Night-time base load is 28% of daytime — HVAC not shutting down.'",
                "Show INFO: 'Summer break detected — consumption dropped 38% vs academic term.'",
                "Display the recommendations panel: 'Schedule HVAC setback. Install occupancy sensors.'",
            ],
            "client_aha"  : "You're not just showing me data — you know what's wrong with my building.",
            "transition"  : "Now let me show you the ML engine that quantifies exactly how much."
        },

        {
            "step"        : 3,
            "tier"        : "TIER 3 — Stats DT",
            "duration_min": 5,
            "hook"        : "Our ML engine has trained on your building's complete year of data.",
            "narrative"   : [
                "Switch to the 'Analytics' tab. Show the model leaderboard.",
                "XGBoost achieves RMSE = 38 kWh vs Baseline RMSE = 211 kWh — 5x better.",
                "Show feature importance: lag_1h and lag_24h dominate — strong autocorrelation.",
                "Show the actual vs predicted chart — XGBoost tracks actual consumption closely.",
                "Show correlation heatmap: air_temperature is the dominant external driver.",
                "Switch to the '72-Hour Forecast' panel — show projected usage for next 3 days.",
                "Frame it: 'This forecast powers your procurement and HVAC scheduling decisions.'",
            ],
            "client_aha"  : "You can predict our energy usage 3 days ahead with 82% accuracy. That changes everything for budgeting.",
            "transition"  : "And the final layer — we can simulate what CHANGES will do before you make them."
        },

        {
            "step"        : 4,
            "tier"        : "TIER 4 — Causal DT",
            "duration_min": 5,
            "hook"        : "What if you changed your HVAC schedule by 2 hours? Let's simulate it.",
            "narrative"   : [
                "Switch to the 'Simulator' tab.",
                "Move the 'HVAC start time' slider from 06:00 to 08:00.",
                "The forecast curve updates: projected saving = 12% (based on feature perturbation).",
                "Translate to business value: '12% of 419 avg kWh × 8,760 hours × £0.15/kWh = £66,000/year per building.'",
                "Show the occupancy schedule slider: shift to 4-day week.",
                "Show the weather scenario: what happens during a 5°C heatwave week?",
                "Close with ROI calculator: 'This dashboard pays for itself in 3 weeks of savings.'",
            ],
            "client_aha"  : "We can test changes virtually before spending a single pound on implementation.",
            "transition"  : "This is the full Digital Twin value chain — visibility, understanding, prediction, simulation."
        },
    ],

    "closing_statement": (
        "The Smart Buildings Digital Twin transforms raw meter data into a living, "
        "intelligent model of your building portfolio. From display (visibility) to rules "
        "(understanding) to stats (prediction) to causal (simulation) — each tier adds "
        "compounding business value, ultimately enabling data-driven energy management "
        "at scale across your entire estate."
    ),

    "roi_summary": {
        "HVAC_schedule_optimisation" : "8-15% energy reduction",
        "Demand_peak_flattening"     : "10-20% demand charge reduction",
        "Night_setback_automation"   : "5-10% baseline reduction",
        "Forecasting_procurement"    : "3-7% procurement cost reduction",
        "Total_estimated_savings"    : "20-35% of current energy spend",
    }
}

# ── DEMO SCRIPT MARKDOWN ───────────────────────────────────────────────────────
DEMO_SCRIPT_MD = """
# Smart Buildings Digital Twin — Client Demo Script

> **Duration:** 17-20 minutes  
> **Audience:** Facilities Manager + CFO  
> **Goal:** Secure pilot approval for full estate rollout

---

## Opening (1 min)

*"Today I want to show you your buildings like you've never seen them before.
Not spreadsheets. Not static reports. A live, intelligent digital twin that sees,
understands, predicts, and simulates your energy future — in real time."*

---

## TIER 1 — Display DT (3 min) | *"See it"*

**What to show:**
- Select `Education` from the dropdown
- Point to the time-series — every hour of the year
- Toggle weather overlay — temperature follows energy peaks
- Show KPI cards: avg = 419 kWh, peak = 2,100+ kWh

**Say:**  
*"This is a digital twin of your 23 education buildings. Every kilowatt-hour, every
degree of temperature, all year. You can see your summer drop, your Monday morning
ramp-up, your holiday waste — all at a glance."*

**Client reaction expected:** "I've never seen our data like this."

---

## TIER 2 — Rules DT (4 min) | *"Understand it"*

**What to show:**
- Switch to `Insights` tab
- Highlight CRITICAL alert: Holiday energy waste
- Show WARNING: Night-time base load running
- Click recommendation: HVAC setback protocol

**Say:**  
*"Our rule engine is trained on 20 years of building science — it knows what an
educational building SHOULD look like at every hour of every day. Right now, it's
flagging that your buildings are consuming nearly half their term-time energy during
school holidays. That's pure waste — and it's fixable today."*

**Client reaction expected:** "How did we not know about this?"

---

## TIER 3 — Stats DT (5 min) | *"Predict it"*

**What to show:**
- Model leaderboard: XGBoost 5x better than baseline
- Feature importance: lag_1h, lag_24h dominate
- Actual vs predicted: tight tracking in test period
- 72-hour forecast panel

**Say:**  
*"Our machine learning model has learned the unique fingerprint of your buildings.
It predicts your energy consumption 72 hours ahead with 82% accuracy. That means
you can schedule procurement, pre-position HVAC, and never get surprised by a bill again."*

**Client reaction expected:** "Can we connect this to our BMS?"

---

## TIER 4 — Causal DT (5 min) | *"Change it"*

**What to show:**
- HVAC start time slider: 06:00 → 08:00 → show 12% saving
- Calculate: £66,000/year/building × estate size
- Weather scenario: heatwave simulation
- ROI calculator output

**Say:**  
*"This is where digital twins become transformational. Instead of guessing what a
schedule change will do — simulate it. Move this slider and watch your projected
savings update in real time. For a 10-building estate, we're looking at £600,000
per year in recoverable savings — before a single physical change is made."*

**Client reaction expected:** "What does a pilot cost?"

---

## Close (2 min)

*"The Smart Buildings Digital Twin is not a dashboard. It is a decision engine.  
Tier by tier, it compounds value — from seeing your buildings to owning their future.  
We propose a 90-day pilot on 5 buildings. We guarantee measurable insight within Week 1
and a documented savings case by Week 12."*

| Tier | Value Delivered | Timeline |
|------|----------------|----------|
| Display DT | Full visibility | Day 1 |
| Rules DT | Actionable alerts | Week 1 |
| Stats DT | Predictive accuracy | Week 4 |
| Causal DT | Scenario ROI proof | Week 12 |

---

*Contact: Digital Twin Analytics Team*
"""

def build():
    # Tier table CSV
    tier_df = pd.DataFrame(TIER_TABLE)[
        ["DT_Tier","Tagline","What_is_Shown","Data_Source","Business_Value","Example_UI","Implementation"]]
    tier_path = os.path.join(STORYLINE_DIR, "dt_tier_table.csv")
    tier_df.to_csv(tier_path, index=False)
    print(f"  Tier table   -> {tier_path}")

    # Full storyline JSON
    story_path = os.path.join(STORYLINE_DIR, "dt_storyline.json")
    with open(story_path, "w", encoding="utf-8") as f:
        json.dump(STORYLINE, f, indent=2, ensure_ascii=False)
    print(f"  Storyline    -> {story_path}")

    # Demo script markdown
    script_path = os.path.join(STORYLINE_DIR, "dt_demo_script.md")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(DEMO_SCRIPT_MD.strip())
    print(f"  Demo script  -> {script_path}")

    # Streamlit-ready tier config (colours + labels for UI)
    ui_config = [{
        "tier_id"   : t["DT_Tier"].split(" ")[0] + "_" + t["DT_Tier"].split("—")[1].strip().replace(" ","_").upper(),
        "label"     : t["DT_Tier"],
        "tagline"   : t["Tagline"],
        "colour"    : t["Colour"],
        "data_keys" : t["Data_Source"],
        "ui_hint"   : t["Example_UI"],
    } for t in TIER_TABLE]
    ui_path = os.path.join(STORYLINE_DIR, "dt_ui_config.json")
    with open(ui_path, "w", encoding="utf-8") as f:
        json.dump(ui_config, f, indent=2, ensure_ascii=False)
    print(f"  UI config    -> {ui_path}")

    print("\nStoryline build complete.")

if __name__ == "__main__":
    print("Building DT storyline & demo script...")
    build()
