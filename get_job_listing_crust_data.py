import requests
import time

CRUSTDATA_API_URL = "https://api.crustdata.com/data_lab/job_listings/Table/"
API_TOKEN = "YOUR_CRUSTDATA_API_KEY"

HEADERS = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# -----------------------------
# BIOTECH FILTER DEFINITIONS
# -----------------------------

BIOTECH_INDUSTRIES = [
    "Biotechnology",
    "Life Sciences",
    "Pharmaceuticals",
    "Medical Devices",
    "Biotech",
    "Pharma"
]

BIOTECH_TITLES = [
    "Scientist",
    "Research",
    "Clinical",
    "Biotech",
    "Bioinformatics",
    "Biologist",
    "R&D",
    "Lab",
    "QC",
    "QA",
    "Regulatory",
    "Clinical Research",
    "Research & Development",
    "Lab roles",
    "Clinical & Regulatory",
    "Quality (QA/QC)",
    "Manufacturing & Operations",
    "Bioinformatics / Data Science",
    "Bioprocess / Biopharma",
    "Medical roles",
    "Compliance & Safety",
    "Leadership roles",
]


def build_biotech_filter():
    """
    Builds filter object combining:
    - Biotech industries
    - Biotech job title keywords
    - Recent postings (last 90 days)
    """

    # OR conditions for company industries
    industry_conditions = [
        {
            "column": "company_industry",
            "type": "(.)",
            "value": industry
        } for industry in BIOTECH_INDUSTRIES
    ]

    # OR conditions for biotech titles
    title_conditions = [
        {
            "column": "title",
            "type": "(.)",
            "value": title
        } for title in BIOTECH_TITLES
    ]

    filter_block = {
        "op": "and",
        "conditions": [
            {
                "op": "or",
                "conditions": industry_conditions
            },
            {
                "op": "or",
                "conditions": title_conditions
            },
            {
                "column": "date_updated",
                "type": ">",
                "value": "2025-11-01"   # keep jobs recent
            },

        ]
    }

    return filter_block


# -----------------------------
# FETCH JOB LISTINGS (WITH PAGINATION)
# -----------------------------

def fetch_biotech_jobs(limit=100):
    """
    Fetch up to ALL biotech jobs from Crustdata.
    Uses pagination logic until no more records found.
    """

    offset = 0
    all_jobs = []

    biotech_filters = build_biotech_filter()

    while True:
        body = {
            "dataset": {
                "name": "job_listings",
                "id": "joblisting"
            },
            "filters": biotech_filters,
            "offset": offset,
            "limit": limit,
            "sorts": [
                {"column": "date_updated", "type": "desc"}
            ]
        }

        response = requests.post(CRUSTDATA_API_URL, headers=HEADERS, json=body)
        json_data = response.json()

        if "rows" not in json_data:
            print("Unexpected response:", json_data)
            break

        rows = json_data["rows"]
        fields = [f["api_name"] for f in json_data["fields"]]

        if not rows:
            break

        # Convert each row into dictionary
        for row in rows:
            job = {fields[i]: row[i] for i in range(len(fields))}
            all_jobs.append(job)

        print(f"Fetched {len(rows)} jobs (offset={offset})")

        # Stop if fewer than limit returned
        if len(rows) < limit:
            break

        offset += limit
        time.sleep(1)  # avoid rate limits

    print(f"\nTotal biotech jobs fetched: {len(all_jobs)}\n")
    return all_jobs


# -----------------------------
# RUN SCRIPT
# -----------------------------

if __name__ == "__main__":
    jobs = fetch_biotech_jobs()
    print("Sample job result:")
    if jobs:
        print(jobs[0])

