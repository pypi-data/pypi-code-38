"""
Some helpers to plot the networks with plotly (https://plot.ly)
"""

import plotly.graph_objs as go
import numpy as np
import igraph

def createSizeFromFunc(gr: igraph.Graph, func: str = "betweenness", min_size: float = 2, scale_size: float = 10) -> np.array:
    """
    Creates an numpy array with sizes for each vertex in the graph.

    :param gr: igraph.Graph object
    :param func: (optional) the name of a method of gr which calculates a numerical value for each vertex. Defaults to "betweenness".
    :param min_size: the minimal size of each vertex
    :param scale_size: maximal size of each vertex
    :return: np.array
    """

    betw = getattr(gr,func)()

    if max(betw) != 0:
        sizes = np.array(betw) / max(betw) * scale_size + min_size
    else:
        sizes = min_size
    return sizes


def createFigGraph(gr: igraph.Graph, title: str, hover_field: str = "label", sizes: object = 2, typ_field: str = None, pos: list = None) -> go.Figure:
    """
    create figure for plotly

    :param gr: graph to be plotted
    :param title: title of the plot
    :param sizes: can be an float or an array, defines size for each vertex
    :param hover_field: property of the node to be displayed (defaults to label)
    :param typ_field: if set the generate 3d perspective
    :param pos: array with x,y coodinates for each vertex. If none layout_fruchterman_reingold() is called.
    :return: figure which than can be used by plotly
    """

    if typ_field:
        typs = set(gr.vs[typ_field])
        Zn =gr.vs[typ_field]

    if not pos:
        pos = gr.layout_fruchterman_reingold()
    Xn = [k[0] for k in pos.coords]  # x-coordinates of nodes
    Yn = [k[1] for k in pos.coords]  # x-coordinates of nodes



    Xe = []
    Ye = []
    Ze = []
    for e in gr.es:
        Xe += [pos.coords[e.source][0], pos.coords[e.target][0], None]  # x-coordinates of edge ends
        Ye += [pos.coords[e.source][1], pos.coords[e.target][1], None]

        if typ_field:
            Ze += [Zn[e.source],Zn[e.target], None]

    #texts = ["%s-%s" % (e["year_s"], e["year_e"]) for e in gr.es]

    tr1_params = dict(x=Xe,
                        y=Ye,
                        mode='lines',
                        line=dict(color='rgb(10,20,20)', width=0.1),
                        #text=texts,
                        hoverinfo='text'
                        )




    if typ_field:
        scatter = go.Scatter3d
        tr1_params["z"] = Ze

    else:
        scatter = go.Scatter

    trace1 = scatter(**tr1_params)


    tr2_params = dict(x=Xn,
                        y=Yn,
                        mode='markers',
                        name='actors',
                        marker=dict(symbol='circle',
                                    size=sizes,
                                    # color=group,
                                    colorscale='Viridis',
                                    line=dict(color='rgb(240,240,240)', width=0.5)
                                    ),
                        text=gr.vs[hover_field],
                        hoverinfo='text'
                        )

    if typ_field:
        tr2_params["z"] = Zn



    trace2 = scatter(**tr2_params)

    axis = dict(showbackground=False,
                showline=False,
                zeroline=True,
                showgrid=True,
                showticklabels=True,
                title=''
                )

    layout = go.Layout(
        title="",
        width=1000,
        height=1000,
        showlegend=False,
        scene=dict(
            xaxis=dict(axis),
            yaxis=dict(axis),
            zaxis=dict(axis),
        ),
        margin=dict(
            t=100
        ),
        hovermode='closest',
        annotations=[
            dict(
                showarrow=False,
                text=title,
                xref='paper',
                yref='paper',
                x=0,
                y=0.1,
                xanchor='left',
                yanchor='bottom',
                font=dict(
                    size=14
                )
            )
        ], )

    data = [trace1, trace2]
    # data=[trace2]
    fig = go.Figure(data=data, layout=layout)

    return fig



