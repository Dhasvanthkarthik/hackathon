import streamlit as st
import pandas as pd
import os
import re
import requests

st.set_page_config(page_title="Hackathon Survey Data", layout="wide")

# ----------------------------
# Load survey data from .ctl file on GitHub
# ----------------------------
@st.cache_data
def load_survey_data():
    # URL to your .ctl file in GitHub
    ctl_file_url = "https://raw.githubusercontent.com/Dhasvanthkarthik/hackathon/main/survey_data.ctl"

    # Read the ctl file content from GitHub
    try:
        ctl_content = requests.get(ctl_file_url).text
    except Exception as e:
        st.error(f"❌ Could not fetch .ctl file: {e}")
        return pd.DataFrame()

    # Extract INFILE path
    infile_match = re.search(r"INFILE\s+'([^']+)'", ctl_content, re.IGNORECASE)
    if not infile_match:
        st.error("❌ No INFILE path found inside the .ctl file")
        return pd.DataFrame()

    raw_path = infile_match.group(1).strip()

    # Convert to GitHub raw link if it's a local file path
    if not raw_path.startswith("http"):
        data_file_url = f"https://raw.githubusercontent.com/Dhasvanthkarthik/hackathon/main/{os.path.basename(raw_path)}"
    else:
        data_file_url = raw_path

    # Extract delimiter
    delimiter_match = re.search(r"FIELDS TERMINATED BY\s+'([^']+)'", ctl_content, re.IGNORECASE)
    delimiter = delimiter_match.group(1) if delimiter_match else ","

    # Try reading the data file
    try:
        df = pd.read_csv(data_file_url, delimiter=delimiter, encoding="utf-8", quotechar='"')
        st.success(f"✅ Survey data loaded from: {data_file_url}")
        return df
    except UnicodeDecodeError:
        df = pd.read_csv(data_file_url, delimiter=delimiter, encoding="latin-1", quotechar='"')
        st.success(f"✅ Survey data loaded from: {data_file_url} (latin-1 encoding)")
        return df
    except Exception as e:
        st.error(f"❌ Error loading survey data: {e}")
        return pd.DataFrame()

# ----------------------------
# Main App
# ----------------------------
def main():
    st.title("📊 Hackathon Survey Data Viewer")
    st.write("This app loads and displays survey data defined in a `.ctl` file.")

    df_survey = load_survey_data()

    if df_survey.empty:
        st.warning("No survey data loaded.")
        return

    # Display raw data
    st.subheader("Survey Data")
    st.dataframe(df_survey)

    # Basic statistics
    st.subheader("Summary Statistics")
    st.write(df_survey.describe(include="all"))

    # Search filter
    st.subheader("Search")
    search_col = st.selectbox("Select column to search", df_survey.columns)
    search_val = st.text_input("Enter search value")

    if search_val:
        results = df_survey[df_survey[search_col].astype(str).str.contains(search_val, case=False, na=False)]
        st.write(f"Found {len(results)} results")
        st.dataframe(results)

if __name__ == "__main__":
    main()
