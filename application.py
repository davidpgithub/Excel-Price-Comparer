import streamlit as st
import pandas as pd
import numpy as np

st.title("Excel Price Comparison Tool")

# --- Initialize session state for swap ---
for key in ["correct_file", "compare_file", "correct_sheet", "compare_sheet",
            "rows_to_skip_correct", "rows_to_skip_compare",
            "correct_id", "compare_id", "correct_price", "compare_price", "correct_name"]:
    if key not in st.session_state:
        st.session_state[key] = None

def safe_index(options, saved_value, fallback=0):
    """Return index of saved_value in options if present, otherwise fallback."""
    return options.index(saved_value) if saved_value in options else fallback

# 1️⃣ Upload Excel files
uploaded_correct = st.file_uploader("Upload Correct Excel", type=["xlsx","xls","csv"], key="correct_file_upload")
uploaded_compare = st.file_uploader("Upload Compare Excel", type=["xlsx","xls","csv"], key="compare_file_upload")

if uploaded_correct:
    st.session_state.correct_file = uploaded_correct
if uploaded_compare:
    st.session_state.compare_file = uploaded_compare

# # 🔄 Swap button
# if st.button("🔄 Swap Correct & Compare"):
#     (st.session_state.correct_file, st.session_state.compare_file,
#      st.session_state.correct_sheet, st.session_state.compare_sheet,
#      st.session_state.rows_to_skip_correct, st.session_state.rows_to_skip_compare,
#      st.session_state.correct_id, st.session_state.compare_id,
#      st.session_state.correct_price, st.session_state.compare_price,
#      st.session_state.correct_name) = (
#         st.session_state.compare_file, st.session_state.correct_file,
#         st.session_state.compare_sheet, st.session_state.correct_sheet,
#         st.session_state.rows_to_skip_compare, st.session_state.rows_to_skip_correct,
#         st.session_state.compare_id, st.session_state.correct_id,
#         st.session_state.compare_price, st.session_state.correct_price,
#         None  # Name only exists in correct file, so reset
#     )

correct_file = st.session_state.correct_file
compare_file = st.session_state.compare_file

if correct_file and compare_file:
    # 2️⃣ Configure sheets
    st.write("Configure Sheets to be read:")
    col1, col2 = st.columns(2)
    col1.markdown("**Correct File Sheet**")
    col2.markdown("**Compare File Sheet**")

    with col1:
        correct_sheet = st.text_input("Correct Sheet Name (or leave blank for first sheet)", st.session_state.correct_sheet or "")
        st.session_state.correct_sheet = correct_sheet
    with col2:
        compare_sheet = st.text_input("Compare Sheet Name (or leave blank for first sheet)", st.session_state.compare_sheet or "")
        st.session_state.compare_sheet = compare_sheet

    with col1:
        rows_to_skip_correct = st.number_input("Correct sheet: Rows to skip (Row Number of Header - 1)", min_value=0, value=st.session_state.rows_to_skip_correct or 5)
        st.session_state.rows_to_skip_correct = rows_to_skip_correct
    with col2:
        rows_to_skip_compare = st.number_input("Compare sheet: Rows to skip (Row Number of Header - 1)", min_value=0, value=st.session_state.rows_to_skip_compare or 2)
        st.session_state.rows_to_skip_compare = rows_to_skip_compare

    # Load correct file
    if correct_sheet:
        correct_df = pd.read_excel(correct_file, sheet_name=correct_sheet, skiprows=rows_to_skip_correct)
    else:
        correct_df = pd.read_excel(correct_file, sheet_name=0, skiprows=rows_to_skip_correct)

    # Load compare file
    if compare_sheet:
        compare_df = pd.read_excel(compare_file, sheet_name=compare_sheet, skiprows=rows_to_skip_compare)
    else:
        compare_df = pd.read_excel(compare_file, sheet_name=0, skiprows=rows_to_skip_compare)

    # 3️⃣ Select columns
    st.write("Select columns for comparison:")
    col1, col2 = st.columns(2)
    col1.markdown("**Correct File Columns**")
    col2.markdown("**Compare File Columns**")

    correct_df.columns = correct_df.columns.astype(str)
    compare_df.columns = compare_df.columns.astype(str)

    correct_cols = correct_df.loc[:, ~correct_df.columns.str.contains("Unnamed")]
    compare_cols = compare_df.loc[:, ~compare_df.columns.str.contains("Unnamed")]

    with col1:
        correct_id = st.selectbox(
            "Correct ID column",
            list(correct_cols.columns),
            index=safe_index(list(correct_cols.columns), st.session_state.get("correct_id"))
        )
        st.session_state.correct_id = correct_id

    with col2:
        compare_id = st.selectbox(
            "Compare ID column",
            list(compare_cols.columns),
            index=safe_index(list(compare_cols.columns), st.session_state.get("compare_id"))
        )
        st.session_state.compare_id = compare_id

    with col1:
        correct_price = st.selectbox(
            "Correct Price column",
            list(correct_cols.columns),
            index=safe_index(list(correct_cols.columns), st.session_state.get("correct_price"))
        )
        st.session_state.correct_price = correct_price

    with col2:
        compare_price = st.selectbox(
            "Compare Price column",
            list(compare_cols.columns),
            index=safe_index(list(compare_cols.columns), st.session_state.get("compare_price"))
        )
        st.session_state.compare_price = compare_price

    with col1:
        correct_name = st.selectbox(
            "Correct Name column",
            list(correct_cols.columns),
            index=safe_index(list(correct_cols.columns), st.session_state.get("correct_name"))
        )
        st.session_state.correct_name = correct_name

    with col2:
        mismatch_type = st.selectbox("Mismatch Type", ["All", "Price change", "Missing", "Other"], index=0)

    # 4️⃣ Clean IDs
    correct_df = correct_df.dropna(subset=[correct_id, correct_price])
    compare_df = compare_df.dropna(subset=[compare_id, compare_price])

    compare_df[compare_id] = compare_df[compare_id].astype(str).str.replace(r"^'", "", regex=True).str.replace(r"\.0$", "", regex=True)
    correct_df[correct_id] = correct_df[correct_id].astype(str).str.replace(r"\.0$", "", regex=True)

    # 5️⃣ Merge and mismatches
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

    final_mismatch = mismatches[[correct_id, correct_name, correct_price, compare_price, "mismatch_type"]]
    final_mismatch = final_mismatch.rename(
        columns={correct_price: "Price_correct", compare_price: "Price_comparison"}
    )

    if mismatch_type != "All":
        final_mismatch = final_mismatch[final_mismatch["mismatch_type"] == mismatch_type].reset_index(drop=True)

    # 7️⃣ Show results
    st.write("Mismatches found:", len(final_mismatch))
    st.dataframe(final_mismatch)

    # Download button
    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode("utf-8")

    csv = convert_df(final_mismatch)
    st.download_button(
        label="Download mismatches as CSV",
        data=csv,
        file_name="mismatches.csv",
        mime="text/csv",
    )
