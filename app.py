import streamlit as st
import pandas as pd
import json
import os
import re
st.set_page_config(page_title="Biotech Jobs", layout="wide")

st.title("🔬 Biotech Job Listings")

# -----------------------------------------
# Load processed jobs (6_final.json)
# -----------------------------------------
FILE_PATH = "output/unique_collection.json"

if not os.path.exists(FILE_PATH):
    st.error("❌ 6_final.json not found. Run the pipeline first.")
    st.stop()

with open(FILE_PATH, "r", encoding="utf-8") as f:
    jobs = json.load(f)

if not jobs:
    st.warning("No job data available.")
    st.stop()


# -----------------------------------------
# Helpers
# -----------------------------------------

def clean_job_role(text):
    if not text:
        return ""

    text = text.lower()

    # Remove "job" or "jobs"
    text = re.sub(r"\bjobs?\b", "", text)

    # Remove "in ..." and everything after
    text = re.sub(r"\bin\s+.*", "", text)

    # Cleanup spaces
    text = text.strip()
    text = " ".join(text.split())  # remove multiple spaces

    # Restore title casing
    return text.title()

def truncate(text, length=40):
    if text is None:
        return ""

    # Convert non-string types to string
    if not isinstance(text, str):
        try:
            text = str(text)
        except:
            return ""

    text = text.strip()

    return text if len(text) <= length else text[:length] + "..."



def apply_link_icons(apply_links):
    if not apply_links:
        return ""
    icons = ""
    for i, item in enumerate(apply_links):
        icons += f"🔗 "
    return icons


# -----------------------------------------
# Convert jobs to a DataFrame for table
# -----------------------------------------
table_rows = []

for job in jobs:
    comp = job.get("company_details") or {}

    table_rows.append({
        "company_uid": job.get("company_uid"),
        "thumbnail": job.get("thumbnail", None),
        "title": truncate(job.get("title")),
        "company_name": truncate(job.get("company_name")),
        "location": job.get("location"),
        "via": job.get("via"),
        "source_query": clean_job_role(job.get("source_query")),
        "posted_at": job["detected_extensions"].get("posted_at"),
        "schedule": job["detected_extensions"].get("schedule"),
        "salary": job["detected_extensions"].get("salary"),
        "linkedin": comp.get("url", ""),
        "experience_required": job.get("experience_required"),
        "apply_links": job.get("apply_links"),
        "address_locations": comp.get("address_locations")
    })

df = pd.DataFrame(table_rows)


# -----------------------------------------
# FILTERS
# -----------------------------------------
with st.expander("🔎 Filters", expanded=True):
    col_f1, col_f2, col_f3, col_f4= st.columns(4)

    with col_f1:
        selected_schedule = st.multiselect(
            "Schedule", 
            options=sorted(df["schedule"].dropna().unique())
        )

    with col_f2:
        selected_location = st.multiselect(
            "Location", 
            options=sorted(df["location"].dropna().unique())
        )

    with col_f3:
        selected_posted = st.multiselect(
            "Posted At",
            options=sorted(df["posted_at"].dropna().unique())
        )

    with col_f4:
        selected_role = st.multiselect(
            "Role",
            options=sorted(df["source_query"].dropna().unique())
        )


# Apply filters
filtered_df = df.copy()

if selected_schedule:
    filtered_df = filtered_df[filtered_df["schedule"].isin(selected_schedule)]

if selected_location:
    filtered_df = filtered_df[filtered_df["location"].isin(selected_location)]

if selected_posted:
    filtered_df = filtered_df[filtered_df["posted_at"].isin(selected_posted)]

if selected_role:
    filtered_df = filtered_df[filtered_df["source_query"].isin(selected_role)]


# -----------------------------------------
# SORTING
# -----------------------------------------
sorting_option = st.selectbox(
    "Sort by",
    ["None", "posted_at (Newest First)", "posted_at (Oldest First)"]
)

if sorting_option == "posted_at (Newest First)":
    filtered_df = filtered_df.sort_values(by="posted_at", ascending=False)

elif sorting_option == "posted_at (Oldest First)":
    filtered_df = filtered_df.sort_values(by="posted_at", ascending=True)


# -----------------------------------------
# TABLE DISPLAY
# -----------------------------------------
st.write("### 📄 Job Results")

