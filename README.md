# SORT Pipeline — Clinical AI Harm Monitoring
A Python pipeline built on the LLM assessor design from Owen et al. (2026), 
arXiv:2604.21412, applied to a clinical AI harm monitoring question in healthcare.

## What this does
Classifies incidents from the AI Incident Database (AIID) against a structured 
monitoring question using Claude Haiku as the LLM assessor, then splits results 
by time period to surface directional harm trends.

## Monitoring question used in this run
Subject: Patients or clinicians in healthcare settings
Opportunity: When a clinician acts on or in response to an AI-generated recommendation
Risk event: Harm caused by incorrect, biased, or overconfident AI output
Timeframe: 2020–2025

**Result:** 
24 full matches from 1,480 incidents assessed, including Epic's sepsis prediction errors, 
IBM Watson's unsafe oncology recommendations, UnitedHealth's AI coverage denials at a 
reported 90% error rate, the VA suicide prevention algorithm's documented bias against 
female veterans, racial bias in lung function diagnostics, and Whisper hallucinating 
content in medical records. Trend across periods: stable (8 matches in 2020–2022, 8 in 2023–2025).

## Scope and limitations
This pipeline implements the LLM assessor component from Owen et al. as a simplified version. 
Two limitations are worth noting. First, the pipeline outputs binary true/false classifications per incident. 
The full estimation procedure in Owen et al. additionally extracts per-incident 
harm count bounds and computes aggregate harm ranges per period — that step is not implemented here.

Second, the temporal split (2020–2022 vs 2023–2025) is indicative rather than precise. 
AIID date fields reflect report publication dates rather than incident occurrence dates.
A stronger source for future runs would be the OECD AIM database (15,346 incidents),
which includes structured fields for harm type, affected stakeholders, and AI system autonomy 
level that map more cleanly onto a properly structured SORT monitoring question.

Future work would extend the pipeline to extract per-incident harm bounds, run identical 
monitoring questions across multiple models to build confidence signals into classifications, 
and automate end-to-end ingestion and scheduled runs, moving from a one-time classification 
exercise toward continuous surveillance.

A stronger source for future runs would be the OECD AIM database (15,346 incidents), 
which includes structured fields for harm type, affected stakeholders, and AI system autonomy 
level that map more cleanly onto a properly structured SORT monitoring question. 

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
