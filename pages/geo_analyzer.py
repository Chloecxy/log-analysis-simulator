import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_elements import elements, mui, dashboard, nivo
from pages.logs_overview import topbar
from tools.theme import graph_theme
import plotly.express as px

st.set_page_config(layout="wide")

# Load dataframes
classified_dataframe = pd.read_csv("csv/classified_log.csv")
classified_dataframe['DateTime'] = pd.to_datetime(classified_dataframe['DateTime'])

current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()
current_date_classified_dataframe = classified_dataframe[classified_dataframe['DateTime'].dt.date == current_date]

# Getting data for cards
groupby_df = current_date_classified_dataframe.groupby(['Label', 'Country Code']).agg(
    {'Country Code': lambda x: x.count()})
groupby_df.rename(columns={'Country Code': 'Count of Events'}, inplace=True)
most_major_events_country = groupby_df.xs('major')['Count of Events'].idxmax()
most_major_events_value = groupby_df.xs('major')['Count of Events'].max()

most_minor_events_country = groupby_df.xs('minor')['Count of Events'].idxmax()
most_minor_events_value = groupby_df.xs('minor')['Count of Events'].max()

total_event_count = groupby_df.groupby(level='Country Code')['Count of Events'].sum()
top_event_country = total_event_count.idxmax()
top_event_value = total_event_count.max()

# Getting data for Nivo bar chart
reset_groupby_df = groupby_df.reset_index()
pivoted = reset_groupby_df.pivot_table(index='Country Code', columns='Label', values='Count of Events', fill_value=0)
pivoted = pivoted.reset_index()
country_severity_event_count = pivoted.to_dict(orient='records')

# Getting data for choropleth graph
total_event_count = total_event_count.reset_index()

# Layout for dashboard
layout = [
    dashboard.Item("major_country", 0, 0, 2.5, 2, isResizable=False),
    dashboard.Item("minor_country", 0, 2, 2.5, 2, isResizable=False),
    dashboard.Item("top_country", 0, 4, 2.5, 2, isResizable=False),
    dashboard.Item("severity_bar_chart", 2.5, 0, 9.5, 6, isResizable=False),
]

with elements("geo_analyzer"):
    topbar("Geo Analyzer")

    with dashboard.Grid(layout, draggableHandle=".drag-handle", rowHeight=75):
        # 3 cards
        with mui.Card(key="major_country", variant="outlined", sx={"bgcolor": "#2D2D44"}):
            mui.CardHeader(
                title=mui.Typography("Most Major Events", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#ff0000'
                }),
                className="drag-handle"
            )

            mui.CardContent(
                mui.Typography(f"{most_major_events_country}  {most_major_events_value}", sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#ff0000'

                })
            )

        with mui.Card(key="minor_country", variant="outlined", sx={"bgcolor": "#575769"}):
            mui.CardHeader(
                title=mui.Typography("Most Minor Events", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#e6ac00'
                }),
                className="drag-handle"
            )

            mui.CardContent(
                mui.Typography(f"{most_minor_events_country}   {most_minor_events_value}", sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#e6ac00'

                })
            )

        with mui.Card(key="top_country", variant="outlined", sx={"bgcolor": "#424257"}):
            mui.CardHeader(
                title=mui.Typography("Most Events", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'
                }),
                className="drag-handle"
            )

            mui.CardContent(
                mui.Typography(f"{top_event_country}   {top_event_value}", sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'

                })
            )

        # Nivo bar chart
        with mui.Card(key="severity_bar_chart", variant="outlined", className="drag-handle", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Events Severity Distribution Across Countries for {current_date}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                }
            )

            nivo.Bar(
                data=country_severity_event_count,
                keys=["major", "minor", "safe"],
                theme=graph_theme,
                colors={"scheme": "set1"},

                margin={"top": 20, "right": 100, "bottom": 120, "left": 80},
                indexBy='Country Code',
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Country",
                    "legendOffset": 40,
                    "legendPosition": "middle"
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Count of Events",
                    "legendOffset": -50,
                    "legendPosition": "middle"
                },
                legends=[
                    {
                        "anchor": "bottom-right",
                        "direction": "column",
                        "translateX": 100,
                        "itemWidth": 80,
                        "itemHeight": 20,
                        "itemsSpacing": 3,
                    }
                ],
            )

        # Choropleth Map Issues with streamlit-elements

        # 1. nivo.Choropleth crashes the app — iframe renders blank or fails silently.
        #    Even with valid GeoJSON features, the map fails to display.
        #    This suggests a possible bug or limitation in the @nivo/geo integration used by streamlit-elements.

        # 2. Alternative: plotly's px.choropleth works and supports full customization,
        #    BUT it can't be embedded inside draggable streamlit-elements cards.
        #    Reason: The draggable cards in streamlit-elements are rendered using React+JS via an iframe,
        #    while st.plotly_chart and other native Streamlit widgets render outside that iframe.
        #    These two don’t share the same DOM hierarchy — so the card just shows up empty or broken.

# Plotly express choropleth graph
st.subheader(f"Total Events Distribution Across Countries for {current_date}")
fig = px.choropleth(
    data_frame=total_event_count,
    locations="Country Code",
    color="Count of Events",
    hover_name="Country Code",
    color_continuous_scale="YlOrRd",
    range_color=[total_event_count["Count of Events"].min(), total_event_count["Count of Events"].max()],
)

fig.update_geos(
    showcountries=True,
    countrycolor="black",
    showcoastlines=True,
    coastlinecolor="black",
    showland=True,
    landcolor="#f0f0f0",
    showocean=True,
    oceancolor="#e0f7fa"
)

fig.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
)

st.plotly_chart(fig, use_container_width=True)
