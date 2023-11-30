# import pandas as pd
# from sqlalchemy import create_engine

# file_path = 'mutual_fund.xlsx'

# # Read the Excel file into a dictionary of DataFrames, with tab names as keys
# dfs = pd.read_excel(file_path, sheet_name=None,header=0)

# # Iterate through the dictionary of DataFrames and add a new column 'Tab Name'
# for tab_name, df in dfs.items():
#     df['mutual_fund'] = tab_name

# # Combine all DataFrames into a single DataFrame
# combined_df = pd.concat(dfs.values(), ignore_index=True)

# # Optional: Reset the index
# combined_df.reset_index(drop=True, inplace=True)

# # Remove columns with mostly NaN values
# combined_df = combined_df.dropna(axis=1, how='all')

# # Remove the last column using the drop method
# combined_df = combined_df.drop(columns=combined_df.columns[-1])

# # Get the first row as the new column names
# new_column_names = combined_df.iloc[0]

# # Rename the columns based on the first row values
# combined_df.columns = new_column_names

# # Drop the first row (which is now the column names)
# combined_df = combined_df.iloc[1:]

# combined_df.rename(columns={'Value (Rs.)':'value','SSIS': 'mutual_fund', 'id':'stock_id'}, inplace=True)

# stock_data = pd.read_csv("stock.csv")
# # print(stock_data)

# # Merge 'orders' and 'customers' DataFrames on 'customer_id' to create a foreign key relationship
# merged_df_right = pd.merge(combined_df, stock_data, on='Symbol', how='right')
# # print(merged_df_right)

# #df_new = merged_df_right.loc[:, ['Symbol','mutual_fund' ,'Quantity','id','Date ']]
# df_new = merged_df_right.loc[:, ['mutual_fund','Quantity','id','Date ']]
# # Create a dictionary to map mutual_fund to id from the stock DataFrame
# mutual_fund_to_id = dict(zip(stock_data['Symbol'], stock_data['id']))

# # Use the map function to create the symbol_id column in df_new
# df_new['symbol_id'] = df_new['mutual_fund'].map(mutual_fund_to_id)

# df_new.rename(columns={'id':'stock_id','Quantity':'quantity','Date ':'dates' }, inplace=True)
# final_df = df_new[["quantity","dates","stock_id","symbol_id"]]
# # print(final_df)


# # insert into the database
# conn_string = 'postgresql://postgres:attribute#123@localhost/mutualfund'
# db = create_engine(conn_string)
# conn = db.connect()
                        
# # Insert data from the DataFrame into the existing table
# final_df.to_sql('report_mutualfund', con=conn, schema='pt_script', if_exists='append', index=False)

# # Close the SQLAlchemy connection
# conn.close()
import pandas as pd
from sqlalchemy import create_engine

def read_excel_file(file_path):
    # Read the Excel file into a dictionary of DataFrames, with tab names as keys
    dfs = pd.read_excel(file_path, sheet_name=None, header=0)
    return dfs

def add_tab_name_column(dfs):
    # Iterate through the dictionary of DataFrames and add a new column 'Tab Name'
    for tab_name, df in dfs.items():
        df['mutual_fund'] = tab_name

def combine_dataframes(dfs):
    # Combine all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs.values(), ignore_index=True)
    return combined_df

def clean_dataframe(combined_df):
    # Optional: Reset the index
    combined_df.reset_index(drop=True, inplace=True)

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

    combined_df.rename(columns={'Value (Rs.)': 'value', 'SSIS': 'mutual_fund', 'id': 'stock_id'}, inplace=True)

    return combined_df

def merge_dataframes(combined_df, stock_data):
    # Merge 'combined_df' and 'stock_data' DataFrames on 'Symbol' to create a foreign key relationship
    merged_df_right = pd.merge(combined_df, stock_data, on='Symbol', how='right')
    return merged_df_right

def map_mutual_funds_to_id(merged_df_right, stock_data):
    # Create a dictionary to map mutual_fund to id from the stock DataFrame
    mutual_fund_to_id = dict(zip(stock_data['Symbol'], stock_data['id']))

    # Use the map function to create the symbol_id column in merged_df_right
    merged_df_right['symbol_id'] = merged_df_right['mutual_fund'].map(mutual_fund_to_id)

def insert_data_into_database(final_df, conn_string):
    # Insert data from the DataFrame into the existing table
    db = create_engine(conn_string)
    conn = db.connect()
    final_df.to_sql('report_mutualfund', con=conn, schema='pt_script', if_exists='append', index=False)
    conn.close()

def main():
    file_path = 'mutual_fund.xlsx'
    stock_data = pd.read_csv("stock.csv")
    conn_string = ''

    dfs = read_excel_file(file_path)
    add_tab_name_column(dfs)
    combined_df = combine_dataframes(dfs)
    cleaned_df = clean_dataframe(combined_df)
    merged_df_right = merge_dataframes(cleaned_df, stock_data)
    map_mutual_funds_to_id(merged_df_right, stock_data)
    final_df = merged_df_right.loc[:, ['mutual_fund', 'Quantity', 'id', 'Date ','symbol_id']]
    final_df.rename(columns={'id': 'stock_id', 'Quantity': 'quantity', 'Date ': 'dates'}, inplace=True)
    final_df = final_df[["quantity", "dates", "stock_id", "symbol_id"]]
    # print(final_df)
    insert_data_into_database(final_df, conn_string)

if __name__ == "__main__":
    main()
