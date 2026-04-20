"""
generate_rules.py
===========================================================
Generates domain-intelligence rule JSON files for all 9
primary_use categories into digital_twin/rules/

Each rule has:
  rule_id, name, description, condition, threshold,
  severity, recommendation, tier
===========================================================
"""

import json, os

RULES_DIR = r"C:\Users\Sweta.Singh\Downloads\project\smart_buildings\digital_twin\rules"
os.makedirs(RULES_DIR, exist_ok=True)

# ── Shared rule templates reused across categories ─────────────────────────
def night_base_load_rule(threshold_pct=30):
    return {
        "rule_id": "NIGHT_BASE_LOAD",
        "name": "High Night-Time Base Load",
        "description": "Average consumption between 11PM-5AM exceeds threshold % of daily mean.",
        "condition": "avg_night_reading / avg_day_reading > threshold",
        "threshold": threshold_pct / 100,
        "metric": "night_to_day_ratio",
        "severity": "warning",
        "tier": "RULES_DT",
        "recommendation": "Investigate equipment left running overnight. Schedule HVAC setback.",
        "demo_alert": "Building is consuming {value}% of daytime energy overnight."
    }

def weekend_anomaly_rule(expected_drop_pct=60):
    return {
        "rule_id": "WEEKEND_ANOMALY",
        "name": "Weekend Consumption Anomaly",
        "description": f"Weekend usage should be <{100-expected_drop_pct}% of weekday usage for this building type.",
        "condition": "avg_weekend_reading / avg_weekday_reading > threshold",
        "threshold": (100 - expected_drop_pct) / 100,
        "metric": "weekend_to_weekday_ratio",
        "severity": "info",
        "tier": "RULES_DT",
        "recommendation": "Review weekend HVAC schedules and unoccupied equipment.",
        "demo_alert": "Weekend usage is {value}% of weekday — expected <{threshold_pct}%."
    }

def temp_correlation_rule(min_correlation=0.3):
    return {
        "rule_id": "TEMP_CORRELATION",
        "name": "Weather Sensitivity Check",
        "description": "Correlation between air_temperature and meter_reading reveals cooling/heating dependency.",
        "condition": "abs(corr_air_temp_meter) > threshold",
        "threshold": min_correlation,
        "metric": "air_temperature_correlation",
        "severity": "info",
        "tier": "STATS_DT",
        "recommendation": "Optimize HVAC based on temperature forecast to reduce reactive energy spikes.",
        "demo_alert": "Energy use is {value:.0%} correlated with outdoor temperature."
    }

def peak_to_mean_rule(threshold=3.0):
    return {
        "rule_id": "PEAK_TO_MEAN",
        "name": "Demand Spike Detection",
        "description": "Max meter reading exceeds threshold × mean — indicates uncontrolled demand peaks.",
        "condition": "max_meter_reading / mean_meter_reading > threshold",
        "threshold": threshold,
        "metric": "peak_to_mean_ratio",
        "severity": "critical",
        "tier": "RULES_DT",
        "recommendation": "Implement demand response: stagger HVAC start, shift non-critical loads.",
        "demo_alert": "Peak demand is {value:.1f}x the average — opportunity to flatten load curve."
    }

def low_occupancy_high_load_rule(hour_start=22, hour_end=5, threshold_pct=25):
    return {
        "rule_id": "LOW_OCC_HIGH_LOAD",
        "name": "High Consumption During Low-Occupancy Hours",
        "description": f"Consumption from {hour_start}:00-{hour_end:02d}:00 exceeds {threshold_pct}% of daily average.",
        "condition": "avg_offhours_reading / avg_reading > threshold",
        "threshold": threshold_pct / 100,
        "metric": "offhours_to_avg_ratio",
        "severity": "warning",
        "tier": "RULES_DT",
        "recommendation": "Configure occupancy sensors and timer-based shutdowns.",
        "demo_alert": "Significant energy consumed when building should be empty ({value:.0%} of daily avg)."
    }

