from dash_bootstrap_components._components.FormGroup import FormGroup
import os
import re
from decimal import Decimal
from typing import List, Dict, Optional, Any

from apiclient import discovery
import dash
from dash_table import DataTable, FormatTemplate
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

from .layout import create_pnl_chart, monthly_totals, set_layout, table_columns

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


def prepare_data(values: SheetData) -> pd.DataFrame:
    headers = [s.strip() for s in values[0]]
    rows = values[1:]
    df = pd.DataFrame(rows, columns=headers)
    df["DateTime"] = pd.to_datetime(df["Date"], format="%m/%d/%Y")
    df["Product"] = df["Product"].str.strip()
    df["Department"] = df["Department"].str.strip()
    df["Sales"] = df["Sales"].apply(to_decimal)
    df["COGS"] = df["COGS"].apply(to_decimal)
    df["Profit"] = df["Profit"].apply(to_decimal)
    df["Date"] = df["DateTime"].dt.date
    df = df.sort_values(by=["DateTime"])

    return df


raw_data = fetch_data()
df = prepare_data(raw_data)

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.MINTY],
    prevent_initial_callbacks=True,
    routes_pathname_prefix="/dashboard/",
)
app.title = "Insight Analytics"
set_layout(app, df)


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
    Output("bar-chart", "figure"),
    Input("department-filter", "value"),
    Input("product-filter", "value"),
)
def update_bar_chart(
    department: Optional[str], product: Optional[str]
) -> List[Dict[str, Any]]:
    dff = apply_filters(df, department, product)
    return create_pnl_chart(monthly_totals(dff))


@app.callback(
    Output("download", "data"),
    Input("download-button", "n_clicks"),
    State("department-filter", "value"),
    State("product-filter", "value"),
)
def handle_download(n_clicks: int, department: Optional[str], product: Optional[str]):
    dff = apply_filters(df, department, product)
    dff = dff[[c["id"] for c in table_columns]]
    filename = "-".join([s for s in ("Sales", department, product) if s])
    return send_data_frame(dff.to_csv, f"{filename}.csv")


server = app.server
if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
