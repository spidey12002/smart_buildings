"""
run_digital_twin.py
===========================================================
Master orchestrator for the Digital Twin intelligence layer.
Runs in sequence:
  1. generate_rules.py   — create domain rule JSON files
  2. rule_engine.py      — evaluate rules vs precomputed data
  3. build_storyline.py  — generate DT storyline + tier table
===========================================================
"""

import os, sys, time

sys.path.insert(0, os.path.dirname(__file__))
os.environ["PYTHONIOENCODING"] = "utf-8"

CATEGORIES = [
    "education","office","healthcare","retail","parking",
    "lodging_residential","food_sales_and_service",
    "entertainment_public_assembly","public_services",
]

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def main():
    t_total = time.time()
    print("=" * 60)
    print("  DIGITAL TWIN INTELLIGENCE LAYER — BUILD START")
    print("=" * 60)

    # ── STEP 1: Generate Rules ─────────────────────────────────────────────
    section("STEP 1/3 — Generating Domain Intelligence Rules")
    t0 = time.time()
    from generate_rules import main as gen_rules
    gen_rules()
    print(f"  Done in {time.time()-t0:.1f}s")

    # ── STEP 2: Run Rule Engine ────────────────────────────────────────────
    section("STEP 2/3 — Evaluating Rules Against Precomputed Results")
    t0 = time.time()
    from rule_engine import run_all
    results = run_all(CATEGORIES)
    print(f"  Done in {time.time()-t0:.1f}s")

    # ── STEP 3: Build Storyline ────────────────────────────────────────────
    section("STEP 3/3 — Building DT Storyline & Demo Script")
    t0 = time.time()
    from build_storyline import build
    build()
    print(f"  Done in {time.time()-t0:.1f}s")

    # ── Final summary ──────────────────────────────────────────────────────
    section("BUILD COMPLETE")
    print(f"  Total time: {time.time()-t_total:.1f}s\n")

    base = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin"
    print("  Output directory structure:")
    for root, dirs, files in os.walk(base):
        level = root.replace(base, "").count(os.sep)
        indent = "    " + "  " * level
        folder = os.path.basename(root)
        print(f"{indent}{folder}/")
        sub = "    " + "  " * (level + 1)
        for f in sorted(files):
            size = os.path.getsize(os.path.join(root, f))
            print(f"{sub}{f}  ({size/1024:.1f} KB)")

    print("\n  Key files for Streamlit dashboard:")
    key_files = [
        ("Rules (per category)"        , "digital_twin/rules/*.json"),
        ("Alerts (per category)"       , "digital_twin/rule_results/*/alerts.json"),
        ("Full insights (per category)", "digital_twin/rule_results/*/insights.json"),
        ("Rule engine summary"         , "digital_twin/rule_results/rule_engine_summary.csv"),
        ("DT tier table"               , "digital_twin/storyline/dt_tier_table.csv"),
        ("DT storyline"                , "digital_twin/storyline/dt_storyline.json"),
        ("Streamlit UI config"         , "digital_twin/storyline/dt_ui_config.json"),
        ("Client demo script"          , "digital_twin/storyline/dt_demo_script.md"),
    ]
    for label, path in key_files:
        print(f"    {label:<35} -> {path}")

if __name__ == "__main__":
    main()
