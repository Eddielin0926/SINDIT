import base64
from datetime import datetime, timedelta
import io
from dash import html
from dash.dependencies import Input, Output, State
import pandas as pd
from dateutil import tz
import plotly.graph_objects as go
from stl import mesh  # pip install numpy-stl
import plotly.graph_objects as go
import numpy as np

import cadquery
import cqkit

# import OCC
# from OCC.STEPControl import STEPControl_Reader
# from OCC.IFSelect import IFSelect_RetDone, IFSelect_ItemsByEntity
# from OCC.Visualization import Tesselator, atNormal

# from cadquery import exporters
# import dash_vtk

# import cadquery as cq
from dash.exceptions import PreventUpdate
from dash import dcc
from frontend import api_client
from frontend.app import app
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.timeseries_graph import (
    timeseries_graph_layout,
)
from frontend.right_sidebar.node_data_tab.file_visualization.visualizer_implementations import (
    pdf_visualizer,
    jpg_visualizer,
    cad_visualizer,
)
from graph_domain.SupplementaryFileNode import (
    SupplementaryFileNodeFlat,
    SupplementaryFileTypes,
)
from graph_domain.factory_graph_types import NodeTypes
from util.environment_and_configuration import (
    ConfigGroups,
    get_configuration,
    get_configuration_float,
)

print("Initializing file visualization callbacks...")


@app.callback(
    Output("suppl_file_notifier", "children"),
    Output("suppl_file_notifier", "is_open"),
    Input("suppl_file_download_button", "n_clicks"),
    prevent_initial_call=False,
)
def delay_notifier(n_clicks):

    if n_clicks is None:
        # Just loading the visualization. Download button not pressed
        return (
            f"Visualization loading. This can take a while for file types like CAD.",
            True,
        )
    else:
        return (
            f"Download triggered. This can take a while.",
            True,
        )


@app.callback(
    Output("suppl_file_download", "data"),
    Input("suppl_file_download_button", "n_clicks"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, selected_el_json):

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    suppl_file_data = api_client.get_raw(
        relative_path="/supplementary_file/data",
        iri=selected_el.iri,
    )

    suppl_file_details_dict = api_client.get_json(
        relative_path="/supplementary_file/details",
        iri=selected_el.iri,
    )
    suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
        suppl_file_details_dict
    )

    return dcc.send_bytes(src=suppl_file_data, filename=suppl_file_details.file_name)


@app.callback(
    Output("suppl_file_visualization_container", "children"),
    Input("suppl_file_visualization_container", "children"),
    State("selected-graph-element-store", "data"),
    prevent_initial_call=False,
)
def visualize_file(_, selected_el_json):
    """Called only whenenver the container is being loaded to the screen

    Args:
        _ (_type_): _description_
        selected_el_json (_type_): _description_

    Raises:
        PreventUpdate: _description_
        PreventUpdate: _description_

    Returns:
        _type_: _description_
    """

    # Cancel if nothing selected
    if selected_el_json is None:
        raise PreventUpdate()

    selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

    # Cancel if anything else than a file is selected
    if selected_el.type != NodeTypes.SUPPLEMENTARY_FILE.value:
        print("Trying to download file for non-file element...")
        raise PreventUpdate()

    # Get type of file
    suppl_file_details_dict = api_client.get_json(
        relative_path="/supplementary_file/details",
        iri=selected_el.iri,
    )
    suppl_file_details: SupplementaryFileNodeFlat = SupplementaryFileNodeFlat.from_dict(
        suppl_file_details_dict
    )

    if suppl_file_details.file_type == SupplementaryFileTypes.IMAGE_JPG.value:
        return jpg_visualizer.get_visualization(selected_el)

    elif suppl_file_details.file_type == SupplementaryFileTypes.CAD_STEP.value:
        return cad_visualizer.get_visualization(selected_el, False)

    elif suppl_file_details.file_type == SupplementaryFileTypes.CAD_STL.value:
        return cad_visualizer.get_visualization(selected_el, True)

    elif suppl_file_details.file_type == SupplementaryFileTypes.DOCUMENT_PDF.value:
        return pdf_visualizer.get_visualization(selected_el)

    else:
        return html.Div("This type of file can not be visualized (yet).")
