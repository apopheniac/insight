import httplib2  # type: ignore
import os
import re
from decimal import Decimal
from typing import List, Optional

from apiclient import discovery  # type: ignore
import dash  # type: ignore
import dash_table  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
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
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
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
                        dcc.Dropdown(
                            id="department_filter",
                            options=[{"label": d, "value": d} for d in departments],
                            value="Department",
                        )
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),
                html.Div(
                    [
                        dcc.Dropdown(
                            id="product_filter",
                            options=[{"label": p, "value": p} for p in products],
                            value="Product",
                        )
                    ],
                    style={"width": "48%", "display": "inline-block", "float": "right"},
                ),
            ]
        ),
        dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            page_size=50,
            style_table={"height": "500px", "overflowY": "auto"},
        ),
    ]
)
server = app.server

if __name__ == "__main__":
    app.run_server(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))
