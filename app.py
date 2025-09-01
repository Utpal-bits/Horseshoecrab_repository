import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Research Paper Repository",
    page_icon="📚",
    layout="wide",
)

# --- Custom CSS for Styling ---
# This CSS styles the results as cards and adds a badge for publication type.
st.markdown("""
<style>
    .publication-type {
        display: inline-block;
        padding: 0.25em 0.6em;
        font-size: 0.75em;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
        color: #004085;
        background-color: #cce5ff;
        margin-bottom: 10px;
    }
    .result-container {
        border: 1px solid #e1e4e8;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02), 0 1px 2px rgba(0,0,0,0.04);
        transition: box-shadow 0.3s ease-in-out;
    }
    .result-container:hover {
        box-shadow: 0 4px 6px rgba(0,0,0,0.05), 0 1px 3px rgba(0,0,0,0.1);
    }
    .result-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #24292e;
        margin-bottom: 0.5rem;
    }
    .result-meta {
        font-size: 0.9rem;
        color: #586069;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# --- Sidebar Content ---
st.sidebar.title("🦀 About the Repository")
st.sidebar.info(
    "This application is a searchable repository of research focused on horseshoe crabs. "
    "Use the search bar to find articles by title, author, or keywords."
)

st.sidebar.header("How the Search Works")
st.sidebar.markdown("""
- The search is **case-insensitive**.
- It matches your query against the paper's **Title**, **Author/s**, and **Keywords**.
- A result will be shown if a match is found in any of these fields.
""")

st.sidebar.header("Search Tips")
st.sidebar.markdown("""
- **For a specific author:** Try using last names (e.g., `Botton`).
- **For a topic:** Use broad keywords (e.g., `LAL`, `conservation`, `spawning`).
- **For a title:** You can use a fragment of the title (e.g., `population genetics`).
""")

st.sidebar.header("About Horseshoe Crabs")
with st.sidebar.expander("Learn more about these 'living fossils'", expanded=True):
    st.markdown("""
    Horseshoe crabs are marine arthropods that have existed for over 450 million years, earning them the title of 'living fossils'. Despite their name, they are more closely related to spiders and scorpions than to crabs.
    
    **Species:**
    There are four living species:
    - **_Limulus polyphemus_**: Found along the Atlantic coast of North America and the Gulf of Mexico.
    - **_Tachypleus gigas_**: Found in Southeast Asia.
    - **_Tachypleus tridentatus_**: Found in East Asia.
    - **_Carcinoscorpius rotundicauda_**: Found in India and Southeast Asia.

    **Medical Importance:**
    Their unique, copper-based blue blood contains amebocytes. These cells are used to create **Limulus Amebocyte Lysate (LAL)**, a critical substance used by the pharmaceutical industry to detect bacterial endotoxins on medical equipment and in injectable drugs, ensuring patient safety.
    """)


# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    """Loads and preprocesses the data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        text_columns = ['Title', 'Author/s', 'Keywords', 'Abstract']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the same directory as the script.")
        return None

# --- Main Application Area ---
st.title(" Horseshoe Crab Research Repository")
st.write("A comprehensive database of scientific literature. Use the search bar below to get started.")

# Load the data
# IMPORTANT: Make sure your CSV file is named 'research_data.csv' or change the filename below.
data = load_data('research_data.csv')

if data is not None:
    # --- Search Input ---
    search_query = st.text_input(
        "Search the repository",
        placeholder="e.g., 'Limulus polyphemus', 'John Doe', or 'conservation'",
        help="You can search by title, author, or keywords."
    )

    # --- Search and Display Logic ---
    if search_query:
        query = search_query.lower()
        results = data[
            data['Title'].str.lower().str.contains(query) |
            data['Author/s'].str.lower().str.contains(query) |
            data['Keywords'].str.lower().str.contains(query)
        ]

        st.divider()

        # --- Display Results ---
        if not results.empty:
            st.success(f"Found **{len(results)}** matching result(s).")

            for index, row in results.iterrows():
                st.markdown(f'<div class="result-container">', unsafe_allow_html=True)
                
                pub_type = row.get('Publication Type', 'N/A')
                st.markdown(f'<span class="publication-type">{pub_type}</span>', unsafe_allow_html=True)
                
                st.markdown(f'<p class="result-title">{row["Title"]}</p>', unsafe_allow_html=True)
                
                authors = row.get('Author/s', 'N/A')
                year = row.get('Publication Year', 'N/A')
                st.markdown(f'<p class="result-meta">By: <strong>{authors}</strong> | Published in: <strong>{year}</strong></p>', unsafe_allow_html=True)

                abstract = row.get('Abstract', '')
                if abstract and pd.notna(abstract):
                    with st.expander("View Abstract"):
                        st.write(abstract)

                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No results found for your query. Please try different search terms.")
    else:
        st.info("Enter a query in the search bar above to see results.")