# Custom layout for table
for idx, row in filtered_df.iterrows():
    company_uid = row["company_uid"]
    
    job_obj = next((j for j in jobs if j["company_uid"] == company_uid), None)
    if not job_obj:
        continue

    col_view, col_table = st.columns([1, 10])

    # ------------------- VIEW BUTTON -------------------
    with col_view:
        if st.button("View", key=f"view_{company_uid}"):
            st.session_state["selected_company_uid"] = company_uid
            st.switch_page("pages/detail_page.py")

    # ------------------- Thumbnail -------------------
    # with col_thumb:
    #     if row["thumbnail"]:
    #         st.image(row["thumbnail"], width=40)

    # ------------------- Main Table Row -------------------
    with col_table:
        display_row = {
            "Title": row["title"],
            "Company": row["company_name"],
            "Location": row["location"],
            "Via": truncate(row["via"]),
            "Job Role": clean_job_role(row["source_query"]),
            "Posted": row["posted_at"],
            "Schedule": row["schedule"],
            "Salary": row["salary"],
            "LinkedIn": row["linkedin"] if row["linkedin"] else "",
            "Experience": row["experience_required"],
            "Apply": apply_link_icons(row["apply_links"]),
            "Address": truncate(row["address_locations"], 45)
        }

        st.dataframe(pd.DataFrame([display_row]), use_container_width=True)

st.success("Loaded successfully.")

# -----------------------------------------
# TABLE DISPLAY – ONE SINGLE HTML TABLE
# -----------------------------------------






# st.write("### 📄 Job Results")

# # Hidden widget for JS → Streamlit communication
# uid_input = st.text_area(
#     "",
#     key="uid_receiver",
#     label_visibility="collapsed",
#     height=1
# )

# # Build HTML table header
# table_html = """
# <style>
# .table-job {
#     width: 100%;
#     border-collapse: collapse;
#     margin-top: 10px;
# }
# .table-job th {
#     background: #f5f5f5;
#     padding: 8px;
#     border-bottom: 1px solid #ddd;
#     font-weight: bold;
#     font-size: 14px;
# }
# .table-job td {
#     padding: 8px;
#     border-bottom: 1px solid #eee;
#     font-size: 14px;
# }
# .table-job tr:hover {
#     background: #fafafa;
# }
# .view-btn {
#     color: #0356e8;
#     cursor: pointer;
#     font-weight: 600;
# }
# </style>

# <table class="table-job">
# <tr>
#     <th>View</th>
#     <th>Title</th>
#     <th>Company</th>
#     <th>Location</th>
#     <th>Via</th>
#     <th>Job Role</th>
#     <th>Posted</th>
#     <th>Schedule</th>
#     <th>Salary</th>
#     <th>LinkedIn</th>
#     <th>Experience</th>
#     <th>Apply</th>
#     <th>Address</th>
# </tr>
# """

# # Build rows
# for idx, row in filtered_df.iterrows():
#     uid = row["company_uid"]

#     view_cell = f"""
#         <span class='view-btn' onclick="VIEW_BUTTON_JS('{uid}')">
#             View
#         </span>
#     """

#     table_html += f"""
#     <tr>
#         <td>{view_cell}</td>
#         <td>{row['title']}</td>
#         <td>{row['company_name']}</td>
#         <td>{row['location']}</td>
#         <td>{row['via']}</td>
#         <td>{clean_job_role(row['source_query'])}</td>
#         <td>{row['posted_at']}</td>
#         <td>{row['schedule']}</td>
#         <td>{row['salary']}</td>
#         <td>{row['linkedin']}</td>
#         <td>{row['experience_required']}</td>
#         <td>{apply_link_icons(row['apply_links'])}</td>
#         <td>{truncate(row['address_locations'], 45)}</td>
#     </tr>
#     """

# table_html += "</table>"

# # Render HTML with a JS function that sends back the UID
# clicked_uid = st.components.v1.html(
#     f"""
#     <script>
#     function VIEW_BUTTON_JS(uid) {{
#         const textarea = window.parent.document.getElementById("uid_receiver");
#         if (textarea) {{
#             textarea.value = uid;
#             textarea.dispatchEvent(new Event("input", {{ bubbles: true }}));
#         }}
#     }}
#     </script>

#     {table_html}
#     """,
#     height=650,
# )

# # If UID received → redirect to detail page
# if st.session_state.get("uid_receiver"):
#     uid = st.session_state["uid_receiver"]
#     st.session_state["selected_company_uid"] = uid
#     st.switch_page("pages/detail_page.py")
