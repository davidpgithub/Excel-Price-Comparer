import pandas as pd
import numpy as np


# excel sheets

# correct version
correct_name= "TB Catalogue - DUFRY _ rev_abr2024_v1"
sheet_name= 0
correct_id_name= "CAT"
correct_price_name="LATAM RRP US$ 2022"
correct_product_name="PRODUCT"
rows_to_skip = 5 # Number of header row -1
try:
    correct_df= pd.read_excel("data/" + correct_name + ".xlsx", sheet_name=sheet_name, skiprows=rows_to_skip)
except:
    correct_df= pd.read_excel("data/" + correct_name + ".xls", sheet_name=sheet_name, skiprows=rows_to_skip)

# compare version
compare_name="Duty Paid Argentina"
sheet_name= 0
compare_id_name= "CAT"
compare_price_name=" LATAM RRP \nUS$ 2022"
missing=False
rows_to_skip = 2 # Number of header row -1
try:
    compare_df= pd.read_excel("data/" + compare_name + ".xlsx", sheet_name=sheet_name, skiprows=rows_to_skip)
except:
    compare_df= pd.read_excel("data/" + compare_name + ".xls", sheet_name=sheet_name, skiprows=rows_to_skip)


# remove all the nan values
correct_df= correct_df.dropna(subset=[correct_id_name, correct_price_name])

# remove all nan columns
compare_df = compare_df.loc[:, compare_df.isna().mean() < 0.5]
#compare_df= compare_df.dropna()
# fix id problems: some are strings 
compare_df[compare_id_name] = compare_df[compare_id_name].astype(str).str.replace(r"^'", "", regex=True).str.replace(r"\.0$", "", regex=True)
#compare_df[compare_id_name] = compare_df[compare_id_name].astype(int)

# change key id into string

correct_df[correct_id_name]= correct_df[correct_id_name].astype(str)
compare_df[compare_id_name]= compare_df[compare_id_name].astype(str)





print(correct_df.head(5))
print(compare_df.head(5))



def compare_data(df1,df1_id,df1_name, df1_price, df2,df2_id, df2_price):
    # merge dfs
    merged = df1.merge(
    df2,
    left_on=df1_id,
    right_on=df2_id,
    how="left")
    #merged = merged.set_index(df1_id)
    print("MERGED")
    print(merged.head(5))
    mismatches = merged[merged[df1_price] != merged[df2_price]]
    mismatches["mismatch_type"] = np.where(
    mismatches[df2_price].isna(),            # If compare price is missing
    "Missing",
    np.where(
        mismatches[df1_price] != mismatches[df2_price],  # If prices differ
        "Price change",
        "Other"  # fallback for any unexpected cases
    )
)   
    final_mismatch = mismatches[[df1_id, df1_name, df1_price, df2_price, "mismatch_type"]]
    final_mismatch = final_mismatch.rename(
    columns={
        df1_price: "Price_correct",
        df2_price: "Price_wrong"
    }
    
)
    if missing:
        final_mismatch = final_mismatch.reset_index(drop=True)
    else:
        final_mismatch = final_mismatch[~final_mismatch["mismatch_type"].str.contains("Missing")]
        final_mismatch = final_mismatch.reset_index(drop=False)

    
    print(final_mismatch)
    print("Amount of mismatches", len(final_mismatch))

    
compare_data(correct_df, correct_id_name,correct_product_name, correct_price_name, compare_df, compare_id_name,compare_price_name)