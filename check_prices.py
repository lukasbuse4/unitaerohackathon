import json
import os

# Header for the table
print(f"{'PART':<20} | {'PRICE':<15}")
print("-" * 35)

# Loop through files and print data
for filename in os.listdir("ingestion_data"):
    if filename.endswith(".json"):
        with open(f"ingestion_data/{filename}", "r") as f:
            data = json.load(f)
            description = data.get('7_Description', 'Unknown')
            price = data.get('15_Price', 'N/A')
            print(f"{description:<20} | {price}")