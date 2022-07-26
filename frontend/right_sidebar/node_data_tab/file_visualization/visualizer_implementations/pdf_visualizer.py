import base64
from dash import html

from frontend import api_client


def get_visualization(selected_el):
    # Get pdf
    suppl_file_data = api_client.get_raw(
        relative_path="/supplementary_file/data",
        iri=selected_el.iri,
    )

    base64pdf = base64.b64encode(suppl_file_data).decode("utf-8")

    return html.ObjectEl(
        data="data:application/pdf;base64," + base64pdf,
        type="application/pdf",
        style={"width": "100%", "height": "100%", "min-height": "500px"},
    )
