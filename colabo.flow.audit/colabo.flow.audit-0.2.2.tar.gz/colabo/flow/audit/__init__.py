# NOTE: In general we should be carefull with importing additional modules in __init__.py because 
# they are imported any time any module or sub-module is required
# import `ColaboFlowAudit` class from the local (notice: `.`) file `colaboflow_audit_client`
from .colaboflow_audit_client import ColaboFlowAudit

# provide the `ColaboFlowAudit` class directly importable from the `audit` namespace
__all__ = ['ColaboFlowAudit']
