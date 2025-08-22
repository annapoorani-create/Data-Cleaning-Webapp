import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Welcome to the data cleaning app!")

def choosing_final_format(unmodified_data_frame,reset_dataframe)
        st.write("You can select each option and download each csv if you would like more than one option.")
        choice = st.radio("Do you want to now remove all rows with null values, replace all null values, or recieve your data frame with any columns you decided to remove now removed?", ["Remove", "Replace","Recieve as is"])

    
        if choice == "Remove":
            unmodified_data_frame = reset_data_frame
            unmodified_data_frame = unmodified_data_frame.dropna().reset_index(drop=True)
            unmodified_data_frame = unmodified_data_frame.replace("___MISSING VAL HiHi___",np.nan)
            st.write("Here’s the head of your DataFrame:")
            st.dataframe(unmodified_data_frame.head())
            
            # Convert DataFrame to CSV bytes
            csv_bytes = unmodified_data_frame.to_csv(index=False).encode('utf-8')
            
            # Download button
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="cleaned_data.csv",
                mime="text/csv",
                key = 'removal')
            
        if choice == "Replace":
            unmodified_data_frame = reset_data_frame
            # Only replace NaNs in numeric columns
            numeric_cols = unmodified_data_frame.select_dtypes(include=np.number).columns

            for col in numeric_cols:
                unmodified_data_frame[col] = unmodified_data_frame[col].fillna(unmodified_data_frame[col].mean())
            unmodified_data_frame = unmodified_data_frame.replace("___MISSING VAL HiHi___",np.nan)
            
            st.write("Here’s the head of your DataFrame:")
            st.dataframe(unmodified_data_frame.head())
            
            # Convert DataFrame to CSV bytes
            csv_bytes = unmodified_data_frame.to_csv(index=False).encode('utf-8')
            
            # Download button
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="cleaned_data.csv",
                mime="text/csv",
                key = 'replacing'
            )
            
        if choice == "Recieve as is":
            unmodified_data_frame = reset_data_frame
            unmodified_data_frame = unmodified_data_frame.replace("___MISSING VAL HiHi___",np.nan)
            
            st.write("Here’s the head of your DataFrame:")
            st.dataframe(unmodified_data_frame.head())
            
            # Convert DataFrame to CSV bytes
            csv_bytes = unmodified_data_frame.to_csv(index=False).encode('utf-8')
            
            # Download button
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name="cleaned_data.csv",
                mime="text/csv",
                key = 'get it back'
            )

# This is for a variables used later on
if "columns_to_keep" not in st.session_state:
    st.session_state["columns_to_keep"] = []

if "button_clicked" not in st.session_state:
    st.session_state["button_clicked"] = False

if "clicked1" not in st.session_state:
    st.session_state["clicked1"] = False

if "df_temp" not in st.session_state:
    st.session_state["df_temp"] = pd.DataFrame()

if "missing_by_column" not in st.session_state:
    st.session_state["missing_by_column"] = pd.Series()

if "threshold" not in st.session_state:
    st.session_state["threshold"] = None


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
        
        df_temp = st.session_state['df_temp']
        df = st.session_state['df']
        missing_val = st.session_state['missing_val']
        button_clicked = True
        st.session_state['button_clicked'] = button_clicked
        
    button_clicked = st.session_state["button_clicked"]
    
    if button_clicked == True and 'df_temp' in locals():
        total_nans = df_temp.isna().sum().sum()
        st.write("Total null values:", total_nans)
        
        threshold = len(df_temp)*0.4
        st.session_state["threshold"] = threshold
        missing_by_column = df_temp.isna().sum()
        st.session_state['missing_by_column'] = missing_by_column

        # Count missing by column and allow users to choose to delete columns.
        threshold = st.session_state["threshold"]
        count_above = (missing_by_column > threshold).sum()
        if count_above > 0:
            st.write(f"We found {count_above} columns in your data frame with over 40% missing values. Choose which of them you would like to KEEP - if any. If you choose to remove/replace null values later, these columns will still be preserved exactly how they are.")
            columns_to_keep = 1
        else:
            st.write("We found no columns with over 40% missing values.")
            columns_to_keep = None
            choosing_final_format(df,df_temp)


        st.session_state['count_above'] = count_above

    if 'count_above' in st.session_state and columns_to_keep != None:
        threshold = st.session_state["threshold"]
        st.session_state["columns_to_keep"] = st.multiselect("Select columns to KEEP",options=missing_by_column[missing_by_column > threshold].index.tolist(),default=st.session_state.get("columns_to_keep", []))

        if st.button("Save my preferences"):
            st.session_state['clicked1'] = True

            
    if st.session_state['clicked1'] == True:
        # Reloading the columns to preserve, the temporary dataframe with NaNs, and the original dataframe
        columns_to_keep = st.session_state["columns_to_keep"]
        df_temp = st.session_state["df_temp"]
        df = st.session_state["df"]
        
        # Proceed only if there are values in columns_to_keep
        if columns_to_keep != None:
            # Save columns to be preserved
            df_temp_2 = df_temp[columns_to_keep]

            # Drop the rest
            missing_by_column = st.session_state['missing_by_column'] 
            threshold = st.session_state.get("threshold")
            for name in missing_by_column[missing_by_column > threshold].index.tolist():
                if name not in columns_to_keep:
                    df_temp.drop(name,axis=1,inplace=True)
        else:
            # Drop all unecessary columns
            for name in missing_by_column[missing_by_column > threshold]:
                df_temp.drop(name,axis=1,inplace=True)

        # Prevent the NaNs in columns_to_keep to be preserved from being detected
        df_temp_2 = df_temp_2.replace(np.nan,"___MISSING VAL HiHi___")

        # Remove the COLUMNS_to_keep (not the unwanted columns, those were already removed) from the temporary dataframe
        if columns_to_keep != None:
            df_temp.drop(columns_to_keep,inplace=True,axis=1)

        # Put them back in
        df = pd.concat([df_temp,df_temp_2],axis=1)
        my_df_2 = df


# The final section - getting their data back!
        
        choosing_final_format(df,my_df_2)
