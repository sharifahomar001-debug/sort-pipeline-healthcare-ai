import anthropic
import pandas as pd
import json

# Load full AIID incidents
df = pd.read_csv("incidents.csv", on_bad_lines='skip', encoding='utf-8')
print(f"Loaded {len(df)} incidents")
print(f"Columns: {df.columns.tolist()}")

# SORT Monitoring Question -- healthcare AI harm
SORT = {
    "subject": "patients or clinicians in healthcare settings",
    "opportunity": "when a clinician acts on or in response to an AI-generated recommendation",
    "risk_event": "harm caused by incorrect, biased, or overconfident AI output",
    "timeframe": "2020-2025"
}

client = anthropic.Anthropic()

def assess_incident(title, description, harmed_parties, sort):
    prompt = f"""You are assessing whether an AI incident matches a monitoring question.

MONITORING QUESTION:
Subject: {sort['subject']}
Opportunity: {sort['opportunity']}
Risk event: {sort['risk_event']}

INCIDENT:
Title: {title}
Description: {description}
Harmed parties: {harmed_parties}

Respond in JSON only with these exact fields:
- subject_match: true, false, or indeterminate
- risk_event_match: true, false, or indeterminate
- reasoning: one sentence

JSON only, no other text."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    
    try:
        text = message.content[0].text
        # Strip markdown code fences
        text = text.replace('```json', '').replace('```', '').strip()
        # Extract JSON
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != 0:
            result = json.loads(text[start:end])
            # Normalise true/false to strings
            for key in ['subject_match', 'risk_event_match']:
                if isinstance(result.get(key), bool):
                    result[key] = 'true' if result[key] else 'false'
            return result
        else:
            return {
                "subject_match": "indeterminate",
                "risk_event_match": "indeterminate",
                "reasoning": "parse error"
            }
    except:
        return {
            "subject_match": "indeterminate",
            "risk_event_match": "indeterminate",
            "reasoning": "parse error"
        }

# Run on all 1480 incidents
results = []
sample = df.head(1480)

for idx, row in sample.iterrows():
    title = str(row.get("title", ""))
    description = str(row.get("description", ""))
    harmed = str(row.get("Alleged harmed or nearly harmed parties", ""))
    print(f"Assessing incident {idx+1}: {title[:50]}...")
    result = assess_incident(title, description, harmed, SORT)
    result["incident_id"] = row.get("incident_id", idx)
    result["title"] = title[:80]
    results.append(result)

# Split by time period
df_results = pd.DataFrame(results)
df_results.to_csv("sort_results.csv", index=False)

# Add dates from original dataframe
full_matches_data = [r for r in results if r["subject_match"] == "true" and r["risk_event_match"] == "true"]

# Get dates for full matches
early_matches = []
late_matches = []

for match in full_matches_data:
    incident_row = df[df["incident_id"] == match["incident_id"]]
    if not incident_row.empty:
        date_val = incident_row.iloc[0]["date"]
        if pd.notna(date_val) and str(date_val)[:4].isdigit():
            year = int(str(date_val)[:4])
            if 2020 <= year <= 2022:
                early_matches.append(match)
            elif 2023 <= year <= 2025:
                late_matches.append(match)

print(f"\n--- SORT PIPELINE RESULTS ---")
print(f"Monitoring Question: Among {SORT['subject']} {SORT['opportunity']}, how many experienced {SORT['risk_event']}?")
print(f"Timeframe: 2020-2022 vs 2023-2025")
print(f"\nTotal assessed: {len(results)}")
print(f"Full matches: {len(full_matches_data)}")
print(f"Partial matches: {len([r for r in results if r not in full_matches_data and (r['subject_match'] == 'indeterminate' or r['risk_event_match'] == 'indeterminate')])}")
print(f"No matches: {len([r for r in results if r['subject_match'] == 'false' and r['risk_event_match'] == 'false'])}")
print(f"\nPeriod 1 (2020-2022): {len(early_matches)} full matches")
print(f"Period 2 (2023-2025): {len(late_matches)} full matches")

if len(early_matches) >= 3 and len(late_matches) >= 3:
    if len(late_matches) > len(early_matches):
        print(f"\nHarm trend: INCREASING")
    elif len(late_matches) < len(early_matches):
        print(f"\nHarm trend: DECREASING")
    else:
        print(f"\nHarm trend: STABLE")
else:
    print(f"\nHarm trend: INSUFFICIENT DATA for reliable trend claim")

print(f"\nFull match incidents:")
for m in full_matches_data:
    print(f"  [{m['incident_id']}] {m['title']}")
    print(f"  Reason: {m['reasoning']}")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("sort_results.csv", index=False)
print(f"\nResults saved to sort_results.csv")
