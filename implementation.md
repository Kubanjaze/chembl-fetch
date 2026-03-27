# Phase 80 — ChEMBL API: Fetch KRAS Bioactivity Data

**Version:** 1.1 | **Tier:** Micro | **Date:** 2026-03-27

## Goal
Fetch bioactivity data for GTPase KRas from the ChEMBL REST API. Demonstrates external public database integration without API keys — the first phase pulling real-world experimental data from an external source.

CLI: `python main.py --target CHEMBL2189121 --limit 100`

Outputs: chembl_bioactivity.csv, chembl_report.txt

## Logic
1. Query ChEMBL REST API for target metadata (name, organism, type) via `/target/{id}.json`
2. Fetch bioactivity records via `/activity.json?target_chembl_id={id}` with pagination
3. Filter: keep records with SMILES, standard_value, and standard_type present
4. Parse pchembl_value as numeric (API returns strings — coerce with `pd.to_numeric`)
5. Save filtered records as CSV + summary report with activity type distribution and pChEMBL stats

## Key Concepts
- **ChEMBL REST API**: `https://www.ebi.ac.uk/chembl/api/data/` — free, no authentication
- **Pagination**: API returns `page_meta.next` for multi-page results; loop with offset increment
- **Target lookup**: KRAS = `CHEMBL2189121` (GTPase KRas, Homo sapiens) — NOT CHEMBL4630 (that's Chk1)
- **pChEMBL value**: -log10(IC50/Ki/etc in M) — comparable across activity types; API returns as string, must coerce to numeric
- **Data quality filtering**: skip records missing SMILES or standard_value
- **requests library**: simple HTTP GET with timeout and raise_for_status()

## Verification Checklist
- [x] Target info fetched: GTPase KRas, Homo sapiens, SINGLE PROTEIN
- [x] 100 bioactivity records retrieved
- [x] CSV output with SMILES, activity values, assay info
- [x] Summary stats: 51 unique molecules, 9 activity types, pChEMBL mean=5.91
- [x] --help works
- [x] $0.00 cost (free public API)

## Deviations from Plan
- **Target ID corrected**: Plan used CHEMBL4630 (Chk1); actual KRAS ID is CHEMBL2189121
- **pchembl_value type fix**: API returns pchembl as string; added `pd.to_numeric(errors="coerce")` to compute stats

## Risks (resolved)
- Wrong ChEMBL target ID — resolved by querying `/target/search.json?q=KRAS` to find correct ID
- pchembl_value as string caused TypeError on `.mean()` — resolved with `pd.to_numeric` coercion
- ChEMBL API rate limiting — not observed for 100 records; timeout=60s sufficient
- API format changes — using stable JSON endpoints, no versioned API prefix needed

## Results
| Metric | Value |
|--------|-------|
| Target | GTPase KRas (CHEMBL2189121) |
| Organism | Homo sapiens |
| Records fetched | 100 |
| Unique molecules | 51 |
| Activity types | 9 (IC50=25, Ki=16, Ratio=15, T1/2=15, Kinact=13, Kd=10, Activity=3, EC50=2, FC=1) |
| pChEMBL values | n=40, mean=5.91, range=[2.70, 8.05] |
| Assay type | 100% Binding (B) |
| Cost | $0.00 |

Key finding: KRAS has diverse activity measurement types beyond just IC50/Ki — Kinact, T1/2, and Kd reflect covalent inhibitor kinetics (sotorasib, adagrasib are covalent binders). The pChEMBL range (2.70-8.05) spans 5 orders of magnitude, indicating both weak screening hits and potent clinical candidates.
