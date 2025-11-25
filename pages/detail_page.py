import streamlit as st
import json
import os
import html

st.set_page_config(page_title="Job Details", layout="wide")

DATA_FILE = "output/unique_collection.json"

# ------------------------------------------------------------------
# 1. Check if user clicked a job in the table
# ------------------------------------------------------------------
if "selected_company_uid" not in st.session_state:
    st.error("No job selected. Please return to the job list.")
    st.stop()

selected_uid = st.session_state["selected_company_uid"]

# ------------------------------------------------------------------
# 2. Load all jobs again (because app.py only sent UID)
# ------------------------------------------------------------------
if not os.path.exists(DATA_FILE):
    st.error("❌ Could not load job dataset.")
    st.stop()

with open(DATA_FILE, "r", encoding="utf-8") as f:
    all_jobs = json.load(f)

# Find the matching job
job = next((j for j in all_jobs if j.get("company_uid") == selected_uid), None)

if job is None:
    st.error("❌ Selected job not found in dataset.")
    st.stop()

company = job.get("company_details") or {}

# ------------------------------------------------------------------
# Helper
# ------------------------------------------------------------------
def clean(text):
    return text if text else ""

def print_metric(label, value):
    st.markdown(
        f"""
        <div style="padding:12px; border-radius:10px; 
                     background:#F8F9FA; border:1px solid #EEE;
                     font-size:15px; margin-bottom:10px;">
            <b>{label}</b><br>
            <span style="font-size:18px; color:#111;">{value}</span>
        </div>
        """,
        unsafe_allow_html=True
    )

# ------------------------------------------------------------------
# PAGE HEADER
# ------------------------------------------------------------------
st.markdown("### 🔙 [Back to Job Listings](../app.py)")

# ------------------------------------------------------------------
# Company Info Card
# ------------------------------------------------------------------
st.markdown("## Company Overview")

thumbnail = job.get("thumbnail")

col1, col2 = st.columns([1, 5])

with col1:
    if thumbnail:
        st.image(thumbnail, width=120)

with col2:
    st.markdown(f"""
        <div style="font-size:26px; font-weight:700;">{company.get("company_name", job.get("company_name", ""))}</div>
        <div style="font-size:16px; margin-top:4px; color:#444;">
            {company.get("industry", "Industry not available")}
        </div>
        <div style="font-size:14px; color:#666;">
            {company.get("size", "")} • {company.get("employee_count", "")} employees
        </div>
        <div style="font-size:14px; margin-top:4px;">
            🌍 {company.get("address_locations", company.get("locality", ""))}
        </div>
        <div style="font-size:14px;">
            🔗 <a href="{company.get('url', '')}" target="_blank">{company.get('url', '')}</a>
        </div>
        <div style="font-size:14px; color:#666; margin-top:6px;">
            Domain: {company.get("company_domain", job.get("company_domain", ""))}
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------------
# Job Summary Section
# ------------------------------------------------------------------
st.markdown("## Job Summary")

salary = job.get("detected_extensions", {}).get("salary", "Not specified")
experience = job.get("experience_required", "Not specified")
schedule = job.get("detected_extensions", {}).get("schedule", "")
posted = job.get("detected_extensions", {}).get("posted_at", "")
via = job.get("via", "")
location = job.get("location", "")
source_query = job.get("source_query", "")

summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    print_metric("💰 Salary", salary)
    print_metric("📍 Location", location)

with summary_col2:
    print_metric("🎓 Experience Required", experience)
    print_metric("🗓 Schedule", schedule)

with summary_col3:
    print_metric("⏳ Posted", posted)
    print_metric("🔎 Job Role Query", source_query)

# APPLY LINKS
st.markdown("### Apply Links")
for link in job.get("apply_links", []):
    url = link.get("link")
    src = link.get("source")
    if url:
        st.markdown(f"- [{src}]({url})")

st.markdown("---")

# ------------------------------------------------------------------
# Job Description
# ------------------------------------------------------------------
st.markdown("## Job Description")
st.write(job.get("description", ""))

st.markdown("---")

# ------------------------------------------------------------------
# Job Highlights
# ------------------------------------------------------------------
st.markdown("## Job Highlights")

for section in job.get("job_highlights", []):
    title = section.get("title")
    items = section.get("items", [])

    st.markdown(f"### {title}")

    for item in items:
        st.markdown(f"- {item}")

    st.markdown("<br>", unsafe_allow_html=True)

st.markdown("---")

# ------------------------------------------------------------------
# Company Description
# ------------------------------------------------------------------
st.markdown("## About the Company")
st.write(company.get("description", "No company description available."))

st.markdown("---")

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------
st.success("End of details. Use the Back button at the top to return.")
