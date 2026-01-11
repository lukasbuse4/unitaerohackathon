import json
import os
from pymongo import MongoClient
import sys
import certifi  # <--- NEW IMPORT

# ---------------------------------------------------------
# PASTE YOUR CONNECTION STRING HERE
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0" 

INPUT_DIR = "ingestion_data"
DB_NAME = "aviation_hackathon"
COLLECTION_NAME = "inventory"

print("--- SCRIPT STARTED ---")

def load_data():
    print(f"Attempting to connect to MongoDB...")
    
    try:
        # FIX ADDED HERE: tlsCAFile=certifi.where()
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where())
        
        # This command forces a connection check
        client.admin.command('ping')
        print("✅ SUCCESS: Connected to MongoDB!")
        
    except Exception as e:
        print(f"❌ ERROR: Could not connect to MongoDB.\nReason: {e}")
        return

    # Database Setup
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    # Clear old data
    print("Clearing old data...")
    try:
        collection.delete_many({})
    except Exception as e:
        print(f"Warning clearing data: {e}")

    # Read Files
    documents_to_insert = []
    print(f"Reading files from '{INPUT_DIR}'...")
    
    if not os.path.exists(INPUT_DIR):
        print(f"❌ ERROR: Directory '{INPUT_DIR}' not found.")
        return

    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(INPUT_DIR, filename)
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                
                # Add metadata
                data["_hackathon_metadata"] = {
                    "source": "simulated_script",
                    "original_filename": filename
                }
                documents_to_insert.append(data)
            except Exception as e:
                print(f"Skipping {filename}: {e}")

    # Bulk Insert
    if documents_to_insert:
        try:
            result = collection.insert_many(documents_to_insert)
            print(f"🚀 DONE! Inserted {len(result.inserted_ids)} documents.")
        except Exception as e:
            print(f"❌ Insert Error: {e}")
    else:
        print("⚠️ No JSON files found to insert.")

if __name__ == "__main__":
    if "YOUR_CONNECTION_STRING" in MONGO_URI:
        print("❌ STOP: You need to paste your actual MongoDB Connection String in line 10.")
    else:
        load_data()