import voyageai
from pymongo import MongoClient
import certifi
import time

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0"
VOYAGE_API_KEY = "pa-2D4iY2lUhQjxSO83kRqYLaWpwPf4moS3eERVW7s0Wv0"

def fix_ghost_assets():
    # 1. Connect with Timeout
    print("2. Attempting to connect to MongoDB...")
    try:
        # Added a 5-second timeout so it doesn't hang forever
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
        
        # Test the connection immediately
        client.admin.command('ping')
        print("   ✅ Connected to Server successfully!")
        
        collection = client["aviation_hackathon"]["inventory"]
        vo = voyageai.Client(api_key=VOYAGE_API_KEY)
        
    except Exception as e:
        print(f"\n❌ CONNECTION ERROR: Could not connect to MongoDB.\nDetails: {e}")
        print("\nPossible fixes:\n - Check your internet.\n - Check if your IP is whitelisted on MongoDB Atlas.")
        return

    # 2. Find Ghosts
    print("3. Scanning for Ghost Assets...")
    try:
        ghosts = list(collection.find({"embedding": {"$exists": False}}))
    except Exception as e:
        print(f"❌ DATABASE READ ERROR: {e}")
        return
    
    count = len(ghosts)
    if count == 0:
        print("\n✅ RESULT: No Ghost Assets found! All items are already vectorized.")
        return

    print(f"\n👻 Found {count} Ghost Assets. Fixing them now...")

    # 3. Vectorize and Update
    for i, doc in enumerate(ghosts):
        print(f"   [{i+1}/{count}] Processing: {doc.get('7_Description', 'Unknown Part')}")
        
        try:
            # Create text to embed
            text_to_embed = f"{doc.get('7_Description')} {doc.get('12_Remarks')} {doc.get('15_Price')}"
            
            # Call AI
            vector = vo.embed([text_to_embed], model="voyage-2", input_type="document").embeddings[0]
            
            # Update Database
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"embedding": vector}}
            )
            print("     ✨ Fixed!")
            
        except Exception as e:
            print(f"     ❌ Failed on this item: {e}")

    print("\n🎉 MISSION COMPLETE: All assets are now visible to the AI.")

if __name__ == "__main__":
    fix_ghost_assets()