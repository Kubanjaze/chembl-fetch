import sys
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import argparse, os, json, warnings
warnings.filterwarnings("ignore")
import requests
import pandas as pd

CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"


def fetch_target_info(target_id: str) -> dict:
    """Fetch target metadata from ChEMBL."""
    url = f"{CHEMBL_BASE}/target/{target_id}.json"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return {
        "target_chembl_id": data.get("target_chembl_id"),
        "pref_name": data.get("pref_name"),
        "organism": data.get("organism"),
        "target_type": data.get("target_type"),
    }


def fetch_bioactivity(target_id: str, limit: int = 100) -> list[dict]:
    """Fetch bioactivity data for a target from ChEMBL."""
    url = f"{CHEMBL_BASE}/activity.json"
    params = {
        "target_chembl_id": target_id,
        "limit": min(limit, 1000),
        "offset": 0,
    }

    records = []
    while len(records) < limit:
        resp = requests.get(url, params=params, timeout=60)
        resp.raise_for_status()
        data = resp.json()

        activities = data.get("activities", [])
        if not activities:
            break

        for act in activities:
            # Filter: keep records with SMILES and standard_value
            smiles = act.get("canonical_smiles")
            std_value = act.get("standard_value")
            std_type = act.get("standard_type")

            if smiles and std_value is not None and std_type:
                records.append({
                    "molecule_chembl_id": act.get("molecule_chembl_id"),
                    "canonical_smiles": smiles,
                    "standard_type": std_type,
                    "standard_value": float(std_value),
                    "standard_units": act.get("standard_units", ""),
                    "standard_relation": act.get("standard_relation", "="),
                    "pchembl_value": act.get("pchembl_value"),
                    "assay_chembl_id": act.get("assay_chembl_id"),
                    "assay_type": act.get("assay_type"),
                    "assay_description": act.get("assay_description", "")[:100],
                })

            if len(records) >= limit:
                break

        # Pagination
        next_url = data.get("page_meta", {}).get("next")
        if not next_url:
            break
        params["offset"] += params["limit"]

    return records[:limit]


def main():
    parser = argparse.ArgumentParser(
        description="Phase 80 — ChEMBL API: fetch bioactivity data for a target",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--target", default="CHEMBL2189121", help="ChEMBL target ID (CHEMBL2189121=KRAS)")
    parser.add_argument("--limit", type=int, default=100, help="Max records to fetch")
    parser.add_argument("--output-dir", default="output", help="Output directory")
    args = parser.parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"\nPhase 80 — ChEMBL Bioactivity Fetch")
    print(f"Target: {args.target} | Limit: {args.limit}\n")

    # Step 1: Target info
    print("Fetching target info...")
    try:
        target_info = fetch_target_info(args.target)
        print(f"  Name: {target_info['pref_name']}")
        print(f"  Organism: {target_info['organism']}")
        print(f"  Type: {target_info['target_type']}\n")
    except Exception as e:
        print(f"  Error fetching target: {e}")
        target_info = {"target_chembl_id": args.target, "error": str(e)}

    # Step 2: Bioactivity data
    print("Fetching bioactivity data...")
    records = fetch_bioactivity(args.target, limit=args.limit)
    print(f"  Records retrieved: {len(records)}\n")

    if not records:
        print("No records found. Check target ID.")
        return

    df = pd.DataFrame(records)

    # Step 3: Summary stats
    print("--- Summary Statistics ---")
    type_counts = df["standard_type"].value_counts()
    print(f"Activity types:\n{type_counts.to_string()}\n")

    assay_types = df["assay_type"].value_counts()
    print(f"Assay types:\n{assay_types.to_string()}\n")

    unique_mols = df["molecule_chembl_id"].nunique()
    print(f"Unique molecules: {unique_mols}")

    pchembl = pd.to_numeric(df["pchembl_value"], errors="coerce").dropna()
    if len(pchembl) > 0:
        print(f"pChEMBL values: n={len(pchembl)}, mean={pchembl.mean():.2f}, "
              f"min={pchembl.min():.2f}, max={pchembl.max():.2f}")

    # Save CSV
    csv_path = os.path.join(args.output_dir, "chembl_bioactivity.csv")
    df.to_csv(csv_path, index=False)
    print(f"\nSaved: {csv_path}")

    # Report
    report = (
        f"Phase 80 — ChEMBL Bioactivity Report\n{'='*50}\n"
        f"Target: {target_info.get('pref_name', args.target)} ({args.target})\n"
        f"Organism: {target_info.get('organism', 'N/A')}\n"
        f"Records fetched: {len(records)}\n"
        f"Unique molecules: {unique_mols}\n\n"
        f"Activity type distribution:\n{type_counts.to_string()}\n\n"
        f"Assay type distribution:\n{assay_types.to_string()}\n\n"
    )
    if len(pchembl) > 0:
        report += f"pChEMBL: n={len(pchembl)}, mean={pchembl.mean():.2f}, range=[{pchembl.min():.2f}, {pchembl.max():.2f}]\n"
    report += f"\nCost: $0.00 (free public API)\n"
    print(f"\n{report}")

    with open(os.path.join(args.output_dir, "chembl_report.txt"), "w") as f:
        f.write(report)
    print("Done.")


if __name__ == "__main__":
    main()
