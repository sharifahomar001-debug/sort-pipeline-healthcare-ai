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
    "opportunity": "using clinical AI systems for diagnosis, decision support, or documentation",
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
    
    print(f"Assessing incident {idx+1}/100: {title[:50]}...")
    
    result = assess_incident(title, description, harmed, SORT)
    result["incident_id"] = row.get("incident_id", idx)
    result["title"] = title[:80]
    results.append(result)

# Classify matches
full_matches = [r for r in results if r["subject_match"] == "true" and r["risk_event_match"] == "true"]
partial_matches = [r for r in results if r not in full_matches and (r["subject_match"] == "indeterminate" or r["risk_event_match"] == "indeterminate")]
no_matches = [r for r in results if r["subject_match"] == "false" and r["risk_event_match"] == "false"]

print(f"\n--- SORT PIPELINE RESULTS ---")
print(f"Monitoring Question: Among {SORT['subject']} {SORT['opportunity']}, how many experienced {SORT['risk_event']}?")
print(f"\nTotal assessed: {len(results)}")
print(f"Full matches: {len(full_matches)}")
print(f"Partial matches: {len(partial_matches)}")
print(f"No matches: {len(no_matches)}")
print(f"\nFull match incidents:")
for m in full_matches:
    print(f"  [{m['incident_id']}] {m['title']}")
    print(f"  Reason: {m['reasoning']}")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv("sort_results.csv", index=False)
print(f"\nResults saved to sort_results.csv")
