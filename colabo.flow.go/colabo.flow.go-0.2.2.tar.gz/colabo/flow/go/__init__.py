# NOTE: In general we should be carefull with importing additional modules in __init__.py because 
# they are imported any time any module or sub-module is required
# import `ColaboFlowGo` class from the local (notice: `.`) file `colaboflow_go`
from .colaboflow_go_client import ColaboFlowGo
from .colaboflow_go_actionhost import ColaboFlowGoActionHost
from .colaboflow_go_demo import ColaboFlowGoDemo

# provide the `ColaboFlowGo` class directly importable from the `go` namespace
__all__ = ['ColaboFlowGo', 'ColaboFlowGoActionHost', 'ColaboFlowGoDemo']
