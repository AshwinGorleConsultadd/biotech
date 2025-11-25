import json
import os
import re


def normalize_key(key: str):
    """
    Convert keys like 'Company Domain ', 'Employee Count', 'Address - Locations'
    into snake_case: company_domain, employee_count, address_locations
    """
    key = key.strip()
    key = key.replace("-", " ")
    key = key.replace("  ", " ")
    key = key.lower()
    return re.sub(r"\s+", "_", key)


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def attach_company_details(
    jobs_file="output/3_jobs_with_domains.json",
    enriched_file="output/5_enriched_compnay.json",
    output_file="output/6_final.json"
):
    # Load both files
    print("Loading jobs and enriched companies...")
    jobs = load_json(jobs_file)
    enriched_companies = load_json(enriched_file)

    # Build lookup by UID
    company_map = {}

    for comp in enriched_companies:
        uid = comp.get("Company Uid")

        if not uid:
            continue

        # normalize keys to snake_case
        normalized = {normalize_key(k): v for k, v in comp.items()}

        company_map[uid] = normalized

    # Attach matched company to jobs
    final_jobs = []

    for job in jobs:
        comp_uid = job.get("company_uid")

        if comp_uid and comp_uid in company_map:
            job["company_details"] = company_map[comp_uid]
        else:
            job["company_details"] = None  # no match

        final_jobs.append(job)

    # Save output
    save_json(output_file, final_jobs)
    print(f"✔ Saved enriched jobs → {output_file}")

    return final_jobs


# ------------- Example usage -------------
if __name__ == "__main__":
    attach_company_details()
