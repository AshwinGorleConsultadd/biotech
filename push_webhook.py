import requests
import time

def push_to_clay_webhook(data_list, webhook_url):
    """
    Push objects one-by-one to Clay webhook.

    Args:
        data_list (list): Array of objects to send
        webhook_url (str): Clay webhook URL
    """

    headers = {
        "Content-Type": "application/json"
    }

    for item in data_list:
        try:
            response = requests.post(webhook_url, json=item, headers=headers)

            if response.status_code == 200:
                print(f"✔ Successfully pushed: {item}")
            else:
                print(f"❌ Failed for {item}, Status: {response.status_code}, Response: {response.text}")

        except Exception as e:
            print(f"❌ Error sending {item}: {e}")

        # Optional small delay to avoid rate limits
        time.sleep(0.3)


# ----------------------------------------
# Example usage
# ----------------------------------------

data = [
    { "id": 1, "company_name": "Columbia Threadneedle Investments" },
    { "id": 2, "company_name": "Columbia Threadneedle" },
    { "id": 3, "company_name": "Andiamo" },
    { "id": 4, "company_name": "CyberCoders" }
]

webhook_url = "https://api.clay.com/v3/sources/webhook/pull-in-data-from-a-webhook-8bfc370e-1e95-4f21-9734-6befd731b61e"

push_to_clay_webhook(data, webhook_url