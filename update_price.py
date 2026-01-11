from pymongo import MongoClient
import certifi

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0"
DB_NAME = "aviation_hackathon"
COLLECTION_NAME = "inventory"

def update_engine_price():
    # 1. Connect to Database
    print("🔌 Connecting to MongoDB...")
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        collection = client[DB_NAME][COLLECTION_NAME]
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        return

    # 2. Define the Change
    # Find the part named "TURBOFAN ENGINE"
    filter_query = {"7_Description": "TURBOFAN ENGINE"}
    
    # Set the NEW Price
    update_operation = {"$set": {"15_Price": "$313,129.02"}}

    # 3. Execute Update
    result = collection.update_one(filter_query, update_operation)

    # 4. Report Success
    if result.modified_count > 0:
        print("\n✅ SUCCESS: 'TURBOFAN ENGINE' is now priced at $313,129.02")
    elif result.matched_count > 0:
        print("\n⚠️ MATCH FOUND, BUT NO CHANGE: The price was already $313,129.02.")
    else:
        print("\n❌ FAILURE: Could not find 'TURBOFAN ENGINE' in the database.")

if __name__ == "__main__":
    update_engine_price()