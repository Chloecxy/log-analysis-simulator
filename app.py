import streamlit as st
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = None


def logout_page():
    st.title("Log Out")
    if st.button("Log Out"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.rerun()

def login_page():
    st.title("Log In")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Log In"):
        if username == "admin" and password == "admin":
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Invalid credentials")

# Define pages
login = st.Page(login_page, title="Log In", icon=":material/login:")
logout = st.Page(logout_page, title="Log Out", icon=":material/logout:")

welcome = st.Page("pages/welcome.py", title="Welcome", icon="🎉", default=True)
dashboard = st.Page("pages/logs_overview.py", title="Logs Overview", icon="💻")
geo_analyzer = st.Page("pages/geo_analyzer.py", title="Geo Analyzer", icon="🗺️")
abuse_analyzer = st.Page("pages/abuse_score_analyzer.py", title="Abuse Score Analyzer", icon="📊")
filter_export = st.Page("pages/filter_export.py", title="Filter & Export", icon="📃")

# Navigation logic
if st.session_state.logged_in:
    nv = st.navigation(
        {
            # may add profile page
            "👤Account": [welcome, logout],
            "🗃️ Reports": [dashboard, geo_analyzer, abuse_analyzer],
            # may add settings
            "🛠️ Tools": [filter_export]
        }
    )
else:
    nv = st.navigation([login])

nv.run()

