import pandas as pd
from sentence_transformers import SentenceTransformer, util
from rapidfuzz import fuzz
import streamlit as st

# ----------------------------
# Load dataset
# ----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(r"D:\project\MOCK_DATA_with_NCO.csv")
    return df

# ----------------------------
# Load model and precompute embeddings
# ----------------------------
@st.cache_resource
def load_model_and_embeddings(df):
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    df['embeddings'] = df['occupation_title'].apply(
        lambda x: model.encode(str(x), convert_to_tensor=True)
    )
    return model, df

# ----------------------------
# Search function
# ----------------------------
def search_occupation(query, model, df, top_k=3):
    query_emb = model.encode(query, convert_to_tensor=True)

    df['semantic_score'] = df['embeddings'].apply(
        lambda emb: float(util.cos_sim(query_emb, emb))
    )

    df['fuzzy_score'] = df['occupation_title'].apply(
        lambda title: fuzz.token_sort_ratio(query.lower(), title.lower()) / 100
    )

    df['final_score'] = 0.7 * df['semantic_score'] + 0.3 * df['fuzzy_score']

    results = df.sort_values(by='final_score', ascending=False).head(top_k)
    return results[['occupation_title', 'nco_code', 'final_score']]

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="NCO Job Title Search", page_icon="🔍", layout="centered")

st.title("🔍 Multilingual NCO Occupation Search")
st.markdown("Search occupations in your convenent language.")

df = load_data()
model, df = load_model_and_embeddings(df)

query = st.text_input("Enter job title", placeholder="Type here... e.g. மென்பொருள் பொறியாளர் / Software Engineer")

top_k = st.slider("Number of results", min_value=1, max_value=10, value=3)

if st.button("Search"):
    if query.strip() == "":
        st.warning("⚠ Please enter a job title to search.")
    else:
        results = search_occupation(query, model, df, top_k)
        st.subheader("Results:")
        st.dataframe(results, use_container_width=True)
