import os
import json
import time
import re
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# ---------------------
# Retry wrapper
# ---------------------
def retry(max_retries=3, delay=2):
    def wrap(fn):
        def run(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    print(f"[Retry {attempt+1}/{max_retries}] Error: {e}")
                    time.sleep(delay)
            raise Exception("Failed after retries.")
        return run
    return wrap


# -------------------------------------------------
# Extract ONLY the "About <company>" text
# -------------------------------------------------
def extract_about_section(long_description: str, company: str):
    if not long_description:
        return None

    pattern = rf"(About\s+{re.escape(company)}[\s\S]+?)(?=\n\n|$)"
    match = re.search(pattern, long_description, re.IGNORECASE)

    if match:
        return match.group(1).strip()[:300]

    return None


# -------------------------------------------------
# LLM call with minimal fields (OpenAI)
# -------------------------------------------------
@retry(max_retries=3, delay=2)
def find_company_domain_minimal(job):
    company = job.get("company_name", "")
    title = job.get("title", "")
    location = job.get("location", "")
    description = job.get("description", "")
    apply_links = job.get("apply_links", [])
    job_highlights = job.get("job_highlights", [])

    first_url = apply_links[0]["link"] if apply_links else ""
    about_text = extract_about_section(description, company)

    minimal_payload = {
        "company_name": company,
        "title": title,
        "location": location,
        "apply_source_url": first_url,
        "about_summary": about_text,
        "job_highlights" : job_highlights
    }

    prompt = f"""
You are a company identification expert.

1) Given the job details below, identify the official company website domain. 
Be 100% sure it matches the correct company — not a similarly named business.

2)Given job_highlights it can include detail like how many year of expereince is required for this job so also provide that in response
Use ONLY the data provided. If uncertain, return your best guess with lower confidence.

DATA:
{json.dumps(minimal_payload, indent=2)}

Return STRICT JSON ONLY:
{{
  "company_name": "{company}",
  "domain": "www.example.com",
  "confidence": 0.0,
  "experience_required": "example 5 years"
}}
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Replace with gpt-4o / gpt-4.1 if you want higher accuracy
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        response_format={"type": "json_object"},
    )

    return json.loads(completion.choices[0].message.content)


# -------------------------------------------------
# Process full job list
# -------------------------------------------------
def append_company_domains(jobs, output_file="output/3_jobs_with_domains.json"):
    updated = []

    for job in jobs:
        print(f"Processing company: {job.get('company_name')}")

        result = find_company_domain_minimal(job)

        job["company_domain"] = result.get("domain")
        job["experience_required"] = result.get("experience_required")
        job["domain_confidence"] = result.get("confidence")

        updated.append(job)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        json.dump(updated, f, indent=2)

    print(f"Saved: {output_file}")
    return updated


# ------------- Example usage -------------
if __name__ == "__main__":
    with open("input_jobs.json", "r") as f:
        jobs = json.load(f)

    final = append_company_domains(jobs)
    print("Completed:", len(final))
