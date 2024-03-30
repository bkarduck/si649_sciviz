import streamlit as st
import pandas as pd


# Example dataset
data = {
    'make': ['Cadillac', 'Cadillac', 'Tesla', 'Tesla'],
    'model': ['Escalade', 'CTS', 'Model S', 'Model X'],
    'other_data': [1, 2, 3, 4]  # Placeholder for other data columns
}
df = pd.DataFrame(data)

# Sidebar selection for 'make'
make_selection = st.sidebar.selectbox('Select Make:', options=df['make'].unique())

# Filter models based on selected make
filtered_models = df[df['make'] == make_selection]['model'].unique()

# Sidebar selection for 'model', filtered based on make selection
model_selection = st.sidebar.selectbox('Select Model:', options=filtered_models)

# Display selections
st.write(f"You selected: {make_selection} {model_selection}")

# Optional: Further actions based on the selection
# For instance, displaying data or results based on the selections
filtered_data = df[(df['make'] == make_selection) & (df['model'] == model_selection)]
st.write(filtered_data)
