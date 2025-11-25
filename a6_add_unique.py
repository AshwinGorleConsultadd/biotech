import json
import random
import string

def add_random_to_company_uid(input_file="output/collection.json", output_file="output/unique_collection.json"):
    # Load the JSON file
    with open(input_file, "r") as f:
        data = json.load(f)

    # Ensure data is a list of objects
    if not isinstance(data, list):
        raise ValueError("Input JSON must contain an array of objects!")

    # Function to generate random 7-character alphanumeric string
    def random_code(length=7):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    # Modify each object
    for item in data:
        if "company_uid" in item:
            item["company_uid"] = item["company_uid"] + random_code()
        else:
            print("Warning: object missing 'company_uid' field:", item)

    # Save output
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)

    print(f"✔ Successfully saved updated data to '{output_file}'")

# Run the function
add_random_to_company_uid()
