import httplib2  # type: ignore
import os
from typing import List

from apiclient import discovery  # type: ignore
import dash  # type: ignore
import dash_table  # type: ignore
import dash_core_components as dcc  # type: ignore
import dash_html_components as html  # type: ignore
import pandas as pd  # type: ignore
import plotly.express as px  # type: ignore
from dotenv import load_dotenv  # type: ignore

load_dotenv()


service = discovery.build("sheets", "v4")
spreadsheet_id = "1d-OnGMQG8IlPIG2Ru2SmiH2n9klzMxivfb3mD3imRBE"
range_name = "Financial Data"

sheet = service.spreadsheets()  # pylint: disable=no-member
result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
values: List[List[str]] = result.get("values", [])

if not values:
    raise RuntimeError("No data found")

column_names = values[0]
data = [{column_names[i]: row[i] for i in range(len(row))} for row in values[1:]]
columns = [{"name": c, "id": c} for c in column_names]

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

app.layout = html.Div(
    children=[
        html.H1(children="Hello Dash"),
        dash_table.DataTable(
            id="table",
            columns=columns,
            data=data,
            page_size=50,
            style_table={"height": "500px", "overflowY": "auto"},
        ),
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)
