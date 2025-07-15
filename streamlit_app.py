import streamlit as st




# Define the pages
app = st.Page("app.py", title="Main Page", icon="🎈")
predict = st.Page("predict.py", title="Chatbot Asistent", icon="❄️")

# Set up navigation
pg = st.navigation([app, predict])

# Run the selected page
pg.run()