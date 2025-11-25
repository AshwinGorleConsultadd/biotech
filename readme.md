# 🔬 Biotech Job Aggregator & Enrichment Pipeline

This project automatically fetches biotech senior-level job listings from Google Jobs API, enriches company data using Clay, resolves company domains, and provides a full Streamlit UI to explore and filter results.

---

# 🚀 Features

### ✔ Fetch jobs from SearchAPI (Google Jobs Engine)  
### ✔ Generate job UIDs & company UIDs  
### ✔ Generate search queries dynamically  
### ✔ Resolve company domains (OpenAI/Gemini based lookup)  
### ✔ Send companies to Clay via Webhook for enrichment  
### ✔ Poll enriched data from Google Sheet → save locally  
### ✔ Combine job + company enriched data  
### ✔ Streamlit App  
- Filters  
- Sorting  
- Single unified table  
- Clickable row actions  
- Full detail page (company + job breakdown)

---

# 📁 Project Structure

biotech/
│
├── a1_fetch_jobs.py
├── a2_get_jobs_domain.py
├── a3_send_webhook_clay.py
├── a4_poll_google_sheet.py
├── a5_merge_company_data.py
│
├── output/
│ ├── 1_raw_jobs.json
│ ├── 2_generate_queries.json
│ ├── 3_jobs_with_domains.json
│ ├── 4_clay_webhook_sent.json
│ ├── 5_enriched_company.json
│ ├── 6_final.json ← FINAL merged output used by UI
│
├── app.py ← Streamlit UI (table)
└── pages/
└── detail_page.py ← Detailed job + company view



---

# 🧩 Requirements

Install dependencies:

🔧 Environment Variables

Create a .env file in the project root:

SEARCHAPI_KEY=your_searchapi_key
GEMINI_API_KEY=your_gemini_or_openai_key
GOOGLE_SERVICE_ACCOUNT_JSON=path_to_service_account_file.json
CLAY_WEBHOOK_URL=your_clay_webhook_url
GOOGLE_SHEET_ID=your_google_sheet_id



🏗 Pipeline Steps (How Data Flows)
1️⃣ Fetch Jobs

Uses SearchAPI (google_jobs engine):

python a1_fetch_jobs.py


Output → output/1_raw_jobs.json

2️⃣ Resolve Company Domains

Minimal LLM calls (OpenAI or Gemini):

python a2_get_jobs_domain.py


Output → output/3_jobs_with_domains.json

3️⃣ Send Companies to Clay Webhook

Clay enriches company data:

python a3_send_webhook_clay.py


Output → output/4_clay_webhook_sent.json

4️⃣ Poll Google Sheet for Clay Results

Clay enrichment data is written to a Google Sheet:

python a4_poll_google_sheet.py


Output → output/5_enriched_company.json

5️⃣ Merge Job + Company Data

Matches via company_uid and normalizes field names:

python a5_merge_company_data.py


Final output → output/6_final.json

This file powers the UI.

🖥 Run the Streamlit App
streamlit run app.py


This opens the UI with:

One unified job table

Clickable “View” button

Filters (Location, Schedule, Role, Posted At)

Sorting

Icons for apply links

Smart role parsing

Detail page for each job

📝 Detail Page (pages/detail_page.py)

Displays:

🏢 Company Section (Top)

Name

Domain

LinkedIn

Industry

Employee count

Address

Description

📄 Job Section

Title

Job role

Location

Salary

Experience required

Posted at

Schedule

Full job description

Job highlights (Qualifications / Responsibilities / Benefits)

Apply links

Thumbnail

🧪 Troubleshooting
❌ TypeError: object of type 'float' has no len()

Use safe truncate helper to avoid NaN/float issues.

❌ StreamlitInvalidHeightError

Change hidden textarea height from 0 → 1.

❌ View button not clicking

JS → Streamlit bridge must be included (already handled in latest code).

📦 Future Improvements (Optional)

Pagination

Save UI filters in session

Export table to CSV

Add AI summary of each job

Add relevance ranking