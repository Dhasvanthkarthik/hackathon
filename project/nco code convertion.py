import pandas as pd
from fuzzywuzzy import process

# Load your datasets
df = pd.read_csv(r"D:\project\MOCK_DATA.csv")  # id, occupation_title, state, district, gender, income, year
nco_df = pd.read_csv(r"D:\project\NCO_reference.csv")  # NCO_Code, Occupation_title

# Function to find best matching NCO code for a given job title
def find_nco_code(job_title, nco_data):
    if pd.isna(job_title):
        return None
    # Get the best match
    result = process.extractOne(job_title, nco_data['Occupation_title'])
    if result:
        match, score, _ = result  # unpack match, score, index
        if score >= 80:  # Threshold for match confidence
            return nco_data.loc[nco_data['Occupation_title'] == match, 'NCO_Code'].values[0]
    return None

# Apply matching function to each row in mock data
df['nco_code'] = df['occupation_title'].apply(lambda x: find_nco_code(x, nco_df))

# Save the updated dataframe
df.to_csv("MOCK_DATA_with_NCO.csv", index=False)

print("Matching completed. File saved as MOCK_DATA_with_NCO.csv")
