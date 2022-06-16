from dash.dependencies import Input, Output, State
import pandas as pd

from frontend import api_client
from config import global_config as cfg
from frontend.app import app
from frontend.main_column.factory_graph import graph_selector_util
from frontend.main_column.factory_graph.GraphSelectedElement import GraphSelectedElement
from frontend.right_sidebar.node_data_tab.live_sensor_readings import sensor_readings_layout

sensor_ID = None

LIVE_SENSOR_DISPLAY_DURATION = cfg.get_float(
                group=cfg.ConfigGroups.FRONTEND,
                key='current_timeseries_duration')

print("Initializing sensor callbacks...")


@app.callback(Output('live-update-timeseries', 'figure'),
              Input('interval-component', 'n_intervals'),
              State('selected-graph-element-store', 'data'))
def update_live_sensors(n, selected_el_json):
    data = pd.DataFrame(columns=['time', 'value'])

    if selected_el_json is not None:
        selected_el: GraphSelectedElement = GraphSelectedElement.from_json(selected_el_json)

        if selected_el.type == graph_selector_util.SelectedElementTypes.TIMESERIES_INPUT:
            data = api_client.get_dataframe(f"/timeseries/current_measurements"
                                            f"?id_uri={selected_el.iri}"
                                            f"&duration={LIVE_SENSOR_DISPLAY_DURATION}")

        else:
            print("Trying to visualize timeseries from non-timeseries element...")

    fig = sensor_readings_layout.get_figure()
    fig.add_trace({
        'x': data['time'],
        'y': data['value'],
        'mode': 'lines+markers',
        'type': 'scatter'
    }, 1, 1)

    return fig
