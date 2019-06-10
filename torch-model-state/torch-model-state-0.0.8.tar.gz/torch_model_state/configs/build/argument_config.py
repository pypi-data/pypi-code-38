class ArgumentConfig:
    def __init__(self, values: dict = None):
        values = values if values is not None else {}
        self.state_file: str = values.get("state_file", None)
        self.load_model: bool = values.get("load_model", False)
        self.extra_import: str = values.get("extra_import", None)
        self.device: str = values.get("device", 'cpu')
        self.export_onnx: str = values.get("export_onnx", None)
        self.input_size: int = values.get("input_size", 224)
        self.verbose: bool = values.get("verbose", False)
