import sys
print("--- SCRIPT STARTING ---") # If you don't see this, you didn't save the file!

from pymongo import MongoClient
import certifi

# ---------------------------------------------------------
# PASTE YOUR REAL CONNECTION STRING HERE
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0y"

def check_connection():
    print("1. Attempting to connect...")
    
    # We add a 5-second timeout so it doesn't hang forever
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        
        # Force a check
        client.admin.command('ping')
        print("✅ Connection Successful!")
        
        db = client["aviation_hackathon"]
        collection = db["inventory"]

        print("2. Counting documents...")
        total_count = collection.count_documents({})
        vector_count = collection.count_documents({"embedding": {"$exists": True}})

        print(f"\n--- RESULTS ---")
        print(f"Total Parts in DB:      {total_count}")
        print(f"Vectorized Parts:       {vector_count}")
        
        if total_count == 0:
            print("❌ ALERT: Database is empty. You need to run 'load_to_mongo.py' first.")
        elif vector_count == 0:
            print("❌ ALERT: Data exists but NO VECTORS. Run 'vectorize_data.py'.")
        else:
            print("✅ STATUS: Data is ready for search!")

    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: {e}")
        print("Possible causes:")
        print("1. You are using the PLACEHOLDER connection string.")
        print("2. Your IP address is not whitelisted in MongoDB Atlas.")

if __name__ == "__main__":
    if "cluster0.abcd" in MONGO_URI:
        print("❌ STOP: You are using the placeholder URI. Paste your real one in line 8!")
    else:
        check_connection()