def seasonal_dependency_rule():
    return {
        "rule_id": "SEASONAL_DEPENDENCY",
        "name": "Seasonal Energy Pattern",
        "description": "Summer (Jun-Aug) vs Winter (Dec-Feb) consumption ratio identifies cooling vs heating dominance.",
        "condition": "abs(avg_summer - avg_winter) / avg_annual > 0.15",
        "threshold": 0.15,
        "metric": "summer_winter_ratio",
        "severity": "info",
        "tier": "STATS_DT",
        "recommendation": "Seasonal HVAC tuning can yield 10-20% energy savings.",
        "demo_alert": "Summer usage is {value:.0%} higher than winter — cooling-dominated building."
    }

# ── Per-category rule definitions ──────────────────────────────────────────
CATEGORY_RULES = {

    "education": {
        "primary_use": "education",
        "description": "Educational buildings (schools, universities) with strong occupancy seasonality.",
        "operating_hours": "Mon-Fri 07:00-18:00, reduced summers",
        "behavioral_rules": [
            {
                "rule_id": "EDU_SCHOOL_HOURS",
                "name": "School Hours Consumption Pattern",
                "description": "Peak consumption expected 08:00-16:00 on school days (Mon-Fri).",
                "condition": "peak_hour in range(8,16) and dayofweek < 5",
                "threshold": None,
                "metric": "peak_hour_weekday",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Validate HVAC pre-cooling starts 30 min before occupancy.",
                "demo_alert": "Energy peaks align with class schedule — occupancy-driven pattern confirmed."
            },
            {
                "rule_id": "EDU_SUMMER_BREAK",
                "name": "Summer Break Anomaly",
                "description": "July-August consumption should be 40-60% lower than academic months.",
                "condition": "avg_jul_aug / avg_oct_may < 0.6",
                "threshold": 0.6,
                "metric": "summer_to_academic_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Verify building shutdown protocols during summer recess.",
                "demo_alert": "Summer break detected — consumption dropped {value:.0%} vs academic term."
            },
            night_base_load_rule(threshold_pct=25),
            weekend_anomaly_rule(expected_drop_pct=65),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=4.0),
            {
                "rule_id": "EDU_CAFETERIA_SPIKE",
                "name": "Cafeteria/Kitchen Midday Spike",
                "description": "Electricity spike during 11:00-13:00 indicates unoptimized kitchen loads.",
                "condition": "avg_11_13h > 1.3 * avg_reading",
                "threshold": 1.3,
                "metric": "lunch_hour_ratio",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Pre-heat kitchen equipment in stages rather than simultaneously.",
                "demo_alert": "Midday kitchen load spike detected — demand staggering recommended."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.25),
            seasonal_dependency_rule(),
        ],
        "alert_rules": [
            low_occupancy_high_load_rule(hour_start=20, hour_end=6, threshold_pct=20),
            {
                "rule_id": "EDU_HOLIDAY_WASTE",
                "name": "Holiday Period Energy Waste",
                "description": "Consumption during school holidays (weekends Dec) > 30% of term average.",
                "condition": "avg_holiday_reading / avg_term_reading > 0.3",
                "threshold": 0.3,
                "metric": "holiday_to_term_ratio",
                "severity": "critical",
                "tier": "RULES_DT",
                "recommendation": "Implement holiday energy shutdown checklist.",
                "demo_alert": "Building consuming {value:.0%} of normal during school holidays — energy waste detected!"
            }
        ]
    },

    "office": {
        "primary_use": "office",
        "description": "Commercial office buildings with strong business-hours patterns.",
        "operating_hours": "Mon-Fri 08:00-19:00",
        "behavioral_rules": [
            {
                "rule_id": "OFF_BUSINESS_HOURS",
                "name": "Business Hours Energy Profile",
                "description": "80%+ of daily energy should occur between 08:00-19:00 on weekdays.",
                "condition": "pct_business_hours_energy > 0.80",
                "threshold": 0.80,
                "metric": "business_hours_pct",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Baseline established — deviations indicate schedule issues.",
                "demo_alert": "Office follows clean 9-to-5 pattern — {value:.0%} of energy in business hours."
            },
            {
                "rule_id": "OFF_MONDAY_RAMPUP",
                "name": "Monday Morning Ramp-Up",
                "description": "Monday 07:00-09:00 shows >50% higher load than Tue-Fri equivalent.",
                "condition": "avg_monday_morning > 1.5 * avg_tue_fri_morning",
                "threshold": 1.5,
                "metric": "monday_ramp_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Pre-cool Friday evening to reduce Monday morning HVAC surge.",
                "demo_alert": "Monday morning surge detected — building systems restarting simultaneously."
            },
            night_base_load_rule(threshold_pct=20),
            weekend_anomaly_rule(expected_drop_pct=70),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=3.5),
            {
                "rule_id": "OFF_OVERNIGHT_LOAD",
                "name": "Overnight Equipment Load",
                "description": "After-hours (20:00-06:00) consumption > 15% of daytime suggests equipment not shut down.",
                "condition": "avg_overnight / avg_daytime > 0.15",
                "threshold": 0.15,
                "metric": "overnight_to_daytime_ratio",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Audit servers, HVAC, and lighting auto-shutoff schedules.",
                "demo_alert": "Overnight load is {value:.0%} of daytime — check equipment shutdown policy."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.30),
            seasonal_dependency_rule(),
        ],
        "alert_rules": [
            low_occupancy_high_load_rule(hour_start=21, hour_end=6, threshold_pct=15),
            {
                "rule_id": "OFF_COOLING_WASTE",
                "name": "Disproportionate Cooling Load",
                "description": "Chilled water usage > 40% of total in mild weather (<22°C).",
                "condition": "chilled_water_pct > 0.4 and avg_temp < 22",
                "threshold": 0.4,
                "metric": "cooling_in_mild_weather",
                "severity": "critical",
                "tier": "RULES_DT",
                "recommendation": "Review thermostat setpoints — natural ventilation viable below 22°C.",
                "demo_alert": "Cooling running at full capacity in mild weather — setpoint misconfiguration suspected!"
            }
        ]
    },

    "healthcare": {
        "primary_use": "healthcare",
        "description": "Hospitals and clinics — 24/7 critical operations with highest base loads.",
        "operating_hours": "24/7 — continuous critical operations",
        "behavioral_rules": [
            {
                "rule_id": "HLT_24_7_BASE",
                "name": "Continuous Critical Base Load",
                "description": "Healthcare requires near-constant load. Night min should be >60% of day avg.",
                "condition": "min_night_reading / avg_day_reading > 0.60",
                "threshold": 0.60,
                "metric": "night_min_to_day_avg",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Normal pattern — validate backup power covers base critical load.",
                "demo_alert": "24/7 critical operations confirmed — {value:.0%} base load maintained overnight."
            },
            {
                "rule_id": "HLT_SHIFT_CHANGE",
                "name": "Shift Change Spike Pattern",
                "description": "Consumption spikes at 07:00, 15:00, and 23:00 indicate shift changeovers.",
                "condition": "local_peak in [7, 15, 23]",
                "threshold": None,
                "metric": "shift_peak_hours",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Validate medical equipment activation follows shift handover protocols.",
                "demo_alert": "Shift-change energy spikes detected — HVAC pre-conditioning recommended."
            },
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=2.0),
            {
                "rule_id": "HLT_STEAM_RATIO",
                "name": "Steam/Hot Water Proportion",
                "description": "Steam for sterilization should be <30% of total energy mix.",
                "condition": "steam_pct > 0.30",
                "threshold": 0.30,
                "metric": "steam_proportion",
                "severity": "warning",
                "tier": "STATS_DT",
                "recommendation": "Consider low-energy sterilization alternatives for non-critical equipment.",
                "demo_alert": "Steam accounts for {value:.0%} of energy mix — above benchmark threshold."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.20),
            {
                "rule_id": "HLT_HUMIDITY_LOAD",
                "name": "Humidity Control Load",
                "description": "Healthcare requires precise humidity control — correlated with dew_temperature.",
                "condition": "abs(corr_dew_temp_meter) > 0.2",
                "threshold": 0.2,
                "metric": "dew_temperature_correlation",
                "severity": "info",
                "tier": "STATS_DT",
                "recommendation": "Pre-emptive dehumidification during forecasted humid days saves reactive load.",
                "demo_alert": "Humidity-driven energy load detected — forecast-based HVAC can reduce cost."
            },
        ],
        "alert_rules": [
            {
                "rule_id": "HLT_SUDDEN_DROP",
                "name": "Unexpected Consumption Drop",
                "description": "A sudden >40% drop in consumption vs prior day average is anomalous in healthcare.",
                "condition": "pct_change_vs_yesterday < -0.40",
                "threshold": -0.40,
                "metric": "daily_pct_change",
                "severity": "critical",
                "tier": "RULES_DT",
                "recommendation": "URGENT: Verify no equipment failure or power supply interruption.",
                "demo_alert": "CRITICAL: Consumption dropped {value:.0%} — possible equipment failure or outage!"
            }
        ]
    },

    "retail": {
        "primary_use": "retail",
        "description": "Retail stores with lighting-heavy loads and trading-hours patterns.",
        "operating_hours": "Mon-Sun 09:00-21:00 (extended weekends)",
        "behavioral_rules": [
            {
                "rule_id": "RET_TRADING_HOURS",
                "name": "Trading Hours Energy Profile",
                "description": "90%+ of energy during operating hours 08:00-22:00.",
                "condition": "pct_trading_hours > 0.90",
                "threshold": 0.90,
                "metric": "trading_hours_pct",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Verify lighting and HVAC shut down within 30 min of close.",
                "demo_alert": "Retail energy profile confirmed — {value:.0%} usage within trading hours."
            },
            {
                "rule_id": "RET_WEEKEND_PEAK",
                "name": "Weekend Higher Traffic Pattern",
                "description": "Weekend energy > weekday for retail — higher footfall expected.",
                "condition": "avg_weekend > avg_weekday",
                "threshold": 1.0,
                "metric": "weekend_to_weekday_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Scale HVAC and lighting to footfall forecasts for weekend optimization.",
                "demo_alert": "Weekend peak confirmed — {value:.1f}x weekday consumption (footfall-driven)."
            },
            night_base_load_rule(threshold_pct=15),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=2.5),
            {
                "rule_id": "RET_LIGHTING_LOAD",
                "name": "Lighting Dominant Load",
                "description": "Electricity meter reading > 70% of total energy indicates lighting dominance.",
                "condition": "electricity_pct > 0.70",
                "threshold": 0.70,
                "metric": "electricity_proportion",
                "severity": "info",
                "tier": "STATS_DT",
                "recommendation": "LED retrofit and daylight harvesting sensors can reduce lighting load 30-50%.",
                "demo_alert": "Lighting accounts for majority of energy — LED upgrade ROI < 2 years."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.25),
            seasonal_dependency_rule(),
        ],
        "alert_rules": [
            {
                "rule_id": "RET_AFTER_HOURS",
                "name": "Post-Close Energy Waste",
                "description": "Consumption >10% of trading avg after store close (22:00-07:00).",
                "condition": "avg_after_close / avg_trading > 0.10",
                "threshold": 0.10,
                "metric": "post_close_ratio",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Install smart lighting with occupancy detection and auto-close timers.",
                "demo_alert": "Energy waste after store close: {value:.0%} of trading-hours load still running."
            }
        ]
    },

    "parking": {
        "primary_use": "parking",
        "description": "Parking structures — lighting dominant, very predictable commuter patterns.",
        "operating_hours": "05:00-23:00 (peak: 07-09 and 17-19)",
        "behavioral_rules": [
            {
                "rule_id": "PRK_COMMUTER_PEAKS",
                "name": "Commuter Double-Peak Pattern",
                "description": "Consumption peaks at 07:00-09:00 (arrival) and 17:00-19:00 (departure).",
                "condition": "local_peak in [7,8] or local_peak in [17,18]",
                "threshold": None,
                "metric": "commuter_peak_hours",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Confirm ventilation fans track occupancy sensor data.",
                "demo_alert": "Classic commuter pattern — morning and evening peaks confirmed."
            },
            {
                "rule_id": "PRK_OVERNIGHT_LIGHTING",
                "name": "Overnight Lighting Base Load",
                "description": "Overnight (23:00-05:00) load should be <20% of peak — mostly security lighting.",
                "condition": "avg_overnight / avg_peak < 0.20",
                "threshold": 0.20,
                "metric": "overnight_to_peak_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Motion-activated lighting can reduce overnight load by 60-70%.",
                "demo_alert": "Parking overnight lighting: {value:.0%} of peak — motion sensors recommended."
            },
            weekend_anomaly_rule(expected_drop_pct=40),
        ],
        "efficiency_rules": [
            {
                "rule_id": "PRK_VENTILATION_OVER",
                "name": "Ventilation Over-Run Detection",
                "description": "Ventilation running >2h after peak occupancy is inefficient.",
                "condition": "post_peak_ventilation_hours > 2",
                "threshold": 2,
                "metric": "post_peak_ventilation_hours",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "CO2-linked ventilation control eliminates idle fan run-time.",
                "demo_alert": "Ventilation fans running {value}h after occupancy peak — CO2 sensors recommended."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.10),
        ],
        "alert_rules": [
            low_occupancy_high_load_rule(hour_start=23, hour_end=5, threshold_pct=20),
        ]
    },

    "lodging_residential": {
        "primary_use": "lodging_residential",
        "description": "Hotels and residential buildings — near-continuous occupancy with twin peaks.",
        "operating_hours": "24/7 — peaks at 06:00-09:00 and 18:00-22:00",
        "behavioral_rules": [
            {
                "rule_id": "LOD_TWIN_PEAK",
                "name": "Morning and Evening Occupancy Peaks",
                "description": "Peak consumption at 07:00-09:00 (morning routines) and 19:00-22:00 (evening).",
                "condition": "peak_hours in [(6,9), (18,22)]",
                "threshold": None,
                "metric": "twin_peak_hours",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Pre-heat hot water 30 min before peak to avoid instant-draw spikes.",
                "demo_alert": "Twin residential peaks detected — morning and evening usage spikes."
            },
            night_base_load_rule(threshold_pct=50),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=2.5),
            {
                "rule_id": "LOD_HOT_WATER",
                "name": "Hot Water / Steam Proportion",
                "description": "Hot water should be 20-35% of energy in lodging — spikes indicate inefficiency.",
                "condition": "hot_water_pct > 0.35",
                "threshold": 0.35,
                "metric": "hot_water_proportion",
                "severity": "warning",
                "tier": "STATS_DT",
                "recommendation": "Install heat pump water heaters — 3x more efficient than electric.",
                "demo_alert": "Hot water load at {value:.0%} — above 35% benchmark for lodging sector."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.30),
            seasonal_dependency_rule(),
        ],
        "alert_rules": [
            {
                "rule_id": "LOD_VACANCY_WASTE",
                "name": "Energy Waste During Low Occupancy",
                "description": "Weekend patterns show significant waste during low-occupancy floors.",
                "condition": "avg_weekend < avg_weekday * 0.85",
                "threshold": 0.85,
                "metric": "weekend_to_weekday_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Smart floor management — power down unoccupied floors automatically.",
                "demo_alert": "Weekend occupancy drop not reflected in energy savings — review floor shutdowns."
            }
        ]
    },

    "food_sales_and_service": {
        "primary_use": "food_sales_and_service",
        "description": "Restaurants and food service — kitchen equipment dominant, meal-time driven.",
        "operating_hours": "07:00-22:00 with meal-time spikes",
        "behavioral_rules": [
            {
                "rule_id": "FSS_MEAL_PEAKS",
                "name": "Meal-Time Energy Spikes",
                "description": "Consumption peaks during 07-09 (breakfast), 11-14 (lunch), 18-21 (dinner).",
                "condition": "local_peak in [7,8,12,13,19,20]",
                "threshold": None,
                "metric": "meal_peak_hours",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Pre-heat kitchen equipment in stages to avoid simultaneous demand spikes.",
                "demo_alert": "Meal-time demand spikes confirmed — staggered start-up recommended."
            },
            night_base_load_rule(threshold_pct=20),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=3.0),
            {
                "rule_id": "FSS_REFRIGERATION",
                "name": "Refrigeration Base Load",
                "description": "Overnight base load driven by refrigeration — should be 15-25% of daily avg.",
                "condition": "avg_overnight / avg_daily between 0.15 and 0.25",
                "threshold": {"min": 0.15, "max": 0.25},
                "metric": "refrigeration_base_ratio",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Validate refrigeration door seals and defrost scheduling.",
                "demo_alert": "Overnight refrigeration load: {value:.0%} of daily — within/outside benchmark."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.20),
        ],
        "alert_rules": [
            {
                "rule_id": "FSS_IDLE_EQUIPMENT",
                "name": "Equipment Idle Between Service Periods",
                "description": "Consumption between 14:00-17:00 (post-lunch, pre-dinner) > 60% of peak.",
                "condition": "avg_idle_period / avg_peak > 0.60",
                "threshold": 0.60,
                "metric": "idle_to_peak_ratio",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Install smart idle-mode controls on ovens and grills between service periods.",
                "demo_alert": "Kitchen equipment idle at {value:.0%} of peak load — auto-idle modes needed."
            }
        ]
    },

    "entertainment_public_assembly": {
        "primary_use": "entertainment_public_assembly",
        "description": "Arenas, theatres, event spaces — event-driven, highly irregular load profiles.",
        "operating_hours": "Variable — event-driven (evenings and weekends dominant)",
        "behavioral_rules": [
            {
                "rule_id": "ENT_EVENT_SPIKE",
                "name": "Event-Driven Consumption Spike",
                "description": "Consumption >3x daily average indicates active event — HVAC and lighting at full capacity.",
                "condition": "hourly_reading > 3 * avg_reading",
                "threshold": 3.0,
                "metric": "event_spike_ratio",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Link building control system to event calendar for automated scale-up.",
                "demo_alert": "Event load spike detected — {value:.1f}x normal consumption (event in progress)."
            },
            {
                "rule_id": "ENT_EVENING_PEAK",
                "name": "Evening and Weekend Dominance",
                "description": "18:00-23:00 and weekends account for >60% of total energy.",
                "condition": "evening_weekend_pct > 0.60",
                "threshold": 0.60,
                "metric": "evening_weekend_pct",
                "severity": "info",
                "tier": "RULES_DT",
                "recommendation": "Optimize pre-event preparation time — start HVAC 90 min before, not 3h.",
                "demo_alert": "Evening/weekend energy dominates at {value:.0%} — aligned with event schedule."
            },
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=5.0),
            {
                "rule_id": "ENT_POST_EVENT_RAMPDOWN",
                "name": "Slow Post-Event Ramp-Down",
                "description": "Consumption should drop to <20% within 1h after event end.",
                "condition": "consumption_1h_post_event / event_peak > 0.20",
                "threshold": 0.20,
                "metric": "post_event_ramp_down",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Automate post-event shutdown sequence for HVAC and non-essential lighting.",
                "demo_alert": "Slow post-event shutdown — {value:.0%} of peak still running 1h after event."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.25),
        ],
        "alert_rules": [
            night_base_load_rule(threshold_pct=15),
            low_occupancy_high_load_rule(hour_start=2, hour_end=8, threshold_pct=15),
        ]
    },

    "public_services": {
        "primary_use": "public_services",
        "description": "Government offices, civic buildings — highly regular, business-hours only.",
        "operating_hours": "Mon-Fri 08:00-17:00 (strict government hours)",
        "behavioral_rules": [
            {
                "rule_id": "PUB_GOVT_HOURS",
                "name": "Government Hours Profile",
                "description": "85%+ of energy should occur Mon-Fri 08:00-17:00.",
                "condition": "pct_govt_hours_energy > 0.85",
                "threshold": 0.85,
                "metric": "govt_hours_pct",
                "severity": "info",
                "tier": "DISPLAY_DT",
                "recommendation": "Baseline normal — deviations indicate unauthorized after-hours use.",
                "demo_alert": "Government hours profile confirmed — clean {value:.0%} efficiency pattern."
            },
            night_base_load_rule(threshold_pct=15),
            weekend_anomaly_rule(expected_drop_pct=80),
        ],
        "efficiency_rules": [
            peak_to_mean_rule(threshold=2.5),
            {
                "rule_id": "PUB_LIGHTING_WASTE",
                "name": "End-of-Day Lighting Waste",
                "description": "Consumption >20% of avg between 17:00-20:00 suggests lights left on.",
                "condition": "avg_eod / avg_daytime > 0.20",
                "threshold": 0.20,
                "metric": "end_of_day_ratio",
                "severity": "warning",
                "tier": "RULES_DT",
                "recommendation": "Automated end-of-day lighting sweep at 17:30.",
                "demo_alert": "Lights/HVAC running 2-3h after close — {value:.0%} of daytime load wasted."
            },
        ],
        "weather_sensitivity_rules": [
            temp_correlation_rule(min_correlation=0.25),
            seasonal_dependency_rule(),
        ],
        "alert_rules": [
            low_occupancy_high_load_rule(hour_start=20, hour_end=7, threshold_pct=10),
            {
                "rule_id": "PUB_WEEKEND_WASTE",
                "name": "Weekend Energy Waste",
                "description": "Government buildings open on weekends is anomalous — >15% of weekday = waste.",
                "condition": "avg_weekend / avg_weekday > 0.15",
                "threshold": 0.15,
                "metric": "weekend_to_weekday_ratio",
                "severity": "critical",
                "tier": "RULES_DT",
                "recommendation": "Enable weekend lockdown mode with master shutoff.",
                "demo_alert": "Weekend energy at {value:.0%} of weekday — government building should be minimal!"
            }
        ]
    },
}

# ── Write rule files ───────────────────────────────────────────────────────────
def main():
    written = []
    for cat, rules in CATEGORY_RULES.items():
        out_path = os.path.join(RULES_DIR, f"{cat}_rules.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(rules, f, indent=2, ensure_ascii=False)
        total_rules = (len(rules.get("behavioral_rules", [])) +
                       len(rules.get("efficiency_rules", [])) +
                       len(rules.get("weather_sensitivity_rules", [])) +
                       len(rules.get("alert_rules", [])))
        print(f"  [{cat:<35}]  {total_rules} rules  ->  {os.path.basename(out_path)}")
        written.append(out_path)

    print(f"\n  Total: {len(written)} rule files written to:\n  {RULES_DIR}")
    return written

if __name__ == "__main__":
    print("Generating domain intelligence rules...")
    main()
    print("Done.")
