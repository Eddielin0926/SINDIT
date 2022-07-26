import base64
import plotly.graph_objects as go
from dash import dcc

from frontend import api_client


def get_visualization(selected_el):
    # Get image
    suppl_file_data = api_client.get_raw(
        relative_path="/supplementary_file/data",
        iri=selected_el.iri,
    )

    # Create figure
    fig = go.Figure()

    # Constants
    img_width = 700
    img_height = 700
    scale_factor = 0.5

    # Add invisible scatter trace.
    # This trace is added to help the autoresize logic work.
    fig.add_trace(
        go.Scatter(
            x=[0, img_width * scale_factor],
            y=[0, img_height * scale_factor],
            mode="markers",
            marker_opacity=0,
        )
    )

    # Configure axes
    fig.update_xaxes(visible=False, range=[0, img_width * scale_factor])

    fig.update_yaxes(
        visible=False,
        range=[0, img_height * scale_factor],
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x",
    )

    base64image = base64.b64encode(suppl_file_data).decode("utf-8")

    # Add image
    fig.add_layout_image(
        dict(
            x=0,
            sizex=img_width * scale_factor,
            y=img_height * scale_factor,
            sizey=img_height * scale_factor,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            source=f"data:image/jpg;base64,{base64image}",
        )
    )

    # Configure other layout
    fig.update_layout(
        width=img_width * scale_factor,
        height=img_height * scale_factor,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    return dcc.Graph(
        figure=fig,
        style={"width": "100%", "height": "100%", "min-height": "500px"},
    )
