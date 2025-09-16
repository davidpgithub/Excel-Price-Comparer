import streamlit as st
import pandas as pd
import numpy as np

st.title("Excel Price Comparison Tool")

# 1️⃣ Upload Excel files
correct_file = st.file_uploader("Upload Correct Excel", type=["xlsx"])
compare_file = st.file_uploader("Upload Compare Excel", type=["xlsx"])

if correct_file and compare_file:
    # 2️⃣ Read sheets
    st.write("Configure Sheets to be read:")
    col1,col2= st.columns(2)
    col1.markdown("**Correct File Sheet**")
    col2.markdown("**Compare File Sheet**")
    #Row1
    with col1:
        correct_sheet = st.text_input("Correct Sheet Name (or leave blank for first sheet)", "")
    with col2:
        compare_sheet = st.text_input("Compare Sheet Name / Index (0 for first sheet)", "0")
    
    #Row2
    with col1:
        rows_to_skip_correct = st.number_input("Correct sheet: Rows to skip (Row Number of Header - 1)", min_value=0, value=2)
    with col2:
        rows_to_skip_compare = st.number_input("Compare sheet: Rows to skip (Row Number of Header - 1)", min_value=0, value=4)
    
    if correct_sheet:
        correct_df = pd.read_excel(correct_file, sheet_name=correct_sheet, skiprows=rows_to_skip_correct)
    else:
        correct_df = pd.read_excel(correct_file, sheet_name=0, skiprows=rows_to_skip_correct)
    
    if compare_sheet.isdigit():
        compare_sheet_idx = int(compare_sheet)
        compare_df = pd.read_excel(compare_file, sheet_name=compare_sheet_idx, skiprows=rows_to_skip_compare)
    else:
        compare_df = pd.read_excel(compare_file, sheet_name=compare_sheet, skiprows=rows_to_skip_compare)

    # 3️⃣ Select columns to compare
    st.write("Select columns for comparison:")
    col1,col2= st.columns(2)
    col1.markdown("**Correct File Columns**")
    col2.markdown("**Compare File Columns**")

    # Row 1
    with col1:
        correct_id = st.selectbox("Correct ID column", correct_df.columns)
    with col2:
        compare_id = st.selectbox("Compare ID column", compare_df.columns)

    # Row 2
    with col1:
         correct_price = st.selectbox("Correct Price column", correct_df.columns)
    with col2:
        compare_price = st.selectbox("Compare Price column", compare_df.columns)

    # Row 3
    with col1:
        correct_name = st.selectbox("Correct Name column", correct_df.columns)
   

   

    # 4️⃣ Clean IDs
    compare_df[compare_id] = compare_df[compare_id].astype(str).str.replace(r"^'", "", regex=True)
    correct_df[correct_id] = correct_df[correct_id].astype(str)
    compare_df[compare_id] = compare_df[compare_id].astype(str)

    # 5️⃣ Merge and find mismatches
    merged = correct_df.merge(compare_df, left_on=correct_id, right_on=compare_id, how="left")

    mismatches = merged[merged[correct_price] != merged[compare_price]].copy()
    mismatches["mismatch_type"] = np.where(
        mismatches[compare_price].isna(),
        "Missing",
        np.where(
            mismatches[correct_price] != mismatches[compare_price],
            "Price change",
            "Other"
        )
    )

    # 6️⃣ Select final columns and rename
    final_mismatch = mismatches[[correct_id, correct_name, correct_price, compare_price, "mismatch_type"]]
    final_mismatch = final_mismatch.rename(
        columns={
            correct_price: "Price_correct",
            compare_price: "Price_wrong"
        }
    )
    final_mismatch = final_mismatch.reset_index(drop=True)

    # 7️⃣ Show result and allow download
    st.write("Mismatches found:", len(final_mismatch))
    st.dataframe(final_mismatch)

    # Download button
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(final_mismatch)
    st.download_button(
        label="Download mismatches as CSV",
        data=csv,
        file_name='mismatches.csv',
        mime='text/csv',
    )
