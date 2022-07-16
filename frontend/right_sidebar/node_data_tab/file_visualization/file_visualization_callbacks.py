from datetime import datetime, timedelta
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
from dash.exceptions import PreventUpdate
import dash_core_components as dcc

from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

print("Initializing file visualization callbacks...")


@app.callback(
    Output("suppl_file_download", "data"),
    Input("suppl_file_download_button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def func(n_clicks, selected_el_json):

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    suppl_file = api_client.get_raw(
        relative_path="/supplementary_file",
        iri=selected_el.iri,
    )

    return dcc.send_bytes(suppl_file, "file.jpg")
