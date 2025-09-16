# Excel-Price-Comparer

**A simple Streamlit application to compare two Excel price sheets.**  

This app allows you to upload a "correct" price list and a "compare" price list, select the relevant columns, and quickly identify mismatches in prices or missing products.

---

## How to Use

1. **Upload Files**  
   - Upload the Excel file containing the correct values.  
   - Upload the Excel file you want to compare.  

2. **Select Sheets**  
   - Specify the sheet name for both Excel files.  
   - Leave it empty if you want to use the first sheet.  

3. **Skip Header Rows**  
   - Enter the number of rows to skip so the program knows where the product data starts.  
   - Use the row number of the column headers minus one.  

4. **Select Columns**  
   - Choose the ID columns in both files to align the products.  
   - Choose the price columns in both files for comparison.  
   - Choose the product name column in the correct Excel file (optional for display).  

5. **View Results**  
   - The app will generate a list of mismatches, including missing products and price differences.  
   - You can download the results as a CSV for further use.  

---

## Features

- Handles Excel files with different sheet layouts and header rows.  
- Flexible selection of IDs, product names, and price columns.  
- Flags missing products and price changes.  
- Clean, interactive interface via Streamlit.  
