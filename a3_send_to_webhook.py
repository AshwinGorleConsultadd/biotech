
from operator import truediv
import os
import json
import time
import requests
from utils import read_counts, increment_job_count

def send_to_webhook_wrapper(file_path = "output/3_jobs_with_domains.json"):
    
    limit = False
    limit_count = 2
    #Check file exists
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    # Load the JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if limit :
        data = data[0:limit_count]
        print("limited data : ", limit_count , data)

    send_json_to_webhook(data)



def send_json_to_webhook(data):
    """
    Send each filtered JSON object individually to a webhook endpoint with a short delay.

    Args:
        file_path (str): Path to the local JSON file containing LinkedIn profiles
        webhook_url (str): Webhook URL to send the data to
    """
    webhook_url = "https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-8bfc370e-1e95-4f21-9734-6befd731b61e"

    

    # Filter data fields
    filteredData = []
    for record in data:
        obj = {
            "company_uid": record.get("company_uid"),
            "company_name": record.get("company_name"),
            "company_domain": record.get("company_domain")
        }
        filteredData.append(obj)

    # Save filtered data for referencesite:linkedin.com/in/ \"PE firm Consultant Low Voltage Electrical Contracting in united state\"
    os.makedirs("output", exist_ok=True)
    with open("output/4_data_sent_to_hook.json", "w", encoding="utf-8") as f:
        json.dump(filteredData, f, ensure_ascii=False, indent=2)

    print(f"📦 Sending {len(filteredData)} profiles to webhook (one by one)...")

    # Send each record one by one with delay
    success_count = 0
    fail_count = 0

    for idx, record in enumerate(filteredData, start=1):
        try:
            counters = read_counts()
            print("counters : ", counters)
            record["count"] = counters["job_id"]
            response = requests.post(
                webhook_url,
                json=record,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 200:
                print(f"✅ [{idx}/{len(filteredData)}] Sent: {record.get('firstName', '')} {record.get('lastName', '')}")
                success_count += 1
                increment_job_count()
            else:
                print(f"⚠️ [{idx}/{len(filteredData)}] Failed ({response.status_code}): {response.text}")
                fail_count += 1

        except requests.exceptions.RequestException as e:
            print(f"❌ [{idx}/{len(filteredData)}] Error sending record: {e}")
            fail_count += 1

        # Delay between requests
        time.sleep(0.2)

    print(f"\n✅ Done! Successfully sent {success_count} profiles, {fail_count} failed.")


# Example usage
if __name__ == "__main__":
    # send_json_to_webhook(data)
    send_to_webhook_wrapper()
