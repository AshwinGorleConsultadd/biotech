from datetime import datetime, timedelta
from typing import List, Optional, Set
import itertools
import re
import os
import json

def _normalize(text: str) -> str:
    return re.sub(r'\s+', ' ', text.strip())

def generate_job_queries_prod(
    roles: List[str],
    location: str,
    include_date_filters: bool = True,
    recent_days: int = 14,
    max_queries: int = 200
) -> List[str]:
    """
    Generate a list of Google Jobs style queries given role names and a location.

    Args:
        roles: list of role strings (e.g., ["Research Scientist", "Bioinformatics Scientist"])
        location: location string (e.g., "New York", "Boston, MA")
        include_date_filters: whether to add 'posted this week/month' and `after:` date variants
        recent_days: for `after:` variant, how many days back to use (default 14)
        max_queries: upper bound to prevent explosion (function truncates results if needed)

    Returns:
        List[str] - de-duplicated queries ready to pass as `q` parameter to Google Jobs scraper
    """

    # Basic seniority variants (ordered by usefulness)
    seniority_tokens = ["senior", "lead", "principal", "manager", "director"]
    # Useful synonyms / qualifier connectors
    connectors = ["", "jobs", "roles", "positions", "openings"]
    # Date filters (human + "after:" operator)
    date_keywords = []
    if include_date_filters:
        date_keywords = [
            "posted this week",
            "posted this month",
            "posted today",
            "posted in last 7 days",
            "posted in last 30 days"
        ]
        # compute after:YYYY-MM-DD for recent_days
        since_date = (datetime.utcnow() - timedelta(days=recent_days)).date().isoformat()
        date_keywords.append(f"after:{since_date}")

    # Normalize inputs
    roles = [ _normalize(r) for r in roles if r and r.strip() ]
    location = _normalize(location)

    # Role-level synonyms / short forms for biotech
    synonym_map = {
        "research scientist": ["research scientist", "r&d scientist", "r and d scientist", "r and d"],
        "bioinformatics scientist": ["bioinformatics scientist", "computational biologist", "genomics data scientist"],
        "clinical research associate": ["clinical research associate", "cra"],
        "molecular biologist": ["molecular biologist"],
        "analytical scientist": ["analytical scientist"],
        # you can add more domain-specific synonyms here
    }

    # Helper to expand synonyms: if role exists in map (case-insensitive) use synonyms, else keep original
    def expand_role_variants(role: str) -> List[str]:
        key = role.lower()
        # exact match lookup
        if key in synonym_map:
            return list(dict.fromkeys([_normalize(s) for s in synonym_map[key]]))
        # otherwise return role itself and a lower-case variant
        return [_normalize(role)]

    queries_set: Set[str] = set()

    # Compose queries
    for role in roles:
        role_variants = expand_role_variants(role)

        # also include plain role (no senior token) and quoted role
        role_variants = list(dict.fromkeys(role_variants + [role, f'"{role}"']))

        for rv in role_variants:
            # plain variants + connector forms
            for conn in connectors:
                base = f"{rv} {conn}".strip()
                # Add location appended forms
                loc_forms = [f"{base} in {location}", f"{base} {location}", base]
                # Add seniority variations
                senior_variants = [base] + [f"{st} {base}" for st in seniority_tokens]
                # Create combined queries: seniority x loc x date
                for sv in senior_variants:
                    for lf in loc_forms:
                        # add query without date filter
                        queries_set.add(_normalize(f"{sv} {lf}").strip())
                        # add date variants if enabled
                        if include_date_filters:
                            for dk in date_keywords:
                                queries_set.add(_normalize(f"{sv} {lf} {dk}").strip())

    # Sanitize: remove empties and duplicates, limit to max_queries
    queries = [q for q in queries_set if q and len(q) > 1]

    # Sort for determinism (optional)
    queries.sort()

    # Truncate if too large and keep most diverse entries:
    if len(queries) > max_queries:
        queries = queries[:max_queries]

    return queries


def generate_simple_queries(roles, locations):
    queries = []

    for role in roles:
        for location in locations:
            query = f"{role} senior role in {location}"
            queries.append(query)

    return queries


def test():
    roles = ["Research Scientist", "Bioinformatics Scientist", "Clinical Research Associate"]
    location = "New York, NY"

    qs = generate_job_queries_prod(roles, location, include_date_filters=True, recent_days=30, max_queries=120)

    print(f"Generated {len(qs)} queries")
    for q in qs[:20]:
        print("-", q)



COUNT_FILE = "count.json"

def read_counts():
    """
    Reads the counts from count.json and returns them as a dictionary.
    If the file doesn't exist, it creates one with default values.
    """
    if not os.path.exists(COUNT_FILE):
        data = {"job_id": 0}
        with open(COUNT_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return data

    with open(COUNT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data

def increment_job_count():
    """
    Increments jd_id by 1 in count.json and returns the updated object.
    """
    data = read_counts()
    data["job_id"] = data.get("job_id", 0) + 1

    with open(COUNT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print(f"🔼 job_id incremented to {data['job_id']}")
    return data
