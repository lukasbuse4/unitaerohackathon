import streamlit as st
import voyageai
from pymongo import MongoClient
import certifi
import pandas as pd
import os

# --- SECRETS HANDLING ---
# This imports the keys from the secrets.py file.
# If secrets.py is missing (like on GitHub), it stops the app.
try:
    from secrets import MONGO_URI, VOYAGE_API_KEY
except ImportError:
    st.error("❌ ERROR: secrets.py not found. You must create this file locally.")
    st.stop()

# ---------------------------------------------------------
# MANUAL IMAGE MAPPING
# ---------------------------------------------------------
IMAGE_MAP = {
    "TURBOFAN ENGINE": "part_images/turbineengine.jpg",
    "GEAR SHAFT": "part_images/gearshaft.jpg",
    "DISKS": "part_images/disk.jpg",
    "NOZZLE": "part_images/nozzle.jpg",
    "VALVE": "part_images/valve.jpg",
    "HPT VEIN": "part_images/vein.jpg"
}

# Page Setup
st.set_page_config(page_title="Unit Aerospace Demo", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .big-font { font-size:24px !important; font-weight: bold; }
    .price-tag { color: #2ecc71; font-size: 20px; font-weight: bold; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# BACKEND LOGIC
# ---------------------------------------------------------
@st.cache_resource
def init_connection():
    try:
        client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
        return client["aviation_hackathon"]["inventory"]
    except Exception as e:
        st.error(f"MongoDB Connection Error: {e}")
        return None

@st.cache_resource
def init_voyage():
    return voyageai.Client(api_key=VOYAGE_API_KEY)

def get_price_value(item):
    price_str = str(item.get('15_Price', '0'))
    clean = price_str.replace('$', '').replace(',', '')
    try:
        return float(clean)
    except:
        return 0.0

def run_search(query, collection, vo):
    # 1. Embed
    vec = vo.embed([query], model="voyage-2", input_type="query").embeddings[0]
    
    # 2. Search
    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index", 
            "path": "embedding", 
            "queryVector": vec, 
            "numCandidates": 100, 
            "limit": 10
        }},
        {"$project": {
            "7_Description": 1, "15_Price": 1, "12_Remarks": 1, 
            "score": {"$meta": "vectorSearchScore"}
        }}
    ]
    results = list(collection.aggregate(pipeline))
    
    # 3. Sort by Price (The Thesis)
    return sorted(results, key=get_price_value, reverse=True)

# ---------------------------------------------------------
# FRONTEND UI
# ---------------------------------------------------------
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/726/726488.png", width=80) 
with col2:
    st.title("Asset Value Prioritization Aerospace Component maintenance")
    st.markdown("AI-driven inventory search that ranks results by **Revenue Potential**.")

collection = init_connection()
vo = init_voyage()

query = st.text_input("Describe the inventory you need:", placeholder="e.g., serviceable engine parts with NDT inspection")

if query and collection is not None:
    with st.spinner("Analyzing Remarks & Calculating Asset Value..."):
        try:
            results = run_search(query, collection, vo)
            
            if not results:
                st.warning("No matches found. Try a broader search.")
            else:
                # METRICS
                top_item = results[0]
                top_val = get_price_value(top_item)
                total_val = sum(get_price_value(x) for x in results)
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Highest Value Asset", f"${top_val:,.0f}")
                m2.metric("Total Opportunity", f"${total_val:,.0f}")
                m3.metric("AI Confidence", f"{top_item['score']*100:.1f}%")

                st.divider()

                # HERO SECTION (Top Result)
                st.subheader("🏆 Priority Asset Identified")
                hero_col1, hero_col2 = st.columns([1, 2])
                
                with hero_col1:
                    part_name = top_item.get('7_Description')
                    
                    if part_name in IMAGE_MAP and os.path.exists(IMAGE_MAP[part_name]):
                        image_source = IMAGE_MAP[part_name]
                        caption_text = f"Asset Image: {part_name}"
                    else:
                        image_source = f"https://placehold.co/600x400/2ecc71/ffffff?text={part_name.replace(' ', '+')}"
                        caption_text = "Image Unavailable - Visual Placeholder"

                    st.image(image_source, caption=caption_text, use_container_width=True)
                
                with hero_col2:
                    st.markdown(f"### {top_item.get('7_Description')}")
                    st.markdown(f"<p class='price-tag'>Price: {top_item.get('15_Price')}</p>", unsafe_allow_html=True)
                    st.info(f"**AI Context Analysis:** {top_item.get('12_Remarks')}")

                st.divider()

                # LIST & CHART
                st.subheader("⬇️ Other Relevant Inventory (Ranked by Value)")
                
                chart_data = []
                for r in results:
                    val = get_price_value(r)
                    chart_data.append({"Part": r.get("7_Description"), "Value": val})
                
                c1, c2 = st.columns([2, 1])
                
                with c1:
                    for item in results[1:6]:
                        with st.expander(f"📦 {item.get('7_Description')} — {item.get('15_Price')}"):
                            st.write(f"**Remarks:** {item.get('12_Remarks')}")
                            st.caption(f"Match Score: {item['score']*100:.1f}%")
                
                with c2:
                    st.markdown("**Value Distribution**")
                    df = pd.DataFrame(chart_data)
                    st.bar_chart(df, x="Part", y="Value", color="#2ecc71")
                    
        except Exception as e:
            st.error(f"Search Error: {e}")