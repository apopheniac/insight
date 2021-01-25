from dash_bootstrap_components._components.FormGroup import FormGroup
import os
import re
from decimal import Decimal
from typing import List, Dict, Optional, Any

from apiclient import discovery
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

SheetData = List[List[str]]


def fetch_data() -> SheetData:
    service = discovery.build("sheets", "v4")
    # TODO: move spreadsheet parameters into config
    spreadsheet_id = "1d-OnGMQG8IlPIG2Ru2SmiH2n9klzMxivfb3mD3imRBE"
    range_name = "Financial Data"
    sheet = service.spreadsheets()
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])
    if not values:
        raise RuntimeError("No data found")

    return values


def to_decimal(s: str) -> Optional[Decimal]:
    pattern = re.compile(r"(?P<paren>\()?(?P<numeral>(\d+,?)+(\.(\d+))?)")
    if match := pattern.search(s):
        groups = match.groupdict()
        sign = -1 if groups["paren"] is not None else 1
        numeral = groups["numeral"].replace(",", "")
        return sign * Decimal(numeral)
    else:
        return None


def to_dataframe(values: SheetData) -> pd.DataFrame:
    headers = [s.strip() for s in values[0]]
    rows = values[1:]
    return pd.DataFrame(rows, columns=headers)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    frame = {
        "Date": pd.to_datetime(df["Date"], format="%m/%d/%Y"),
        "Department": df["Department"].str.strip(),
        "Product": df["Product"].str.strip(),
        "Sales": df["Sales"].apply(to_decimal),
        "COGS": df["COGS"].apply(to_decimal),
        "Profit": df["Profit"].apply(to_decimal),
    }
    return pd.DataFrame(frame)


def create_pnl_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=[
            go.Bar(name="Sales", x=df["Date"], y=df["Sales"]),
            go.Bar(name="COGS", x=df["Date"], y=df["COGS"]),
            go.Scatter(
                name="Profit",
                x=df["Date"],
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
        df[["Date", "Sales", "COGS", "Profit"]]
        .resample("1M", on="Date")
        .sum()
        .reset_index()
    )


df = clean(to_dataframe(fetch_data()))
fig = create_pnl_chart(monthly_totals(df))
departments = df["Department"].unique()
products = df["Product"].unique()


app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    prevent_initial_callbacks=True,
    routes_pathname_prefix="/dashboard/",
)
app.layout = dbc.Container(
    html.Div(
        [
            dbc.NavbarSimple(
                [
                    dbc.NavItem(
                        dbc.NavLink("Log out", href="/logout", external_link=True)
                    ),
                ],
                brand="Insight - Business Metrics",
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
                                        {"label": d, "value": d} for d in departments
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
                        dash_table.DataTable(
                            id="sales-table",
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict("records"),
                            fixed_rows={"headers": True, "data": 0},
                        )
                    )
                ]
            ),
        ]
    )
)


def apply_filters(
    df: pd.DataFrame, department: Optional[str], product: Optional[str]
) -> pd.DataFrame:
    mask = pd.Series(True, index=df.index)
    if department:
        mask = mask & (df["Department"] == department)
    if product:
        mask = mask & (df["Product"] == product)

    return df[mask]


@app.callback(
    Output("sales-table", "data"),
    Input("department-filter", "value"),
    Input("product-filter", "value"),
)
def update_table(
    department: Optional[str], product: Optional[str]
) -> List[Dict[str, Any]]:
    return apply_filters(df, department, product).to_dict("records")


@app.callback(
    Output("download", "data"),
    Input("download-button", "n_clicks"),
    State("department-filter", "value"),
    State("product-filter", "value"),
)
def handle_download(n_clicks: int, department: Optional[str], product: Optional[str]):
    dff = apply_filters(df, department, product)
    filename = "-".join([s for s in ("Sales", department, product) if s])
    return send_data_frame(dff.to_csv, f"{filename}.csv")


server = app.server
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
