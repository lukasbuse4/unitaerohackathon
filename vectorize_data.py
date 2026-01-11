import os
import json
import voyageai
from pymongo import MongoClient
import certifi

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# 1. MongoDB Connection (Paste the same one you used before)
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0"

# 2. Voyage AI API Key (Get this from the Partner Toolkit)
VOYAGE_API_KEY = "pa-2D4iY2lUhQjxSO83kRqYLaWpwPf4moS3eERVW7s0Wv0"

# ---------------------------------------------------------
# MAIN SCRIPT
# ---------------------------------------------------------
def create_embeddings():
    print("--- CONNECTING ---")
    
    # Connect to MongoDB
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client["aviation_hackathon"]
    collection = db["inventory"]
    
    # Connect to Voyage AI
    vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    
    # Fetch all documents that don't have an embedding yet
    cursor = collection.find({"embedding": {"$exists": False}})
    docs = list(cursor)
    
    if not docs:
        print("All documents are already vectorized!")
        return

    print(f"Found {len(docs)} documents to vectorize...")

    for doc in docs:
        # We want to embed the 'Remarks' because that's where the rich context is
        text_to_embed = doc.get("12_Remarks", "")
        
        # Combine with Description for better context
        full_text = f"{doc.get('7_Description', '')}: {text_to_embed}"
        
        try:
            # Generate Embedding (Model: voyage-2 is standard)
            print(f"Vectorizing: {doc.get('7_Description')}...")
            result = vo.embed([full_text], model="voyage-2", input_type="document")
            vector = result.embeddings[0]
            
            # Update the document in MongoDB with the new 'embedding' field
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"embedding": vector}}
            )
        except Exception as e:
            print(f"Error vectorizing {doc['_id']}: {e}")

    print("\n🚀 SUCCESS: All documents now have Vector Embeddings!")

if __name__ == "__main__":
    if "PASTE_YOUR" in VOYAGE_API_KEY:
        print("❌ STOP: You need to paste your Voyage AI API Key in line 14.")
    else:
        create_embeddings()