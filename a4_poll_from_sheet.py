import pandas as pd
import json
import os
import time
from datetime import datetime


def get_google_sheet_as_df(sheet_url: str) -> pd.DataFrame:
    """
    Reads a public Google Sheet as a pandas DataFrame (via its CSV export link).
    """
    
    if "/edit" in sheet_url:
        base_url = sheet_url.split("/edit")[0]
        csv_url = f"{base_url}/export?format=csv"
    else:
        csv_url = sheet_url

    return pd.read_csv(csv_url)


def poll_google_sheet(
    sheet_url: str,
    previous_record_count: int,
    new_records_expected: int,
    poll_interval: int = 4,
    output_path: str = "output/enriched_records.json"
):
    """
    Polls a public Google Sheet until new records appear and saves them to a JSON file.

    Args:
        sheet_url (str): The Google Sheet public URL.
        previous_record_count (int): Number of records already present before update.
        new_records_expected (int): Number of new records expected to be added.
        poll_interval (int): Polling interval in seconds.
        output_path (str): Where to save the fetched new records.
    """
    #---------------------Adjusting header coount in previous records-----------
    previous_record_count = previous_record_count

    print(f"📊 Starting polling for Google Sheet updates...")
    print(f"🔗 Sheet URL: {sheet_url}")
    print(f"⏱️ Poll Interval: {poll_interval}s")
    print(f"🧾 Waiting for {new_records_expected} new records after row {previous_record_count}...\n")

    total_required = previous_record_count + new_records_expected + 1
    attempt = 0
    print("total_required", total_required)

    while True:
        attempt += 1
        try:
            df = get_google_sheet_as_df(sheet_url)
            current_count = len(df)
            print("current_count ", current_count)

            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] 🌀 Attempt {attempt}: Found {current_count} total rows...")

            if current_count < previous_record_count:
                print(f"⚠️ Detected fewer rows than expected ({current_count}). The sheet may have been reset. ({previous_record_count})")
            elif current_count >= total_required:
                print(f"✅ All {new_records_expected} new records detected! Fetching now...")
                new_df = df.iloc[previous_record_count:current_count]
                records = new_df.to_dict(orient="records")

                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(records, f, ensure_ascii=False, indent=2)

                print(f"💾 Saved {len(records)} new records to '{output_path}'")
                print("🎉 Polling completed successfully!\n")
                
                return records

            else:
                remaining = total_required - current_count
                print(f"⏳ Still waiting for {remaining} more records...")

        except Exception as e:
            print(f"❌ Error fetching sheet (attempt {attempt}): {e}")

        time.sleep(poll_interval)


def test(sheet_url):
    df = get_google_sheet_as_df(sheet_url)
    current_count = len(df)
    print("record in sheet", current_count)

if __name__ == "__main__":
    sheet_url = "https://docs.google.com/spreadsheets/d/1Wf9lon4r41BdgkFL4QFSry9hfFdorlFqpAXgJdbuXwM/edit?gid=0#gid=0"
    previous_records = 14      # Number of rows before Code X updates
    expected_new_records = 4   # Number of rows Code X will add

    test(sheet_url)
    # poll_google_sheet(
    #     sheet_url=sheet_url,
    #     previous_record_count=previous_records,
    #     new_records_expected=expected_new_records,
    #     poll_interval=4,
    #     output_path="output/6_enriched_records.json"
    # )

