import streamlit as st
import pandas as pd
import numpy as np  # We'll need numpy to check for NaN

# UI Elements
st.title("TKU reports, Virtuous to Mailer CSV Formatting")

# Display the format of the input CSV
txt = st.text_area(
    "TKU List Column Structure",
    "Contact Id | "
    "Contact Name | "
    "Contact Type | "
    "Contact Informal Name | "
    "Contact Primary First Name | "
    "Contact Primary Last Name | "
    "Contact Primary Address Line 1 | "
    "Contact Primary Address City | "
    "Contact Primary Address State | "
    "Contact Primary Address Postal | "
    "Contact Primary Address Country | "
    "Gift Id | "
    "Gift Date | "
    "Amount | "
    "Segment Code | "
    "Notes",
)


uploaded_file = st.file_uploader(
    "Upload your TKU List file in the CSV format", type=["csv"]
)

if uploaded_file is not None:
    # Load the CSV
    data = pd.read_csv(uploaded_file, encoding="latin1")

    def flatten_lists(df):
        cols = ["Gift Id", "Gift Date", "Amount", "Segment Code", "Notes"]
        max_gifts = max(
            df[cols[0]].str.len()
        )  # Find maximum gifts using the first column
        for i in range(1, max_gifts + 1):
            for col in cols:
                df[f"{col} {i}"] = df[col].apply(
                    lambda x: x[i - 1] if i <= len(x) else None
                )
        return df.drop(cols, axis=1)

    # Modified Transformation
    def transform_data(data):
        transformed_data = data.groupby("Contact Id").agg(list).reset_index()

        # Select columns to deduplicate
        dedup_cols = [
            "Contact Name",
            "Contact Type",
            "Contact Informal Name",
            "Contact Primary First Name",
            "Contact Primary Last Name",
            "Contact Primary Address Line 1",
            "Contact Primary Address City",
            "Contact Primary Address State",
            "Contact Primary Address Postal",
            "Contact Primary Address Country",
        ]
        transformed_data[dedup_cols] = transformed_data[dedup_cols].apply(
            lambda x: x.str[0]
        )

        transformed_data = flatten_lists(transformed_data)
        return transformed_data

    # Modified transformation
    transformed_data = transform_data(data.copy())
    transformed_data = transformed_data.set_index(
        "Contact Id"
    )  # Or another suitable column

    print(transformed_data.info())

    # Apply formatting within the display context
    # Example: Remove decimals if Contact IDs are numeric
    transformed_data.index = transformed_data.index.map("{:.0f}".format)
    numeric_columns = transformed_data.select_dtypes(include=["float64"]).columns
    print(numeric_columns)

    def format_all_columns(x):
        if isinstance(x, int):
            return f"{x:,}".replace(",", "")
        elif isinstance(x, float):
            if np.isnan(x):  # Check for an empty float64 (NaN)
                return ""  # Return empty string
            elif x.is_integer():
                return f"{x:.0f}"
            else:
                return f"{x:.2f}"
        else:
            try:
                return str(x)
            except ValueError:
                return x

    # Apply to relevant columns (modify column_subset as needed)
    column_subset = transformed_data.select_dtypes(include=["int64", "float64"]).columns
    transformed_data[column_subset] = transformed_data[column_subset].map(
        format_all_columns
    )

    st.download_button(
        label="Download as CSV",
        data=transformed_data.to_csv(index=True),
        file_name="TKU List Final.csv",
    )
    st.dataframe(transformed_data)
