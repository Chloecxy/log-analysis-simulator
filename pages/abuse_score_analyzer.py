import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_elements import elements, mui, dashboard, nivo
from pages.logs_overview import topbar
from tools.theme import graph_theme

st.set_page_config(layout="wide")

# Load dataframes
hourly_logs_dataframe = pd.read_csv("csv/hourly_logs_summary.csv")
hourly_logs_dataframe['DateTime'] = pd.to_datetime(hourly_logs_dataframe['DateTime'])
raw_logs_dataframe = pd.read_csv("csv/raw_log.csv")
raw_logs_dataframe['DateTime'] = pd.to_datetime(raw_logs_dataframe['DateTime'])
malicious_dataframe = pd.read_csv("csv/malicious_ips.csv")
malicious_dataframe['ip'] = malicious_dataframe['ip'].astype(str)
malicious_dataframe.rename(columns={'ip': 'IP'}, inplace=True)

# Data for ascore_failed_attempts graph
current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()
current_month_raw_logs_dataframe = raw_logs_dataframe[
    raw_logs_dataframe['DateTime'].dt.month == current_date.month]

ip_fail_count_df = current_month_raw_logs_dataframe.groupby(["IP"]).agg({'Status': lambda x: (x == "Failed").sum()})
ip_fail_count_df.reset_index()
ip_fail_count_df.rename(columns={'Status': 'Failed Attempt Count'}, inplace=True)

merged = malicious_dataframe.merge(ip_fail_count_df, left_on="IP", right_index=True, how="inner")
ascore_failed_attempts = merged[["Failed Attempt Count", "abuse_score"]]
ascore_failed_attempts = ascore_failed_attempts.rename(columns={'Failed Attempt Count': 'x', "abuse_score": 'y'})

ascore_failed_attempts = [{"id": "Failed Attempts vs Abuse Score", "data": ascore_failed_attempts.to_dict(orient='records')}]

# Data for top10_abuse_ips graph
top10_ips = malicious_dataframe[malicious_dataframe["abuse_score"] > 0].sort_values(by="abuse_score", ascending=False).head(10)
top10_ips = top10_ips[['IP', 'abuse_score']]
top10_ips = top10_ips.to_dict(orient='records')

# Data for ownership graph
ownership_counts = malicious_dataframe["isPublic"].value_counts()
ownership_counts = [
    {"id": "Public", "label": "Public", "value": int(ownership_counts.get(True, 0))},
    {"id": "Private", "label": "Private", "value": int(ownership_counts.get(False, 0))}
]

# Data for usage_type graph
usage_type_count = malicious_dataframe["usage_type"].value_counts()
usage_type_count = [
    {"id": str(usage_type), "label": str(usage_type), "value": int(count)}
    for usage_type, count in usage_type_count.items()
]

# Data for usage_type_ascore graph
malicious_dataframe['bin'] = pd.cut(
    malicious_dataframe['abuse_score'],
    bins=range(0, 110, 10),  # 0–100 in steps of 10
    right=False
)

hist_data = (
    malicious_dataframe.groupby(['bin', 'usage_type'])
    .size()
    .reset_index(name="count")
)

# Format for Nivo
nivo_data = []
for b in hist_data['bin'].cat.categories:
    row = {"bin": str(b)}
    for usage in hist_data['usage_type'].unique():
        val = hist_data[(hist_data['bin'] == b) & (hist_data['usage_type'] == usage)]['count']
        row[usage] = int(val.iloc[0]) if not val.empty else 0
    nivo_data.append(row)

# Layout for dashboard
layout = [
    dashboard.Item("ascore_failed_attempts", 0, 0, 5, 5, isResizable=False),
    dashboard.Item("top10_abuse_ips", 5, 0, 7, 5, isResizable=False),
    dashboard.Item("ownership", 0, 5, 4.5, 4, isResizable=False),
    dashboard.Item("usage_type", 0, 10, 4.5, 4, isResizable=False),
    dashboard.Item("usage_type_ascore", 4.5, 4, 7.5, 8, isResizable=False),
]

with elements("abuse_score_analyzer"):
    topbar("Abuse Score Analyzer")

    with dashboard.Grid(layout, draggableHandle=".drag-handle", rowHeight=75):
        with mui.Card(key="ascore_failed_attempts", variant="outlined", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Number of failed attempts against abuse score in {current_date.strftime('%B')}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d',
                },
                className="drag-handle"
            )

            nivo.Line(
                data=ascore_failed_attempts,
                theme=graph_theme,
                lineWidth=0,

                margin={"top": 15, "right": 40, "bottom": 125, "left": 90},
                xScale={"type": "linear"},
                yScale={"type": "linear", "min": "auto", "max": "auto"},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Failed Attempt Count",
                    "legendOffset": 45,
                    "legendPosition": "middle"
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Abuse Score",
                    "legendOffset": -50,
                    "legendPosition": "middle"
                },
                pointSize=5,
                useMesh=True,
                colors={"scheme": "set1"},
            )

        with mui.Card(key="top10_abuse_ips", variant="outlined", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Top 10 IPs with Highest Abuse Score in {current_date.strftime('%B')}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                },
                className="drag-handle"
            )

            nivo.Bar(
                data=top10_ips,
                theme=graph_theme,
                colorBy="value",
                colors={"scheme": "red_yellow_green"},
                padding=0.3,
                indexBy='IP',
                keys=["abuse_score"],
                margin={"top": 20, "right": 25, "bottom": 150, "left": 80},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": -17,
                    "legend": "IP",
                    "legendOffset": 60,
                    "legendPosition": "middle"
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Abuse Score",
                    "legendOffset": -50,
                    "legendPosition": "middle"
                }
            )

        with mui.Card(key="ownership", variant="outlined", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Ownership of IPs in {current_date.strftime('%B')}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                },
                className="drag-handle"
            )

            nivo.Pie(
                data=ownership_counts,
                theme=graph_theme,
                colors={"scheme": "nivo"},
                margin={"top": 5, "right": 20, "bottom": 80, "left": 20},
                innerRadius=0.5,
                activeOuterRadiusOffset=5
            )

        with mui.Card(key="usage_type", variant="outlined", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Usage Types of IPs in {current_date.strftime('%B')}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                },
                className="drag-handle"
            )

            nivo.Pie(
                data=usage_type_count,
                theme=graph_theme,
                colors={"scheme": "nivo"},
                margin={"top": 0, "right": 270, "bottom": 110, "left": 20},
                innerRadius=0.5,
                activeOuterRadiusOffset=5,
                enableArcLinkLabels=False,

                legends=[
                    {
                        "anchor": 'right',
                        "direction": 'column',
                        "translateX": 110,
                        "itemWidth": 100,
                        "itemHeight": 25,
                        "symbolShape": 'circle',

                    }
                ]

            )

        with mui.Card(key="usage_type_ascore", variant="outlined", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Distribution of Usage Type and Abuse Score of IPs in {current_date.strftime('%B')}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                },
                className="drag-handle"
            )

            nivo.Bar(
                data=nivo_data,
                theme=graph_theme,
                colorBy="id",
                colors={"scheme": "nivo"},
                padding=0.1,
                indexBy='bin',
                keys=list(hist_data['usage_type'].unique()),
                groupMode="grouped",
                margin={"top": 10, "right": 10, "bottom": 150, "left": 75},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": -17,
                    "legend": "Abuse Score",
                    "legendOffset": 60,
                    "legendPosition": "middle"
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "IP Count",
                    "legendOffset": -50,
                    "legendPosition": "middle"
                }
            )
