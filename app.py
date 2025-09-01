import streamlit as st
import pandas as pd
import hashlib

# --- Page Configuration ---
st.set_page_config(
    page_title="Horseshoe Crab Research Repository",
    layout="wide",
)

# --- State Management ---
# Initialize session state to manage the view (homepage vs. results page)
if 'search_active' not in st.session_state:
    st.session_state.search_active = False

# --- Helper Functions ---
def get_pub_type_class(pub_type_string):
    """Assigns a color class based on the publication type string for varied styling."""
    if not isinstance(pub_type_string, str):
        return "pub-type-default"
    hash_object = hashlib.md5(pub_type_string.encode())
    hash_dig = int(hash_object.hexdigest(), 16)
    num_classes = 4 # We have 4 color styles defined in CSS
    class_index = (hash_dig % num_classes) + 1
    return f"pub-type-{class_index}"

# --- Custom CSS ---
st.markdown("""
<style>
    /* --- General & Background Video --- */
    .stApp {
        background-color: #000; /* Fallback background */
    }
    #bg-video {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%; 
        min-height: 100%;
        z-index: -1;
    }
    /* Dark overlay for text readability */
    .overlay {
        position: fixed;
        right: 0;
        bottom: 0;
        min-width: 100%;
        min-height: 100%;
        background-color: rgba(0, 0, 0, 0.6);
        z-index: -1;
    }
    
    /* --- Result Card Styling --- */
    .result-container {
        background-color: #0d1b2a; /* Dark blue background */
        border: 1px solid #415a77;   /* Lighter blue border */
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        color: #e0e1dd;
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .result-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
    }
    .result-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 0.5rem;
    }
    .result-meta {
        font-size: 1.0rem;
        color: #b0b3b8;
        margin-bottom: 0.5rem;
    }
    .result-container .st-expander p {
        color: #e0e1dd !important; /* Text inside abstract expander */
    }

    /* --- Publication Type Badge (Multiple Colors) --- */
    .publication-type {
        display: inline-block;
        padding: 0.3em 0.7em;
        font-size: 0.8em;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.375rem;
        color: #ffffff;
        margin-bottom: 10px;
    }
    .pub-type-1 { background-color: #0077b6; } /* Blue */
    .pub-type-2 { background-color: #e56b6f; } /* Red */
    .pub-type-3 { background-color: #52b788; } /* Green */
    .pub-type-4 { background-color: #f7b801; } /* Yellow */
    .pub-type-default { background-color: #6c757d; } /* Grey */
</style>
""", unsafe_allow_html=True)


# --- Background Video Player ---
# This will only be shown on the homepage
if not st.session_state.search_active:
    st.markdown("""
        <div class="overlay"></div>
        <video autoplay muted loop id="bg-video">
            <source src="https://videos.pexels.com/video-files/2422488/2422488-hd_1920_1080_25fps.mp4" type="video/mp4">
            Your browser does not support the video tag.
        </video>
    """, unsafe_allow_html=True)


# --- Sidebar Content ---
st.sidebar.title("🦀 About the Repository")
st.sidebar.info(
    "A searchable repository of research on horseshoe crabs. Use the search bar to find articles by title, author, or keywords."
)
st.sidebar.header("How the Search Works")
st.sidebar.markdown("- Search is **case-insensitive**.\n- Matches against **Title**, **Author/s**, and **Keywords**.")
st.sidebar.header("Search Tips")
st.sidebar.markdown("- **Author:** Use last names (e.g., `Botton`).\n- **Topic:** Use broad keywords (e.g., `LAL`).")
with st.sidebar.expander("About Horseshoe Crabs"):
    st.markdown("""
    Horseshoe crabs are marine arthropods that have existed for over 450 million years. There are four living species:
    - _Limulus polyphemus_ (North America)
    - _Tachypleus gigas_ (Southeast Asia)
    - _Tachypleus tridentatus_ (East Asia)
    - _Carcinoscorpius rotundicauda_ (Southeast Asia & India)
    
    Their blue blood is vital for creating **Limulus Amebocyte Lysate (LAL)**, used to detect bacterial contamination in medical applications.
    """)
st.sidebar.markdown("---")
st.sidebar.caption("Developed by Utpal Mallick, ViStA Lab, BITS Pilani, Goa Campus.")
st.sidebar.caption("Data sourced from The Lens, PoP software, Google Scholar, etc.")


# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    """Loads and preprocesses data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        text_columns = ['Title', 'Author/s', 'Keywords', 'Abstract']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please ensure it's in the same directory.")
        return None

data = load_data('research_data.csv')


# --- App Layout (Main Area) ---
# This function displays the homepage
def show_homepage():
    st.title("")
    st.markdown("<h1 style='text-align: center; color: white;'>Horseshoe Crab Research Repository</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #e0e1dd;'>Discover the world of horseshoe crab research. Enter a query to begin.</p>", unsafe_allow_html=True)
    
    # Add empty space to push the search bar down
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Search bar in the middle of the homepage
    search_query = st.text_input(
        "Search the repository",
        placeholder="e.g., 'Limulus polyphemus', 'John Doe', or 'conservation'",
        label_visibility="collapsed",
        key="home_search"
    )
    if search_query:
        st.session_state.search_active = True
        st.session_state.search_query = search_query
        st.rerun()

# This function displays the search results page
def show_results_page():
    st.title(" Horseshoe Crab Research Repository")

    def perform_search():
        query = st.session_state.get('search_query', '').lower()
        if query and data is not None:
            results = data[
                data['Title'].str.lower().str.contains(query) |
                data['Author/s'].str.lower().str.contains(query) |
                data['Keywords'].str.lower().str.contains(query)
            ]
            return results
        return pd.DataFrame()

    # Search bar for the results page
    search_query = st.text_input(
        "Search the repository",
        value=st.session_state.get('search_query', ''),
        key="results_search"
    )
    # If the search query changes, update the state and rerun
    if search_query != st.session_state.get('search_query', ''):
        st.session_state.search_query = search_query
        st.rerun()

    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.button("⬅️ New Search (Homepage)"):
            st.session_state.search_active = False
            st.session_state.search_query = ""
            st.rerun()

    results = perform_search()
    st.divider()

    if not results.empty:
        st.success(f"Found **{len(results)}** matching result(s) for '{st.session_state.search_query}'.")
        for _, row in results.iterrows():
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            pub_type = row.get('Publication Type', '')
            pub_class = get_pub_type_class(pub_type)
            st.markdown(f'<span class="publication-type {pub_class}">{pub_type}</span>', unsafe_allow_html=True)
            
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
        st.warning(f"No results found for your query: '{st.session_state.search_query}'. Please try different terms.")

# --- Main Logic ---
# Use the session state to decide which page to show
if data is not None:
    if not st.session_state.search_active:
        show_homepage()
    else:
        show_results_page()
