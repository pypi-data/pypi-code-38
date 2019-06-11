import shlex
import subprocess as sp
import tempfile

from tree_html.utils import run


def filter_tree_depth(level, tree):
    def traverse(nest, local_level=999):
        if isinstance(nest, dict):
            if nest.get("contents"):
                if local_level < 1:
                    nest["contents"] = []
                    return nest
                else:
                    local_level -= 1
                    nest = traverse(nest.get("contents"), local_level)
        elif isinstance(nest, list):
            for node in nest:
                traverse(node, local_level)
        return nest

    tree = traverse(tree, local_level=level)
    return tree


def generate_json_tree(target_dir, level):
    """Runs tree in a subprocess and captures the output in JSON format"""
    cmd = f"tree -J {target_dir}"

    if level:
        cmd += f" -L {level}"

    cmd = shlex.split(cmd)

    try:
        result = run(cmd)
    except sp.CalledProcessError:
        print(
            "Failed to execute tree - make sure that 'tree' is available "
            "in your PATH and that the TARGET_DIR exists"
        )
    else:
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(result)
        temp.close()
        return temp.name
