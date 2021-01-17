import httplib2  # type: ignore
import os
import re
from decimal import Decimal
from typing import List, Dict, Optional, Any

from apiclient import discovery  # type: ignore
import dash  # type: ignore
import dash_table  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
from dash.dependencies import Input, Output, State  # type: ignore
from dash_extensions import Download  # type: ignore
from dash_extensions.snippets import send_data_frame  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()

SheetData = List[List[str]]


def fetch_data() -> SheetData:
    service = discovery.build("sheets", "v4")
    # TODO: move spreadsheet parameters into config
    spreadsheet_id = "1d-OnGMQG8IlPIG2Ru2SmiH2n9klzMxivfb3mD3imRBE"
    range_name = "Financial Data"
    sheet = service.spreadsheets()  # pylint: disable=no-member
    result = (
        sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
    )
    values = result.get("values", [])
    if not values:
        raise RuntimeError("No data found")

    return values


def to_decimal(s: str) -> Optional[Decimal]:  # pylint: disable=unsubscriptable-object
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
        "Date": pd.to_datetime(df["Date"], format="%m/%d/%Y").dt.date,
        "Department": df["Department"].str.strip(),
        "Product": df["Product"].str.strip(),
        "Sales": df["Sales"].apply(to_decimal),
        "COGS": df["COGS"].apply(to_decimal),
        "Profit": df["Profit"].apply(to_decimal),
    }
    return pd.DataFrame(frame)


df = clean(to_dataframe(fetch_data()))
departments = df["Department"].unique()
products = df["Product"].unique()

fig = px.bar(df, x="Date", y="Sales", color="Product")

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(
    __name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True
)
app.layout = html.Div(
    [
        html.H1(children="Hello Dash"),
        html.Div(
            [
                dcc.Graph(id="bar-chart", figure=fig),
            ]
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(
                            id="department-filter",
                            options=[{"label": d, "value": d} for d in departments],
                        ),
                        html.Div(
                            [
                                html.Button("Download", id="download-button"),
                                Download(id="download"),
                            ]
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="product-filter",
                            options=[{"label": p, "value": p} for p in products],
                        )
                    ],
                    style={"width": "48%", "display": "inline-block", "float": "right"},
                ),
            ]
        ),
        dash_table.DataTable(
            id="sales-table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            fixed_rows={"headers": True, "data": 0},
        ),
    ]
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
