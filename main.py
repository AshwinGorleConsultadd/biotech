import os 
from a4_poll_from_sheet import poll_google_sheet
from utils import read_counts
from a1_get_jobs import fetch_jobs_wrapper
from a2_get_jobs_domain import append_company_domains
from a3_send_to_webhook import send_to_webhook_wrapper
from a5_merge_company_job import attach_company_details
import json

def execute():
    roles = ["supply Chain Biotech-focused job"]
    locations = ["united states"]
    
    # #step 1: fetching jobs
    # jobs = fetch_jobs_wrapper(
    #     roles,
    #     locations,
    #     jobs_per_query=10
    # )
    
    # step 2: find domain of companies
    with open("output/2_fetched_jobs.json", "r", encoding='utf-8') as f:
        jobs = json.load(f)

    domain_enriched_jobs = append_company_domains(jobs)


    with open("output/3_jobs_with_domains.json", "r", encoding="utf-8") as f:
        data_loaded = json.load(f)
        expected = len(data_loaded)

    # step 3; send to web hook
    counter = read_counts()
    send_to_webhook_wrapper()

    #step 4: poll from webhook
    prev_records= counter["job_id"]
    poll_google_sheet(sheet_url="https://docs.google.com/spreadsheets/d/1Wf9lon4r41BdgkFL4QFSry9hfFdorlFqpAXgJdbuXwM/edit?gid=0#gid=0",
                     previous_record_count=prev_records,
                     new_records_expected=expected,
                     output_path="output/5_enriched_compnay.json")
    


    #step 5: merging job and company details
    attach_company_details()



execute()