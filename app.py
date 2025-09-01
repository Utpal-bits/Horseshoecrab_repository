import streamlit as st
import pandas as pd

# --- Page Configuration ---
st.set_page_config(
    page_title="Research Paper Repository",
    page_icon="📚",
    layout="wide",
)

# --- Custom CSS for Styling ---
# This CSS is used to style the publication type as a small badge.
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
        color: #0366d6;
        background-color: #e1efff;
        margin-bottom: 10px;
    }
    .result-container {
        border: 1px solid #e1e4e8;
        border-radius: 6px;
        padding: 1rem;
        margin-bottom: 1rem;
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


# --- Data Loading ---
# @st.cache_data is a Streamlit decorator that caches the data.
# This means the data is loaded only once, making the app much faster.
@st.cache_data
def load_data(file_path):
    """Loads and preprocesses the data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Fill missing values in key text columns to prevent errors during search
        # We will use empty strings as placeholders.
        text_columns = ['Title', 'Author/s', 'Keywords', 'Abstract']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('')
        return df
    except FileNotFoundError:
        st.error(f"Error: The file '{file_path}' was not found. Please make sure it's in the same directory as the script.")
        return None

# --- Main Application ---
st.title("📚 Research Paper Search Repository")
st.write("Search through the repository using titles, authors, or keywords.")

# Load the data
# IMPORTANT: Make sure your CSV file is named 'research_data.csv' or change the filename below.
data = load_data('research_data.csv')

if data is not None:
    # --- Search Input ---
    search_query = st.text_input(
        "Enter your search query",
        placeholder="e.g., 'machine learning', 'John Doe', or 'data visualization'",
        help="You can search by title, author, or keywords."
    )

    # --- Search and Display Logic ---
    if search_query:
        # Perform a case-insensitive search across the specified columns
        query = search_query.lower()
        
        # The core search logic: check if the query string is present in any of the three columns.
        # The '|' symbol acts as an 'OR' operator.
        results = data[
            data['Title'].str.lower().str.contains(query) |
            data['Author/s'].str.lower().str.contains(query) |
            data['Keywords'].str.lower().str.contains(query)
        ]

        st.divider()

        # --- Display Results ---
        if not results.empty:
            st.success(f"Found **{len(results)}** matching result(s).")

            # Iterate through each row of the results and display it
            for index, row in results.iterrows():
                # Using st.markdown with unsafe_allow_html=True to render custom HTML/CSS
                st.markdown(f'<div class="result-container">', unsafe_allow_html=True)
                
                # Display Publication Type in the corner
                pub_type = row.get('Publication Type', 'N/A')
                st.markdown(f'<span class="publication-type">{pub_type}</span>', unsafe_allow_html=True)
                
                # Display Title
                st.markdown(f'<p class="result-title">{row["Title"]}</p>', unsafe_allow_html=True)
                
                # Display Authors and Publication Year
                authors = row.get('Author/s', 'N/A')
                year = row.get('Publication Year', 'N/A')
                st.markdown(f'<p class="result-meta">By: <strong>{authors}</strong> | Published in: <strong>{year}</strong></p>', unsafe_allow_html=True)

                # Display Abstract if available
                abstract = row.get('Abstract', '')
                if abstract and pd.notna(abstract):
                    with st.expander("View Abstract"):
                        st.write(abstract)

                st.markdown('</div>', unsafe_allow_html=True)

        else:
            st.warning("No results found for your query. Please try different search terms.")
