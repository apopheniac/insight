import dash
from dash_table import DataTable, FormatTemplate
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash_extensions import Download
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict

money = FormatTemplate.money(2)
table_columns: List[Dict[str, str]] = [
    {"id": "Date", "name": "Date"},
    {"id": "Department", "name": "Department"},
    {"id": "Product", "name": "Product"},
    {"id": "Sales", "name": "Sales", "type": "numeric", "format": money},
    {"id": "COGS", "name": "COGS", "type": "numeric", "format": money},
    {"id": "Profit", "name": "Profit", "type": "numeric", "format": money},
]


def create_pnl_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(name="Sales", x=df["DateTime"], y=df["Sales"]),
            go.Bar(name="COGS", x=df["DateTime"], y=df["COGS"]),
            go.Scatter(
                name="Profit",
                x=df["DateTime"],
                y=df["Profit"],
                line=dict(color="darkslategrey", width=1.5),
                marker=dict(size=5),
                mode="lines+markers",
            ),
        ]
    )
    fig.update_layout(
        dict(
            title="P&L Trend",
            colorway=px.colors.qualitative.Set2,
        )
    )
    return fig


def monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df[["DateTime", "Sales", "COGS", "Profit"]]
        .resample("1M", on="DateTime")
        .sum()
        .reset_index()
    )


def set_layout(
    app: dash.Dash,
    df: pd.DataFrame,
) -> None:
    departments = df["Department"].unique()
    products = df["Product"].unique()
    fig = create_pnl_chart(monthly_totals(df))

    app.layout = dbc.Container(
        html.Div(
            [
                dbc.NavbarSimple(
                    [
                        dbc.NavItem(
                            dbc.NavLink("Log out", href="/logout", external_link=True)
                        ),
                    ],
                    brand="Insight | Business Analytics",
                    brand_href="#",
                    color="primary",
                    dark=True,
                ),
                dbc.Row(
                    dbc.Col(
                        html.Div(
                            [
                                dcc.Graph(id="bar-chart", figure=fig),
                            ]
                        )
                    )
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.FormGroup(
                                [
                                    dcc.Dropdown(
                                        id="department-filter",
                                        options=[
                                            {"label": d, "value": d}
                                            for d in departments
                                        ],
                                        placeholder="Filter by department",
                                    ),
                                ],
                            )
                        ),
                        dbc.Col(
                            dbc.FormGroup(
                                [
                                    dcc.Dropdown(
                                        id="product-filter",
                                        options=[
                                            {"label": p, "value": p} for p in products
                                        ],
                                        placeholder="Filter by product",
                                    ),
                                ],
                            )
                        ),
                        dbc.Col(
                            [
                                dbc.Button("Export", id="download-button"),
                                Download(id="download"),
                            ]
                        ),
                    ],
                ),
                dbc.Row(
                    [
                        dbc.Col(
                            DataTable(
                                id="sales-table",
                                columns=table_columns,
                                data=df.to_dict("records"),
                                page_size=20,
                                style_cell_conditional=[
                                    {
                                        "if": {"column_id": c},
                                        "textAlign": "left",
                                    }
                                    for c in ["Date", "Department", "Product"]
                                ],
                                style_as_list_view=True,
                            )
                        )
                    ]
                ),
            ]
        )
    )