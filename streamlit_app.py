import streamlit as st


# Page config
st.set_page_config(
    page_title="Trend Fashion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

PROJECT_TITLE = "AI Engineer Fellowship"
PROJECT_DESC  = "Capstone: Dashboard & Chatbot Analisis Tren Fashion"

# --- CSS untuk menyisipkan teks di atas menu navigasi ---
st.markdown(f"""
    <style>
    [data-testid="stSidebarNav"]::before {{
        content: "{PROJECT_TITLE}\\A {PROJECT_DESC}\\A\\A 📂 Menu Utama";
        white-space: pre-wrap;            /* agar \\A jadi baris baru */
        display: block;
        margin: 1rem 0 0.5rem 0.5rem;     /* ruang di sekitar teks */
        font-size: 1rem;
        font-weight: 600;
        color: #333333;
    }}
    </style>
""", unsafe_allow_html=True)

# Define the pages
app = st.Page("app.py", title="Main Page", icon="🎈")
predict = st.Page("predict.py", title="Chatbot Asistent", icon="❄️")

# Set up navigation
pg = st.navigation([app, predict])

# Run the selected page
pg.run()