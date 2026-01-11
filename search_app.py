import voyageai
from pymongo import MongoClient
import certifi

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
MONGO_URI = "mongodb+srv://lukebuse_db:6236Emontecito$@cluster0.e665k0d.mongodb.net/?appName=Cluster0"
VOYAGE_API_KEY = "pa-2D4iY2lUhQjxSO83kRqYLaWpwPf4moS3eERVW7s0Wv0"

def get_price_value(item):
    """
    Helper function to clean '$' symbols and convert text to numbers.
    """
    price_str = item.get('15_Price', '0')
    if not isinstance(price_str, str):
        return 0.0
    # Remove '$' and ',' then convert to float
    clean_price = price_str.replace('$', '').replace(',', '')
    try:
        return float(clean_price)
    except ValueError:
        return 0.0

def search_inventory(query):
    # 1. Connect
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        collection = client["aviation_hackathon"]["inventory"]
        vo = voyageai.Client(api_key=VOYAGE_API_KEY)
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    print(f"\n🔎 Query: '{query}'")

    # 2. Embed Query (Get the vector)
    try:
        query_vector = vo.embed([query], model="voyage-2", input_type="query").embeddings[0]
    except Exception as e:
        print(f"Voyage AI Error: {e}")
        return

    # 3. Search MongoDB (Get candidates)
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", 
                "path": "embedding",
                "queryVector": query_vector,
                "numCandidates": 100, # Scan more items
                "limit": 10           # Return top 10 relevant items
            }
        },
        {
            "$project": {
                "7_Description": 1,
                "15_Price": 1,
                "12_Remarks": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]

    # --- CRITICAL STEP: EXECUTE SEARCH ---
    raw_results = list(collection.aggregate(pipeline))
    
    if not raw_results:
        print("❌ No matches found. (Check if your Index name is 'vector_index')")
        return

    # 4. FINANCIAL RE-RANKING (Sort by Price: High -> Low)
    # We take the AI's top 10 relevant items and force the expensive ones to the top.
    sorted_results = sorted(raw_results, key=get_price_value, reverse=True)

    # 5. Display Results
    print(f"\n💰 FOUND {len(raw_results)} MATCHES. PRIORITIZING HIGH VALUE ASSETS:\n")
    
    # Show top 3 expensive items
    for res in sorted_results[:3]:
        price_val = get_price_value(res)
        ai_score = res.get('score', 0) * 100
        
        print(f"🔹 PART: {res.get('7_Description')}")
        print(f"   💲 VALUE: ${price_val:,.2f}") 
        print(f"   🤖 MATCH: {ai_score:.1f}%")
        print(f"   📝 NOTE:  {res.get('12_Remarks')[:100]}...")
        print("-" * 50)

if __name__ == "__main__":
    while True:
        user_query = input("\nSearch (e.g. 'serviceable engine parts' or 'q' to quit): ")
        if user_query.lower() == 'q':
            break
        search_inventory(user_query)