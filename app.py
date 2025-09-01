import streamlit as st
import pandas as pd
import hashlib
import re

# --- Page Configuration ---
st.set_page_config(
    page_title="Horseshoe Crab Research Repository",
    layout="wide",
)

# --- State Management ---
# Initialize session state for various features
if 'search_active' not in st.session_state:
    st.session_state.search_active = False
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

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

def highlight_text(text, query):
    """Highlights the search query within a given text."""
    if query:
        # Use regex to find all occurrences of the query, case-insensitive
        return re.sub(f'({re.escape(query)})', r'<mark>\1</mark>', text, flags=re.IGNORECASE)
    return text

# --- Custom CSS ---
st.markdown("""
<style>
    /* --- General & Background Video --- */
    .stApp { background-color: #000; }
    #bg-video { position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; z-index: -1; }
    .overlay { position: fixed; right: 0; bottom: 0; min-width: 100%; min-height: 100%; background-color: rgba(0, 0, 0, 0.7); z-index: -1; }
    
    /* --- Result Card Styling --- */
    .result-container { background-color: #0d1b2a; border: 1px solid #415a77; border-radius: 8px; padding: 1.5rem; margin-bottom: 1rem; color: #e0e1dd; transition: transform 0.2s, box-shadow 0.2s; }
    .result-container:hover { transform: translateY(-5px); box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3); }
    .result-title { font-size: 1.5rem; font-weight: 600; color: #ffffff; margin-bottom: 0.5rem; }
    .result-meta { font-size: 1.0rem; color: #b0b3b8; margin-bottom: 0.5rem; }
    .result-container .st-expander p { color: #e0e1dd !important; }

    /* --- Publication Type Badge (Multiple Colors) --- */
    .publication-type { display: inline-block; padding: 0.3em 0.7em; font-size: 0.8em; font-weight: 700; line-height: 1; text-align: center; white-space: nowrap; border-radius: 0.375rem; color: #ffffff; margin-bottom: 10px; }
    .pub-type-1 { background-color: #0077b6; } .pub-type-2 { background-color: #e56b6f; } .pub-type-3 { background-color: #52b788; } .pub-type-4 { background-color: #f7b801; } .pub-type-default { background-color: #6c757d; }
    
    /* Highlight Style */
    mark { background-color: #f7b801; color: black; border-radius: 3px; padding: 0 2px; }
</style>
""", unsafe_allow_html=True)

