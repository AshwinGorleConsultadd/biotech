
import requests
import json
import os
import time
import hashlib


# SEARCHAPI_KEY = "iYDUQnrq14XX3ipPswPr3gSK"   # put your key here
SEARCHAPI_KEY = "AIzaSyAPL1KYElx7P7j2rSPOkia6Ud0PDioD1MU"   # put your key here


# -------------------------------------------------------------------
# Utility: generate simple queries
# -------------------------------------------------------------------
def generate_simple_queries(roles, locations):
    queries = []
    for role in roles:
        for location in locations:
            query = f"{role} in {location}"
            queries.append(query)
    return queries
# -------------------------------------------------------------------
# Utility: create UID for deduplication
# -------------------------------------------------------------------
def job_uid(job):
    """
    Create a unique hash per job using title+company+location.
    """
    title = job.get("title", "")
    company = job.get("company_name", "")
    loc = job.get("location", "")
    raw = (title + company + loc).lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()

def company_uid(job):
    """
    Create a unique hash per job using title+company+location.
    """
    company = job.get("company_name", "")
    raw = (company).lower().strip()
    return hashlib.md5(raw.encode()).hexdigest()


# -------------------------------------------------------------------
# Fetch Google Jobs with pagination + attach query to job object
# -------------------------------------------------------------------
def fetch_jobs_for_query(query, limit_per_query=10):
    """
    Fetch up to X jobs for a specific query using SearchAPI.io Google Jobs API.
    Uses ?start= pagination approach.
    """

    print(f"\n🔍 Fetching jobs for query: '{query}'  | Limit: {limit_per_query}")
    call_count = 0
    all_jobs = []
    seen = set()  # avoid duplicates

    start = 0
    page_size = 10   # SearchAPI tends to give ~10 results per page

    while len(all_jobs) < limit_per_query:

        url = "https://www.searchapi.io/api/v1/search"
        params = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
            "gl": "us",
            "udm": "8",
            "api_key": SEARCHAPI_KEY,
            "start": start
        }

        try:
            print("✅ calling api for : ",query)
            response = requests.get(url, params=params)
            call_count = call_count + 1
            response.raise_for_status()
            data = response.json()
            print("DATA------", data)

            jobs = data.get("jobs", [])

            if not jobs:
                break  # no more pages
            if call_count >= 2:
                break

            for job in jobs:
                uid = job_uid(job)
                if uid not in seen:
                    seen.add(uid)
                    job["source_query"] = query  # ← attach originating query
                    job["company_uid"] = company_uid(job)
                    all_jobs.append(job)

                if len(all_jobs) >= limit_per_query:
                    break

            start += page_size
            time.sleep(0.4)  # avoid rate-limits & stay safe

        except Exception as e:
            print(f"⚠️ Error fetching page {start} for query '{query}': {e}")
            break

    print(f"✔ Total fetched for '{query}': {len(all_jobs)}")
    return all_jobs


# -------------------------------------------------------------------
# WRAPPER FUNCTION: Roles + Locations → Queries → Fetch jobs → Save JSON
# -------------------------------------------------------------------
def fetch_jobs_wrapper(roles, locations, jobs_per_query=10):
    """
    1. Generate queries
    2. Save queries JSON
    3. Fetch jobs for each query (with pagination + dedupe)
    4. Save jobs to JSON
    5. Return jobs array
    """

    # 1️⃣ Generate queries
    queries = generate_simple_queries(roles, locations)
    print(f"Generated {len(queries)} queries")

    # Save queries
    os.makedirs("output", exist_ok=True)
    with open("output/1_generate_queries.json", "w") as f:
        json.dump(queries, f, indent=4)
    print("✔ Saved queries → output/2_generate_queries.json")

    # 2️⃣ Fetch jobs per query
    all_jobs = []
    for q in queries:
        jobs = fetch_jobs_for_query(q, limit_per_query=jobs_per_query)
        all_jobs.extend(jobs)

    # 3️⃣ Save all jobs into one file
    with open("output/2_fetched_jobs.json", "w", encoding="utf-8") as f:
        json.dump(all_jobs, f, indent=4, ensure_ascii=False)

    print(f"\n✔ Total jobs fetched across ALL queries: {len(all_jobs)}")
    print("✔ Saved → output/2_fetched_jobs.json")

    return all_jobs


# -------------------------------------------------------------------
# Example Usage
# -------------------------------------------------------------------
if __name__ == "__main__":
    roles = ["Bio Tech", "Research Scientist"]
    locations = ["New York", "Boston"]

    jobs = fetch_jobs_wrapper(
        roles,
        locations,
        jobs_per_query=10
    )

    print("\nDONE")
