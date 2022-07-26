import io
import plotly.graph_objects as go
from stl import mesh  # pip install numpy-stl
import plotly.graph_objects as go
import numpy as np

from dash import dcc
from frontend import api_client
from graph_domain.SupplementaryFileNode import (
    SupplementaryFileNodeDeep,
    SupplementaryFileNodeFlat,
    SupplementaryFileTypes,
)
from service.exceptions.GraphNotConformantToMetamodelError import (
    GraphNotConformantToMetamodelError,
)


def stl2mesh3d(stl_mesh):
    # stl_mesh is read by nympy-stl from a stl file; it is  an array of faces/triangles (i.e. three 3d points)
    # this function extracts the unique vertices and the lists I, J, K to define a Plotly mesh3d
    p, q, r = stl_mesh.vectors.shape  # (p, 3, 3)
    # the array stl_mesh.vectors.reshape(p*q, r) can contain multiple copies of the same vertex;
    # extract unique vertices from all mesh triangles
    vertices, ixr = np.unique(
        stl_mesh.vectors.reshape(p * q, r), return_inverse=True, axis=0
    )
    I = np.take(ixr, [3 * k for k in range(p)])
    J = np.take(ixr, [3 * k + 1 for k in range(p)])
    K = np.take(ixr, [3 * k + 2 for k in range(p)])
    return vertices, I, J, K


def get_visualization(selected_el, is_stl_format: bool):

    if is_stl_format:
        stl_iri = selected_el.iri
    else:
        # Alternative format required!
        available_formats_dicts = api_client.get_json(
            relative_path="/supplementary_file/alternative_formats", iri=selected_el.iri
        )

        available_formats = [
            SupplementaryFileNodeFlat.from_dict(m) for m in available_formats_dicts
        ]

        stl_iris = [
            file.iri
            for file in available_formats
            if file.file_type == SupplementaryFileTypes.CAD_STL.value
        ]
        if len(stl_iris) == 0:
            raise GraphNotConformantToMetamodelError(
                "No STL format available to be displayed for the selected CAD file"
            )

        stl_iri = stl_iris[0]

    cad_data = api_client.get_raw(relative_path="/supplementary_file/data", iri=stl_iri)

    cad_file_handle = io.BytesIO(cad_data)

    cad_mesh = mesh.Mesh.from_file(
        filename="cad", fh=cad_file_handle  # Filename not used
    )

    cad_mesh.vectors.shape

    vertices, I, J, K = stl2mesh3d(cad_mesh)
    x, y, z = vertices.T

    vertices.shape

    colorscale = [[0, "#e5dee5"], [1, "#e5dee5"]]

    mesh3D = go.Mesh3d(
        x=x,
        y=y,
        z=z,
        i=I,
        j=J,
        k=K,
        flatshading=True,
        colorscale=colorscale,
        intensity=z,
        name="AT&T",
        showscale=False,
    )

    layout = go.Layout(
        paper_bgcolor="rgb(1,1,1)",
        font_color="white",
        scene_camera=dict(eye=dict(x=1.25, y=-1.25, z=1)),
        scene_xaxis_visible=False,
        scene_yaxis_visible=False,
        scene_zaxis_visible=False,
    )

    fig = go.Figure(data=[mesh3D], layout=layout)

    fig.data[0].update(
        lighting=dict(
            ambient=0.18,
            diffuse=1,
            fresnel=0.1,
            specular=1,
            roughness=0.1,
            facenormalsepsilon=0,
        )
    )
    fig.data[0].update(lightposition=dict(x=3000, y=3000, z=10000))

    return dcc.Graph(figure=fig)
