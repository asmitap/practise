import pandas as pd
from sqlalchemy import create_engine
import pandas as pd

def database_connection():
    DATABASE_URI = ''
    engine = create_engine(DATABASE_URI)
    return engine

def get_stock_data():
    query = """SELECT * FROM pt_script.stock"""
    df = pd.read_sql_query(query, con=database_connection())
    stock_df = df[['id','symbol']]
    stock_df = stock_df.copy()
    stock_df.rename(columns={'symbol': 'Symbol'}, inplace=True)
    return stock_df

# def get_mutual_fund_data(file_path):
#     # Read the Excel file into a dictionary of DataFrames, with tab names as keys
#     dfs = pd.read_excel(file_path, sheet_name=None,header=0)
#     # Iterate through the dictionary of DataFrames and add a new column 'Tab Name'
#     for tab_name, df in dfs.items():
#         df['mutual_fund'] = tab_name
#     # Combine all DataFrames into a single DataFrame
#     combined_df = pd.concat(dfs.values(), ignore_index=True)
#     return combined_df

def get_mutual_fund_data(file_path):
    # Read the Excel file into a dictionary of DataFrames, with tab names as keys
    dfs = pd.read_excel(file_path, sheet_name=None, header=0)
    # Create a list of DataFrames with an additional 'mutual_fund' column
    dfs_with_tab_name = [df.assign(mutual_fund=tab_name) for tab_name, df in dfs.items()]
    # Concatenate all DataFrames in the list into a single DataFrame
    combined_df = pd.concat(dfs_with_tab_name, ignore_index=True)
    return combined_df

def mutual_fund(file_path):
    combined_df = get_mutual_fund_data(file_path)
    # Remove columns with mostly NaN values
    combined_df = combined_df.dropna(axis=1, how='all')
    # Remove the last column using the drop method
    combined_df = combined_df.drop(columns=combined_df.columns[-1])
    # Get the first row as the new column names
    new_column_names = combined_df.iloc[0]
    # Rename the columns based on the first row values
    combined_df.columns = new_column_names
    # Drop the first row (which is now the column names)
    combined_df = combined_df.iloc[1:]
    combined_df.rename(columns={'Value (Rs.)':'value','SSIS': 'mutual_fund', 'id':'stock_id'}, inplace=True)
    # Convert the 'date_column' to datetime format and handle errors
    combined_df['Date '] = pd.to_datetime(combined_df['Date '], errors='coerce')
    # Filter rows where 'date_column' is not a valid date
    combined_df = combined_df[combined_df['Date '].notna()]
    return combined_df

def merge_dataframes(combined_df, stock_data):
    # Merge 'combined_df' and 'stock_data' DataFrames on 'Symbol' to create a foreign key relationship
    merged_df_inner = pd.merge(combined_df, stock_data, on='Symbol', how='inner')
    return merged_df_inner

def map_mutual_funds_to_id(merged_df_inner, stock_data):
    # Create a dictionary to map mutual_fund to id from the stock DataFrame
    mutual_fund_to_id = dict(zip(stock_data['Symbol'], stock_data['id']))
    # Use the map function to create the symbol_id column in merged_df_inner
    merged_df_inner['symbol_id'] = merged_df_inner['mutual_fund'].map(mutual_fund_to_id)

def check_data(merged_df_inner, final_df):
    mutual_fund_counts = merged_df_inner.groupby('symbol_id')['id'].nunique().reset_index().rename(columns={'id': 'mutual_fund_count'})
    final_df_counts = final_df.groupby('symbol_id')['stock_id'].nunique().reset_index().rename(columns={'stock_id': 'final_df_count'})
    counts_match = (mutual_fund_counts.set_index('symbol_id')['mutual_fund_count'] ==
                    final_df_counts.set_index('symbol_id')['final_df_count'])
    # Check if all 'symbol_id' values have matching counts
    if counts_match.all():
        print("Counts match for all 'symbol_id' values.")
    else:
        print("Counts do not match for some 'symbol_id' values.")
    # If you want to see which 'symbol_id' values have mismatched counts:
    mismatched_symbol_ids = counts_match[counts_match == False].index.tolist()
    print("Mismatched 'symbol_id' values:", mismatched_symbol_ids)
    


def main():
    stock_df = get_stock_data()
    file_path = "mutual_fund.xlsx"
    mutual_fund_df = mutual_fund(file_path)
    # print(mutual_fund_df)
    merged_df_inner = merge_dataframes(mutual_fund_df, stock_df)
    map_mutual_funds_to_id(merged_df_inner, stock_df)
    # print(merged_df_inner)
    final_df = merged_df_inner.loc[:, ['mutual_fund', 'Quantity', 'id', 'Date ','symbol_id']]
    final_df.rename(columns={'id': 'stock_id', 'Quantity': 'quantity', 'Date ': 'dates'}, inplace=True)
    final_df = final_df[["quantity", "dates", "stock_id", "symbol_id"]]
    # print(final_df)

    check_data(merged_df_inner, final_df)
    # final_df.to_csv("finaldf.csv")





if __name__ == "__main__":
    main()
