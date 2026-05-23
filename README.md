# SORT Pipeline — Clinical AI Harm Monitoring

A Python pipeline built on the LLM assessor design from Owen et al. (2026), 
arXiv:2604.21412, applied to a clinical AI harm monitoring question not covered 
in the paper's case studies.

## What this does

Classifies incidents from the AI Incident Database (AIID) against a structured 
monitoring question using Claude Haiku as the LLM assessor, then splits results 
by time period to surface directional harm trends.

## Monitoring question used in this run

- Subject: Patients or clinicians in healthcare settings
- Opportunity: Using clinical AI systems for diagnosis, decision support, or 
  documentation
- Risk event: Harm caused by incorrect, biased, or overconfident AI output
- Timeframe: 2020–2025

**Result:** 28 full matches from 1,480 incidents assessed, including Epic's 
sepsis prediction errors, IBM Watson's unsafe oncology recommendations, 
UnitedHealth's AI coverage denials at a reported 90% error rate, and Whisper 
hallucinating content in medical records.

## What a properly structured SORT question would look like

The question above is an exploratory proxy. A correctly structured SORT 
monitoring question for this domain would be:

- Subject: Patients receiving care where clinical decision support AI is 
  actively used in the care pathway
- Opportunity: When a clinician acts on or in response to an AI-generated 
  recommendation
- Risk event: A patient safety incident attributable to incorrect, biased, or 
  overconfident AI output
- Timeframe: 2020–2025

The key difference is the opportunity condition — the proxy question describes 
a setting, where the structured question identifies the specific moment of 
exposure where the risk event could occur. Future runs should use the structured 
version.

## Scope and limitations

This pipeline implements the LLM assessor component from Owen et al. The full 
paper additionally runs a secondary database to enable predictive harm exposure 
quadrant mapping — that analysis requires longitudinal exposure data not 
available in the AIID, so this pipeline focuses on incident classification and 
pattern detection rather than forward-looking risk projection.

The temporal split (2020–2022 vs 2023–2025) is indicative rather than precise. 
AIID date fields reflect report publication dates rather than incident occurrence 
dates, and some incidents in the database date back to 1998.

## Requirements
anthropic
pandas

Set your API key:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

## Usage

```bash
python3 sort_pipeline.py      # classify incidents
python3 analyze_results.py    # temporal split analysis
```

## Files

- `sort_pipeline.py` — main classification pipeline
- `analyze_results.py` — temporal analysis of results
- `incidents.csv` — AIID export (not included; download from incidentdatabase.ai)
- `sort_results.csv` — output from pipeline run
