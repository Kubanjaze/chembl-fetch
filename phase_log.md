# Phase 80 — ChEMBL API: Fetch KRAS Bioactivity Data
## Phase Log

**Status:** ✅ Complete
**Started:** 2026-03-27
**Completed:** 2026-03-27
**Repo:** https://github.com/Kubanjaze/chembl-fetch

---

## Log

### 2026-03-27 — Phase complete
- v1.0 plan pushed to Kubanjaze/chembl-fetch
- Target ID corrected: CHEMBL4630 (Chk1) → CHEMBL2189121 (GTPase KRas)
- pchembl_value type fix: string → pd.to_numeric coercion
- 100 records fetched: 51 unique molecules, 9 activity types
- pChEMBL range 2.70-8.05 (5 orders of magnitude)
- Key insight: KRAS activity data includes covalent kinetics (Kinact, T1/2) beyond standard IC50/Ki
- Cost: $0.00 (free public API)
- Committed and pushed to Kubanjaze/chembl-fetch
