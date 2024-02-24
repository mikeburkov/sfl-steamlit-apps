import streamlit as st
import pandas as pd

# UI Elements
st.title("TKU reports, Virtuous to Mailer CSV Formatting")
uploaded_file = st.file_uploader("Upload your CSV file", type=['csv'])

if uploaded_file is not None:
    # Load the CSV
    data = pd.read_csv(uploaded_file)

    def flatten_lists(df):
      cols = ['Gift Id','Gift Date', 'Amount', 'Segment Code', 'Notes']
      max_gifts = max(df[cols[0]].str.len())  # Find maximum gifts using the first column
      for i in range(1, max_gifts + 1):
          for col in cols:
              df[f'{col} {i}'] = df[col].apply(lambda x: x[i-1] if i <= len(x) else None)
      return df.drop(cols, axis=1)

  # Modified Transformation
    def transform_data(data):
      transformed_data = data.groupby('Contact Id').agg(list).reset_index() 
    
      # Select columns to deduplicate
      dedup_cols = ['Contact Name','Contact Type','Contact Informal Name','Contact Primary First Name','Contact Primary Last Name','Contact Primary Address Line 1','Contact Primary Address City','Contact Primary Address State','Contact Primary Address Postal','Contact Primary Address Country',] 
      transformed_data[dedup_cols] = transformed_data[dedup_cols].apply(lambda x: x.str[0])

      transformed_data = flatten_lists(transformed_data)
      return transformed_data

    # Modified transformation
    transformed_data = transform_data(data.copy())
    transformed_data = transformed_data.set_index('Contact Id') # Or another suitable column

    print(transformed_data.info())
    

    # Apply formatting within the display context
    # Example: Remove decimals if Contact IDs are numeric
    transformed_data.index = transformed_data.index.map('{:.0f}'.format)
    st.download_button(label="Download as CSV", 
                       data=transformed_data.to_csv(index=True),
                       file_name='TKU List Final.csv')

    def format_gift_and_amount(val):   
      if val is None:  # Check for None explicitly
          return val   # Return None without formatting

      try:
          # Try converting to integer
          as_int = int(val) 
          return '{:.0f}'.format(as_int)
      except ValueError:
          try:
              # Try converting to float
              as_float = float(val)
              return '{:.0f}'.format(as_float) if as_float.is_integer() else '{:.2f}'.format(as_float)  
          except ValueError:
              # If all else fails, return the original value
              return val 
# Apply formatting 
    #st.dataframe(transformed_data.style.map(format_gift_and_amount))  # Use map instead of applymap 
    st.dataframe(transformed_data)  # Use map instead of applymap 

#    st.dataframe(transformed_data.style.format({
#      'Gift Id': '{:.0f}',  # Remove decimal separators for Gift Id
#      'Amount':  lambda x: f'{x:.0f}' if x.is_integer() else f'{x:.2f}' 
#  }))

    
