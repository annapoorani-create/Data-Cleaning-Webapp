import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Welcome to the data cleaning app!")

# This is for a variables used later on
if "columns_to_delete_nulls" not in st.session_state:
    st.session_state["columns_to_delete_nulls"] = []

if "columns_to_preserve_nulls" not in st.session_state:
    st.session_state["columns_to_preserve_nulls"] = []

if "columns_to_replace_nulls" not in st.session_state:
    st.session_state["columns_to_replace_nulls"] = []

if "first_button_clicked" not in st.session_state:
    st.session_state["first_button_clicked"] = False

if "second_button_clicked" not in st.session_state:
    st.session_state["second_button_clicked"] = False

if "df_temp" not in st.session_state:
    st.session_state["df_temp"] = pd.DataFrame()

if "missing_by_column" not in st.session_state:
    st.session_state["missing_by_column"] = pd.Series()

if "threshold" not in st.session_state:
    st.session_state["threshold"] = None   
        
if "missing_val" not in st.session_state:
    st.session_state["missing_val"] = "hello"

# Allow users to upload a CSV file (eventually expand to an option menu for many different file types)
uploaded_file = st.file_uploader("Upload your CSV", type=["csv", "xlsx"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success("Your file has been uploaded!")
    st.session_state["df"] = df

    # Ask users for the missing value indicator 0, NaN, -, whatever it is. Could start with just assuming NaN
    choice = st.selectbox("Are missing values in your data denoted by a number or text? (Total null value count will update.)", ['Number','Text'])
    
    if choice == 'Text':
        missing_val = st.text_input("What denotes missing values in your dataset? e.g., NaN, -, etc.")
        df_temp = df.replace(missing_val,np.nan)
    else:
        missing_val = st.number_input("Enter an integer:", step=1)
        df_temp = df.replace(missing_val,np.nan)
        
    st.session_state['df_temp'] = df_temp
    st.session_state['df'] = df
    st.session_state['missing_val'] = missing_val
    
    if st.button("Submit!"):
        first_button_clicked = True
        st.session_state['first_button_clicked'] = first_button_clicked
        
    first_button_clicked = st.session_state["first_button_clicked"]
    
    if first_button_clicked == True:
        total_nans = df_temp.isna().sum().sum()
        st.write("Total null values:", total_nans)
        
        threshold = len(df_temp)*0.4
        st.session_state["threshold"] = threshold
        missing_by_column = df_temp.isna().sum()
        st.session_state['missing_by_column'] = missing_by_column

        # Count missing by column and allow users to choose to delete columns.
        threshold = st.session_state["threshold"]
        count_above = (missing_by_column > threshold).sum()
            
        st.write(f"We found {count_above} columns in your data frame with over 40% missing values.")

        st.session_state["count_above"] = count_above
        
        if count_above > 0:
            st.write("These are the columns with over 40% missing values:")
            st.write(missing_by_column[missing_by_column > threshold].index.tolist())
        
        st.write("""Choose how you would like to handle each of the columns in your dataframe, keeping in mind the columns with more than 40% missing values 
        (printed above if there were any).  All unselected columns will be deleted. The multiselects will only show columns that have thus far not been selected. 
        If you choose to delete null values in a column listed above, over 40% of your data could be deleted.""")
        
        column_names = df.columns
        
        st.session_state["columns_to_delete_nulls"] = st.multiselect("Select columns to delete all missing values from, keeping in mind this means deleting entire rows of data:",options=[x for x in column_names if x not in st.session_state["columns_to_replace_nulls"] and x not in st.session_state["columns_to_preserve_nulls"]],default=st.session_state.get("columns_to_delete_nulls", []))
        
        st.session_state["columns_to_replace_nulls"] = st.multiselect("Select columns to replace null values with the column average:",options= [x for x in column_names if x not in st.session_state["columns_to_delete_nulls"] and x not in st.session_state["columns_to_preserve_nulls"]],default=st.session_state.get("columns_to_replace_nulls",[]))
        
        st.session_state["columns_to_preserve_nulls"] = st.multiselect("Select columns to preserve the null values as they are, without messing up indexing if you choose to delete nulls in other columns:",options= [x for x in column_names if x not in st.session_state["columns_to_replace_nulls"] and x not in st.session_state["columns_to_delete_nulls"]],default=st.session_state.get("columns_to_preserve_nulls",[]))
        

        df_temp = st.session_state["df_temp"]
        df = st.session_state["df"]
            
        if st.button("Save my preferences"):
            st.session_state["second_button_clicked"] = True

        if st.session_state["second_button_clicked"] == True:
                # Reloading the columns, now separated by user preferences
            
                columns_to_delete_nulls = st.session_state["columns_to_delete_nulls"]
                columns_to_replace_nulls = st.session_state["columns_to_replace_nulls"]
                columns_to_preserve_nulls = st.session_state["columns_to_preserve_nulls"]
            
                df_temp = st.session_state["df_temp"]
                df = st.session_state["df"]
                missing_val = st.session_state["missing_val"]

                count_above = st.session_state["count_above"]
            
                df_for_deletions = df_temp[columns_to_delete_nulls]
                df_for_replacements = df_temp[columns_to_replace_nulls]
                df_for_preservation = df_temp[columns_to_preserve_nulls]

                for col in df_for_replacements.columns:
                    if df_for_replacements[col].isna().all():  # if entire column is NaN
                        df_for_replacements[col] = 0  
                    else:
                        df_for_replacements[col].fillna(df_for_replacements[col].mean(), inplace=True)
                        
                df_for_preservation = df_for_preservation.replace(np.nan,"__Missing__")

                df_temp = pd.concat([df_for_replacements,df_for_deletions,df_for_preservation],axis=1)
                df_temp = df_temp.dropna().reset_index(drop=True)
                df_temp = df_temp.replace("__Missing__",np.nan)

                # Convert DataFrame to CSV bytes
                csv_bytes = df_temp.to_csv(index=False).encode('utf-8')
            
                # Download button
                st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="cleaned_data.csv",
                mime="text/csv",
                key = 'get it back'
            )
