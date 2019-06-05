from graphviz import Source

def generate_graph():
    dot = """
        digraph Tree {
            edge [fontname="FangSong"];
            node [shape=box];
            0 [label="test"];
        }
    """

    graph = Source(dot)
    graph.format = 'png'
    graph.view('image', cleanup = True)
