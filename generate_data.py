import json
import os
import random
import datetime

# 1. Setup Output Directory
output_dir = "ingestion_data"
os.makedirs(output_dir, exist_ok=True)

# 2. Define the exact source data from your uploaded file
source_data = {
    "1_Approving_Civil_Aviation_Authority_Country": "FAA/United States",
    "2_Title": "AUTHORIZED RELEASE CERTIFICATE",
    "3_Form_Tracking_Number": "5550019",
    "4_Organization_Name_and_Address": "F. J. Turbine Power, Inc. - PIT, 303 Oshkosh Dr., Bld 1110, Findlay TWP, PA 15231 (FAA Approved Repair Station F7JD192Y)",
    "5_Work_Order_Contract_Invoice_Number": "5550019/860117",
    "6_Item": "1",
    "7_Description": "TURBOFAN ENGINE",
    "8_Part_Number": "CFM56-3C-1",
    "9_Quantity": "1",
    "10_Serial_Number": "860-117",
    "11_Status_Work": "TESTED",
    "12_Remarks": "ACCOMPLISHED ENGINE TEST AS PER CFM56-3, CFMI-TP-SM.5, REV. 81, DATED DECEMBER 15, 2023, MANUFACTURER'S SPECIFICATIONS AND CUSTOMER INSTRUCTIONS. THE FOLLOWING A.D'S WERE COMPLIED WITH / VERIFIED THIS SHOP VISIT: A.D. 2006-26-01-VERIFIED FUEL FILTER P/N ACC462F2038M. TESTED PER CFM56-3 ESM 72-00-00, TEST 002 - ENGINE FUNCTIONAL TEST. PRESERVED FUEL AND OIL SYSTEMS PER CFM56-3 ESM 72-00-00, STORAGE 001, 30-365 DAYS ON 21/FEB/2024. DETAILS OF THE WORK PERFORMED ARE ON FILE UNDER FJ TURBINE POWER, INC.-PIT W/O #5550019. REFER TO OPEN ITEMS LIST FORM PIT 006 FOR CARRY FORWARD ITEMS AND STORAGE DETAILS. REFER TO ENGINE WORK LOG FORM PIT 025 FOR REPLACEMENT ARTICLES INSTALLED. AFTER INSTALLATION, ENGINE REQUIRES ADDITIONAL TESTING PER AMM 71-00-00, AS APPLICABLE. TOTAL TIME AND CYCLES SUPPLIED BY CUSTOMER / OPERATOR: TSN: 53,974.01 CSN: 31,409. Certifies that the work specified in block 11/12 was carried out in accordance with EASA Part-145 and in respect to that work, the component is considered ready for release to service under EASA Part-145, Approval Number: EASA 145.8010",
    "13a_Certifies_Items_Manufactured_In_Conformance": {
        "Approved_Design_Data": False,
        "Non_Approved_Design_Data": False
    },
    "14a_Return_To_Service": {
        "14_CFR_43_9_Return_To_Service": True,
        "Other_Regulation_Specified_In_Block_12": False
    },
    "14b_Authorized_Signature": "Signed",
    "14c_Approval_Certificate_No": "F7JD192Y",
    "14d_Name": "PAUL ANGLIN",
    "14e_Date": "23/FEB/2024"
}

# Write the exact source file (File #1)
with open(f"{output_dir}/01_source_TURBOFAN_ENGINE.json", "w") as f:
    json.dump(source_data, f, indent=4)
print(f"Created: 01_source_TURBOFAN_ENGINE.json")

# 3. Helper Data for Simulation
parts_list = [
    "nozzle", "blade", "HPT Vein", "fusel bolt", 
    "gear shaft", "igniter", "valve", "disks", "gearbox"
]

statuses = ["INSPECTED", "REPAIRED", "OVERHAULED", "MODIFIED"]
names = ["SARAH JENKINS", "MIKE ROSS", "DAVID CHEN", "LISA WONG", "ROBERT MILLER"]

def generate_random_date():
    start_date = datetime.date(2023, 1, 1)
    end_date = datetime.date(2024, 2, 28)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + datetime.timedelta(days=random_number_of_days)
    return random_date.strftime("%d/%b/%Y").upper()

# 4. Generate the 9 Simulated Files
for i, part in enumerate(parts_list, start=2):
    
    # Generate random identifiers
    track_num = str(random.randint(5550020, 5559999))
    wo_num = f"{track_num}/{random.randint(800000, 999999)}"
    # Create Part Number (e.g., NOZ-123-A)
    part_abbr = part[:3].upper()
    part_num = f"{part_abbr}-{random.randint(100,999)}-{random.choice(['A','B','C'])}"
    serial_num = f"{random.randint(100, 999)}-{random.randint(100, 999)}"
    status = random.choice(statuses)
    
    # Create specific remarks based on the part
    remarks = (
        f"ACCOMPLISHED {status} OF {part.upper()} AS PER CMM {random.randint(20, 80)}-{random.randint(10, 50)}-{random.randint(0, 9)}. "
        f"CLEANED AND NDT INSPECTED PER SHOP MANUAL REV {random.randint(10, 99)}. "
        f"REPLACED CONSUMABLES. BENCH TEST PERFORMED SATISFACTORILY. "
        f"DETAILS OF WORK ON FILE UNDER W/O #{track_num}. TSN: {random.randint(1000, 50000)}. CSN: {random.randint(500, 20000)}."
    )

    # Create the new dictionary based on the template
    simulated_doc = source_data.copy()
    simulated_doc["3_Form_Tracking_Number"] = track_num
    simulated_doc["5_Work_Order_Contract_Invoice_Number"] = wo_num
    simulated_doc["6_Item"] = str(i)
    simulated_doc["7_Description"] = part.upper()
    simulated_doc["8_Part_Number"] = part_num
    simulated_doc["9_Quantity"] = str(random.randint(1, 20)) if part.lower() in ["blade", "fusel bolt", "hpt vein"] else "1"
    simulated_doc["10_Serial_Number"] = serial_num
    simulated_doc["11_Status_Work"] = status
    simulated_doc["12_Remarks"] = remarks
    simulated_doc["14d_Name"] = random.choice(names)
    simulated_doc["14e_Date"] = generate_random_date()

    # Create filename
    filename = f"{i:02d}_simulated_{part.replace(' ', '_')}.json"
    
    # Write file
    with open(f"{output_dir}/{filename}", "w") as f:
        json.dump(simulated_doc, f, indent=4)
        
    print(f"Created: {filename}")

print(f"\nAll 10 files have been generated in the '{output_dir}' directory.")