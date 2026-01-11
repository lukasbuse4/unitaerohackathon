import json
import os
import random

# Directory where your files are located
input_dir = "ingestion_data"

# Pricing logic
price_ranges = {
    "TURBOFAN ENGINE": (2500000, 8000000), 
    "NOZZLE": (45000, 120000),
    "BLADE": (2500, 8000),
    "HPT VEIN": (12000, 45000),
    "FUSEL BOLT": (150, 600),
    "GEAR SHAFT": (25000, 65000),
    "IGNITER": (1500, 4000),
    "VALVE": (5000, 18000),
    "DISKS": (80000, 250000),
    "GEARBOX": (150000, 400000)
}

def get_price_for_part(part_name):
    low, high = (1000, 5000) 
    for key, val in price_ranges.items():
        if key.lower() in part_name.lower():
            low, high = val
            break
    price = random.uniform(low, high)
    return f"${price:,.2f}"

# Process all files
print(f"Updating files in '{input_dir}'...\n")

if os.path.exists(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            filepath = os.path.join(input_dir, filename)
            
            with open(filepath, "r") as f:
                data = json.load(f)
                
            part_desc = data.get("7_Description", "UNKNOWN")
            price = get_price_for_part(part_desc)
            data["15_Price"] = price
            
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
                
            print(f"Updated {filename}: {part_desc} -> {price}")
else:
    print(f"Error: Directory '{input_dir}' not found.")

print("\nSuccess: All files now have pricing data.")