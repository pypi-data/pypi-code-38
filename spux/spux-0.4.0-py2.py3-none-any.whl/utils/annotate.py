
import pandas, numpy

# annotate array with the given labels
def annotate (data, labels, time, auxiliary=None):
    """Annotate data array with the given labels (with an option for auxiliary information).

    Optional auxiliary object of any type can be provided and will be passed to the error model,
    but will not be stored in the corresponding 'info' as the model prediction, and hence will be node-local.
    In the error model, the 'prediction' will then be a dictionary of the form: {'scalars' : predictions, 'auxiliary' : auxiliary}.
    This is useful for large non-scalar model outputs, such as vectors or multi-dimensional arrays (e.g. xarray's).
    Any additional (i.e outside the error model) access of such auxiliary information is not supported.
    As such data is often very large, the recommended option is to keep the trace of all sandboxes and perform additional a posteriori post-processing."""

    if not isinstance (data, numpy.ndarray):
        data = numpy.array (data)
    shape = (1, len (labels))
    if data.shape != shape:
        data = data.reshape (shape)
    prediction = pandas.DataFrame (data, columns=labels, index=[time]) .iloc [0]
    if auxiliary is None:
        return prediction
    else:
        return { 'scalars' : prediction, 'auxiliary' : auxiliary }
