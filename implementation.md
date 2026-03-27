# Phase 80 — ChEMBL API: Fetch KRAS Bioactivity Data

**Version:** 1.0 | **Tier:** Micro | **Date:** 2026-03-28

## Goal
Fetch bioactivity data for a well-known drug target (KRAS) from the ChEMBL REST API. Demonstrates external data integration without API keys (free, public data).

CLI: `python main.py --target CHEMBL4630 --limit 100`

Outputs: chembl_bioactivity.csv, chembl_report.txt

## Logic
1. Query ChEMBL REST API for target info (CHEMBL4630 = KRAS)
2. Fetch bioactivity data (IC50, Ki) for the target
3. Parse and filter: keep records with molecule SMILES, standard_value, standard_type
4. Save as CSV + summary report
5. Basic stats: compound count, activity type distribution, value range

## Key Concepts
- ChEMBL REST API (https://www.ebi.ac.uk/chembl/api/data/)
- External bioactivity database integration
- JSON pagination handling
- Data quality filtering (units, types, missing values)

## Verification Checklist
- [ ] Target info fetched (KRAS / CHEMBL4630)
- [ ] Bioactivity records retrieved
- [ ] CSV output with SMILES, activity values
- [ ] Summary stats reported
- [ ] --help works
- [ ] $0.00 cost (free API)

## Risks
- ChEMBL API may be slow or rate-limited
- KRAS may have very many records — limit parameter controls this
- API format may change — use versioned endpoint