# --- Background Video Player ---
if 'page' not in st.session_state or st.session_state.page == 'Home':
    st.markdown("""
        <div class="overlay"></div>
        <video autoplay muted loop id="bg-video">
            <source src="https://videos.pexels.com/video-files/2422488/2422488-hd_1920_1080_25fps.mp4" type="video/mp4">
        </video>
    """, unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Preprocessing
        text_columns = ['Title', 'Author/s', 'Keywords', 'Abstract', 'Source Country', 'Publication Type']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        # Ensure 'Publication Year' is numeric for sorting/filtering
        if 'Publication Year' in df.columns:
            df['Publication Year'] = pd.to_numeric(df['Publication Year'], errors='coerce').fillna(0).astype(int)
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found.")
        return None

data = load_data('research_data.csv')

# --- Sidebar ---
st.sidebar.title("🦀 Repository Menu")
page = st.sidebar.radio("Navigate", ["Home", "Search Repository", "Data Dashboard"], key="page_selection")

st.sidebar.markdown("---")
if data is not None and page == "Search Repository":
    st.sidebar.header("Advanced Search Filters")
    
    # Year Filter
    min_year, max_year = int(data['Publication Year'].min()), int(data['Publication Year'].max())
    year_range = st.sidebar.slider("Publication Year Range", min_year, max_year, (min_year, max_year))

    # Publication Type Filter
    pub_types = sorted(data['Publication Type'].unique())
    selected_pub_types = st.sidebar.multiselect("Publication Type", pub_types, default=pub_types)
    
    # Country Filter
    countries = sorted(data['Source Country'].unique())
    selected_countries = st.sidebar.multiselect("Source Country", countries, default=countries)

st.sidebar.markdown("---")
st.sidebar.caption("Developed by Utpal Mallick, ViStA Lab, BITS Pilani, Goa Campus.")
st.sidebar.caption("Data sourced from The Lens, PoP software, Google Scholar, etc.")

# --- Page Functions ---

def show_homepage():
    st.markdown("<h1 style='text-align: center; color: white;'>Horseshoe Crab Research Repository</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #e0e1dd;'>Discover the world of horseshoe crab research. Select a page from the sidebar to begin.</p>", unsafe_allow_html=True)

def show_dashboard_page():
    st.title("📊 Data Dashboard")
    st.write("Visualizing trends in the horseshoe crab research dataset.")
    
    if data is not None:
        # Publications Over Time
        st.subheader("Publications Over Time")
        yearly_counts = data[data['Publication Year'] > 0]['Publication Year'].value_counts().sort_index()
        st.bar_chart(yearly_counts)

        # Top Source Countries
        st.subheader("Top 10 Source Countries")
        country_counts = data[data['Source Country'] != '']['Source Country'].value_counts().nlargest(10)
        st.bar_chart(country_counts)

        # Publication Types
        st.subheader("Publication Type Distribution")
        pub_type_counts = data[data['Publication Type'] != '']['Publication Type'].value_counts()
        st.bar_chart(pub_type_counts)

def show_results_page():
    st.title("🔍 Search the Repository")

    def perform_search():
        query = st.session_state.get('search_query', '').lower()
        
        # Filter data based on sidebar selections
        filtered_data = data[
            (data['Publication Year'].between(year_range[0], year_range[1])) &
            (data['Publication Type'].isin(selected_pub_types)) &
            (data['Source Country'].isin(selected_countries))
        ]

        if query:
            results = filtered_data[
                filtered_data['Title'].str.lower().str.contains(query) |
                filtered_data['Author/s'].str.lower().str.contains(query) |
                filtered_data['Keywords'].str.lower().str.contains(query)
            ]
            return results
        return pd.DataFrame() # Return empty if no query

    search_query = st.text_input("Search query", value=st.session_state.get('search_query', ''), key="search_bar")
    if search_query != st.session_state.get('search_query', ''):
        st.session_state.search_query = search_query
        st.session_state.current_page = 1 # Reset to first page on new search
        st.rerun()

    results = perform_search()
    st.divider()

    if not results.empty:
        # --- Sorting ---
        sort_option = st.selectbox("Sort results by", ["Relevance", "Year (Newest First)", "Year (Oldest First)", "Title (A-Z)"])
        if sort_option == "Year (Newest First)": results = results.sort_values('Publication Year', ascending=False)
        if sort_option == "Year (Oldest First)": results = results.sort_values('Publication Year', ascending=True)
        if sort_option == "Title (A-Z)": results = results.sort_values('Title')

        # --- Download Button ---
        csv = results.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Results as CSV", data=csv, file_name="search_results.csv", mime="text/csv")

        st.success(f"Found **{len(results)}** matching result(s).")
        
        # --- Pagination ---
        results_per_page = 10
        start_index = (st.session_state.current_page - 1) * results_per_page
        end_index = start_index + results_per_page
        paginated_results = results.iloc[start_index:end_index]
        
        for _, row in paginated_results.iterrows():
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            pub_type = row.get('Publication Type', '')
            st.markdown(f'<span class="publication-type {get_pub_type_class(pub_type)}">{pub_type}</span>', unsafe_allow_html=True)
            
            title_html = highlight_text(row["Title"], search_query)
            st.markdown(f'<p class="result-title">{title_html}</p>', unsafe_allow_html=True)
            
            authors = highlight_text(row.get('Author/s', 'N/A'), search_query)
            year = row.get('Publication Year', 'N/A')
            st.markdown(f'<p class="result-meta">By: <strong>{authors}</strong> | Published in: <strong>{year}</strong></p>', unsafe_allow_html=True)

            abstract = row.get('Abstract', '')
            if abstract and pd.notna(abstract):
                with st.expander("View Abstract"):
                    st.write(highlight_text(abstract, search_query), unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)

        # Pagination controls
        total_pages = (len(results) - 1) // results_per_page + 1
        if total_pages > 1:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.session_state.current_page > 1:
                    if st.button("⬅️ Previous"):
                        st.session_state.current_page -= 1
                        st.rerun()
            with col2:
                st.write(f"Page {st.session_state.current_page} of {total_pages}")
            with col3:
                if st.session_state.current_page < total_pages:
                    if st.button("Next ➡️"):
                        st.session_state.current_page += 1
                        st.rerun()

    elif search_query:
        st.warning(f"No results found for your query: '{search_query}'. Try adjusting filters or search terms.")
    else:
        st.info("Enter a query and apply filters to see results.")

# --- Main Logic ---
if data is not None:
    if page == "Home":
        show_homepage()
    elif page == "Data Dashboard":
        show_dashboard_page()
    elif page == "Search Repository":
        show_results_page()

