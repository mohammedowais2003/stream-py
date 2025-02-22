import pandas as pd
import streamlit as st
import os
from io import BytesIO

st.set_page_config(page_title="Class Assignment 1", layout='wide')

# Title and Description
st.title("FAMILY -SALARY CHART")
st.write("Transform your file between CSV and Excel formats with built-in data cleaning and visualization!")

# File Uploader
uploaded_files = st.file_uploader("Upload your files (accepts CSV or Excel):", type=["csv", "xlsx"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        file_ext = os.path.splitext(file.name)[-1].lower()

        # Read the file
        try:
            if file_ext == ".csv":
                df = pd.read_csv(file)
            elif file_ext == ".xlsx":
                df = pd.read_excel(file, engine='openpyxl')
            else:
                st.error(f"Unsupported file type: {file_ext}")
                continue
        except Exception as e:
            st.error(f"Error reading {file.name}: {str(e)}")
            continue

        # Display the file preview
        st.subheader(f"Preview of {file.name}")
        st.dataframe(df.head())

        # Data Cleaning
        st.subheader(f"Data Cleaning Options for {file.name}")
        remove_duplicates = st.checkbox(f"Remove Duplicates ({file.name})")
        fill_missing_values = st.checkbox(f"Fill Missing Values ({file.name})")

        if remove_duplicates:
            df.drop_duplicates(inplace=True)
            st.success("Duplicates removed!")

        if fill_missing_values:
            numeric_cols = df.select_dtypes(include=["number"]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            st.success("Missing values filled with column mean!")

        # Column Selection
        st.subheader(f"Select Columns to Keep for {file.name}")
        selected_columns = st.multiselect(f"Choose columns for {file.name}", df.columns, default=df.columns)
        df = df[selected_columns]

        # Data Visualization
        st.subheader(f"Data Visualization for {file.name}")
        if st.checkbox(f"Show Visualization ({file.name})"):
            numeric_cols = df.select_dtypes(include="number")
            if numeric_cols.shape[1] >= 2:
                st.bar_chart(numeric_cols.iloc[:, :2])
            else:
                st.warning("Not enough numerical columns for visualization.")

        # Conversion Options
        st.subheader(f"Convert {file.name} to:")
        conversion_type = st.radio(f"Convert {file.name} to:", ["CSV", "Excel"], key=f"conv_{file.name}")

        # Convert and Download
        if st.button(f"Download {file.name} as {conversion_type}", key=f"download_{file.name}"):
            buffer = BytesIO()
            try:
                if conversion_type == "CSV":
                    df.to_csv(buffer, index=False)
                    file_name = file.name.replace(file_ext, ".csv")
                    mime_type = "text/csv"
                else:  # Excel conversion
                    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False)
                    file_name = file.name.replace(file_ext, ".xlsx")
                    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

                buffer.seek(0)
                st.download_button(
                    label=f"Download {file_name}",
                    data=buffer,
                    file_name=file_name,
                    mime=mime_type
                )
                st.success(f"File {file_name} ready for download!")
            except Exception as e:
                st.error(f"Error converting {file.name}: {str(e)}")

    st.success("All files processed successfully!")
