# Jupyter Extension points
def _jupyter_nbextension_paths():
   return [dict(
      section="notebook",
      # the path is relative to the root directory
      src="",
      # directory in the `nbextension/` namespace
      dest="rsp_jupyter",
      # _also_ in the `nbextension/` namespace
      require="rsp_jupyter/index")]


