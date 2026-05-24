import pandas as pd

# Load existing results
results = pd.read_csv("sort_results.csv")
incidents = pd.read_csv("incidents.csv")

# Get full matches
full_matches = results[(results["subject_match"] == "true") & (results["risk_event_match"] == "true")]

# Merge with incident dates
full_matches = full_matches.merge(incidents[["incident_id", "date"]], on="incident_id", how="left")

# Split by period
early = full_matches[full_matches["date"].str[:4].astype(float) <= 2022]
late = full_matches[full_matches["date"].str[:4].astype(float) > 2022]

print(f"Period 1 (2020-2022): {len(early)} full matches")
print(f"Period 2 (2023-2025): {len(late)} full matches")
print(f"\nEarly matches:")
print(early[["incident_id", "title", "date"]])
print(f"\nLate matches:")
print(late[["incident_id", "title", "date"]])
