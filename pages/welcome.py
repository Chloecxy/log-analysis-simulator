import streamlit as st

st.set_page_config(page_title="Cybersecurity Dashboard", layout="wide")

st.title("🛡️ Cybersecurity Log Analyzer Dashboard")
st.markdown("""
Welcome to the **Threat Analysis Dashboard**.  
Use the sidebar to navigate through the views:
- View log summaries
- Analyze geographical distribution of threats
- Explore abuse scores
- Filter and export flagged IPs
""")