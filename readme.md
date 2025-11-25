# 🔬 Biotech Job Aggregator & Enrichment Pipeline

url: https://consultadd.streamlit.app/

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



# Pipeline Steps (How Data Flows)
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

#Run the Streamlit App
   streamlit run app.py

