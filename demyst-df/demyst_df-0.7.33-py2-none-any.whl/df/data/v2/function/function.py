
from demyst.df.df2 import df2
import os

@df2
def data_function(df):
    inputs = df.connectors.get("pass_through", '', {})
    return {'inputs': inputs, 'env': str(os.environ), 'output_field_example': "Hello World"}
