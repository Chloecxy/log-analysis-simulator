import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_elements import elements, mui, dashboard, nivo
from pages.logs_overview import topbar
from st_aggrid import AgGrid, GridOptionsBuilder, StAggridTheme

st.set_page_config(layout="wide")

# Custom styling injection
st.markdown("""
    <style>
    /* Expander container */
    div[data-testid="stExpander"] {
        background-color: #575769 !important;
        border-radius: 8px;
        padding: 4px;
        margin-bottom: 8px;
    }

    div[data-testid="stExpander"] > details > summary {
        color: white !important;
        font-weight: bold;
    }

    div[data-testid="stExpander"] > details > div {
        background-color: #575769 !important;
        border-radius: 0 0 8px 8px;
        padding: 10px;
    }
    
    div.stDownloadButton > button {
        background-color: #575769;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 8px 16px;
    }
    
    div.stDownloadButton > button:hover {
        background-color: #464654;
        color: #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# Load dataframes
raw_logs_dataframe = pd.read_csv("csv/raw_log.csv")
raw_logs_dataframe['DateTime'] = pd.to_datetime(raw_logs_dataframe['DateTime'])

current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()

# Filter section
filters = []


def render_filter_labels(filter_list):
    labels_html = "<div class='filter-row'>"
    labels_html += "<span class='filter-title'>Filters: </span>"

    labels_html += "<div class='label-container'>"

    for f in filter_list:
        labels_html += f"<span class='label'>{f}</span>"
    labels_html += "</div>"

    st.markdown("""
        <style>
            .filter-row {
                display: flex;
                align-items: center;
                margin: 0px 0;
            }
            .filter-title {
                font-weight: bold;
                margin-right: 12px;
                font-size: 18px;
                color: #ffffff;
            }
            .label-container {
                display: flex;
                gap: 5px;
                flex-wrap: wrap;
                background-color: #424257;
                padding: 7px;
                border-radius: 8px;
                margin-bottom: 5px;
                flex-grow: 1;
            }
            .label {
                display: inline-block;
                background-color: #9d9dbe;
                color: white;
                padding: 6px 12px;
                margin: 4px 6px 4px 0;
                border-radius: 20px;
                font-size: 13px;
                font-family: "Segoe UI", sans-serif;
            }
            </style>
        """, unsafe_allow_html=True)

    st.markdown(labels_html, unsafe_allow_html=True)


# Top bar
with elements("filter_export"):
    topbar("Filter Export")

# Row 1
date, hour = st.columns([2, 1])

with date:
    with st.expander("Date Range", expanded=True):
        min_date = raw_logs_dataframe["DateTime"].min().date()
        max_date = raw_logs_dataframe["DateTime"].max().date()
        date_range = st.date_input("", (min_date, max_date), min_value=min_date, max_value=max_date)
        filters.append(f"Start Date: {date_range[0]}")
        filters.append(f"End Date: {date_range[1]}")

with hour:
    with st.expander("Hour Range", expanded=True):
        time_range = st.slider("", 0, 23, (0, 23))
        filters.append(f"Start Hour: {time_range[0]}")
        filters.append(f"End Hour: {time_range[1]}")

# Row 2
ip, port, username, status = st.columns([3, 2, 3, 2])

with ip:
    with st.expander("IP Address", expanded=True):
        ip_input = st.text_input("(full or partial)")

with port:
    with st.expander("Port", expanded=True):
        port_input = st.text_input("")
        if port_input.strip():
            filters.append(f"Port: {port_input}")

with username:
    with st.expander("Username", expanded=True):
        users = st.multiselect("", options=raw_logs_dataframe["Username"].unique(), default=None)
        if len(users) == 0:
            users = raw_logs_dataframe["Username"].unique()
        else:
            for user in users:
                filters.append(f"Username: {user}")

with status:
    with st.expander("Status", expanded=True):
        statuses = st.multiselect("", options=raw_logs_dataframe["Status"].unique(), default=None)
        if len(statuses) == 0:
            statuses = raw_logs_dataframe["Status"].unique()
        else:
            for status in statuses:
                filters.append(f"Status: {status}")

filtered_df = raw_logs_dataframe[
    (raw_logs_dataframe["Status"].isin(statuses)) &
    (raw_logs_dataframe["Username"].isin(users)) &
    (raw_logs_dataframe["DateTime"].dt.date >= date_range[0]) &
    (raw_logs_dataframe["DateTime"].dt.date <= date_range[1]) &
    (raw_logs_dataframe["DateTime"].dt.hour >= time_range[0]) &
    (raw_logs_dataframe["DateTime"].dt.hour <= time_range[1]) &
    (raw_logs_dataframe["Port"].astype(str).str.contains(port_input.strip(), case=False, na=False))
    ]

if ip_input.strip():
    filters.append(f"IP: {ip_input}")
    filtered_df = filtered_df[filtered_df["IP"].str.contains(ip_input.strip(), case=False, na=False)]

render_filter_labels(filters)

st.markdown("")

# Filtered table
gb = GridOptionsBuilder.from_dataframe(filtered_df)
gb.configure_pagination()
gb.configure_default_column(filterable=False, sortable=True, resizable=True)
gb.configure_selection(selection_mode="multiple", use_checkbox=True, header_checkbox=True)
gb.configure_grid_options(domLayout="normal", suppressSizeToFit=True)
grid_options = gb.build()
grid_options["floatingFilter"] = False

# Render table
response = AgGrid(
    filtered_df,
    gridOptions=grid_options,
    height=500,
    fit_columns_on_grid_load=True,
    enable_enterprise_modules=False,
    theme=StAggridTheme(base="quartz").withParams(
        backgroundColor="#c4c4d8",
        foregroundColor="#000000",  # Text colour
        headerTextColor="#000000",
        headerBackgroundColor="#898996",
        oddRowBackgroundColor="#babacd",
        headerColumnResizeHandleColor="#000000"
    )
)

# Download selected rows
selected = response["selected_rows"]
if selected is not None:
    selected_df = pd.DataFrame(selected)
    st.download_button(
        "⤓ Download Selected Rows",
        data=selected_df.to_csv(index=False).encode(),
        file_name="filtered_logs.csv",
        mime="text/csv"
    )
