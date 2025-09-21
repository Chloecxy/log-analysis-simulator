import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_elements import elements, mui, dashboard, nivo
from tools.theme import graph_theme


st.set_page_config(layout="wide")

# Load dataframes
hourly_logs_dataframe = pd.read_csv("csv/hourly_logs_summary.csv")
hourly_logs_dataframe['DateTime'] = pd.to_datetime(hourly_logs_dataframe['DateTime'])
raw_logs_dataframe = pd.read_csv("csv/raw_log.csv")
raw_logs_dataframe['DateTime'] = pd.to_datetime(raw_logs_dataframe['DateTime'])

# Cards data
# current_date = datetime.now()
current_date = datetime.strptime("2025 Jul 08", "%Y %b %d").date()
current_date_hourly_logs_dataframe = hourly_logs_dataframe[hourly_logs_dataframe['DateTime'].dt.date == current_date]
logs_count = int(raw_logs_dataframe[raw_logs_dataframe['DateTime'].dt.date == current_date]['IP'].count())
major_count = int(current_date_hourly_logs_dataframe['major'].sum())
minor_count = int(current_date_hourly_logs_dataframe['minor'].sum())

# Logs Table data
top10_latest_logs = raw_logs_dataframe[raw_logs_dataframe['DateTime'].dt.date == current_date] \
    .sort_values(by='DateTime', ascending=False).head(10)
top10_latest_logs_dict = top10_latest_logs.to_dict(orient='records')
columns = top10_latest_logs.columns.to_list()

# Nivo format (Line chart)
current_date_hourly_logs_dataframe = [
    {
        "id": severity,
        "data": [{"x": row["DateTime"].strftime("%b %d %H:%M"), "y": row[severity]} for _, row in
                 current_date_hourly_logs_dataframe.iterrows()]
    }
    for severity in ["major", "minor", "safe"]
]


# Function for top app bar
def topbar(title):
    mui.AppBar(position="static", sx={
        "marginBottom": "13px",
        "backgroundColor": "#2E2E44"
    })(
        mui.Toolbar(
            mui.Box(sx={
                "display": "flex",
                "alignItems": "center",
                "justifyContent": "space-between",
                "width": "100%",
                "position": "relative"
            })(
                # Title
                mui.Typography(title, sx={
                    "fontSize": "22px",
                    "fontWeight": "Bold",

                }),

                # DateTime
                mui.Typography(f'📆 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', sx={
                    "fontSize": "20px",
                    "textAlign": 'center',
                }),

                mui.Box(sx={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "12px"
                })(
                    mui.Typography(st.session_state.username.upper(), sx={
                        "fontSize": "18px",
                        "fontWeight": 500,
                    }),

                    mui.IconButton(
                        mui.icon.AccountCircle,
                        size="large",
                        color="inherit"
                    )
                )
            )
        )
    )


# Layout for dashboard
layout = [
    dashboard.Item("total_logs", 0, 0, 1.5, 2, isResizable=False),
    dashboard.Item("average_logs", 1.5, 0, 1.5, 2, isResizable=False),
    dashboard.Item("major_logs", 0, 2, 1.5, 2, isResizable=False),
    dashboard.Item("minor_logs", 1.5, 2, 1.5, 2, isResizable=False),
    dashboard.Item("raw_logs", 3, 0, 9, 4, isResizable=False),
    dashboard.Item("logs_line_graph", 0, 4, 12, 6, isResizable=False),

]

with elements("logs_overview"):
    # Top AppBar
    topbar("Logs Overview")

    with dashboard.Grid(layout, draggableHandle=".drag-handle", rowHeight=75):
        # 4 cards
        with mui.Card(key="total_logs", variant="outlined", sx={"bgcolor": "#424257"}):
            mui.CardHeader(
                title=mui.Typography("Total", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'

                }),
                className="drag-handle"
            )
            mui.CardContent(
                mui.Typography(logs_count, sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'

                })
            )

        with mui.Card(key="average_logs", variant="outlined", sx={"bgcolor": "#6c6c7c"}):
            mui.CardHeader(
                title=mui.Typography("Average", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'

                }),
                className="drag-handle"
            )
            mui.CardContent(
                mui.Typography(round(logs_count / datetime.now().hour), sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#80f2d0'

                })
            )

        with mui.Card(key="major_logs", variant="outlined", sx={"bgcolor": "#2D2D44"}):
            mui.CardHeader(
                title=mui.Typography("Major", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#ff0000'

                }),
                className="drag-handle"
            )
            mui.CardContent(
                mui.Typography(major_count, sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#ff0000'
                })
            )

        with mui.Card(key="minor_logs", variant="outlined", sx={"bgcolor": "#575769"}):
            mui.CardHeader(
                title=mui.Typography("Minor", sx={
                    "fontSize": "24px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#e6ac00'

                }),
                className="drag-handle"
            )
            mui.CardContent(
                mui.Typography(minor_count, sx={
                    "fontSize": "40px",
                    "fontWeight": "Bold",
                    "textAlign": 'center',
                    "color": '#e6ac00'

                })
            )

        # 10 latest logs
        with mui.Card(key='raw_logs', variant="outlined", className="drag-handle"):
            with mui.TableContainer(sx={"maxHeight": 330}):
                mui.Table(stickyHeader=True)(
                    mui.TableHead(
                        mui.TableRow(
                            *[mui.TableCell(col, sx={
                                "fontWeight": "bold",
                                "fontSize": "16px",
                                "backgroundColor": "#2D2D44",
                            }) for col in columns]
                        )
                    ),

                    mui.TableBody(
                        *[
                            mui.TableRow(
                                mui.TableCell(str(row[col]), sx={
                                    "backgroundColor": "#575769",
                                }) for col in columns
                            )
                            for row in top10_latest_logs_dict
                        ]
                    )
                )

        # Graph
        with mui.Card(key="logs_line_graph", variant="outlined", className="drag-handle", sx={"bgcolor": "#c6ccd8"}):
            mui.CardHeader(
                title=f"Logs Severity Distribution for {current_date}",
                sx={
                    "textAlign": 'left',
                    "color": '#1d1d1d'
                }
            )

            nivo.Line(
                data=current_date_hourly_logs_dataframe,
                theme=graph_theme,

                margin={"top": 10, "right": 100, "bottom": 180, "left": 90},
                xScale={"type": "point"},
                yScale={"type": "linear", "min": "auto", "max": "auto"},
                axisBottom={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "tickRotation": -45,
                    "legend": "Time",
                    "legendOffset": 100,
                    "legendPosition": "middle"
                },
                axisLeft={
                    "tickSize": 5,
                    "tickPadding": 5,
                    "legend": "Count",
                    "legendOffset": -50,
                    "legendPosition": "middle"
                },
                pointSize=5,
                pointBorderWidth=2,
                useMesh=True,
                legends=[
                    {
                        "anchor": "bottom-right",
                        "direction": "column",
                        "translateX": 100,
                        "itemWidth": 80,
                        "itemHeight": 20,
                        "symbolSize": 10,
                        "symbolShape": "circle"
                    }
                ],
                colors={"scheme": "set1"},

            )
