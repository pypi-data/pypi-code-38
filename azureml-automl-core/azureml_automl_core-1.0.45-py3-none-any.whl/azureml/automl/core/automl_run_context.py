# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context manager that wraps an AutoML run context."""
from typing import Any, cast, Optional, Callable, Dict
from abc import ABC, abstractmethod
from contextlib import contextmanager
import os
import pickle
import tempfile
import json

from .onnx_convert import OnnxConverter


class AutoMLAbstractRunContext(ABC):
    """Wrapper class for an AutoML run context."""

    def __init__(self):
        """Initialize the run context wrapper."""
        self._run_id = None     # type: Optional[str]

    @abstractmethod
    def _get_run_internal(self):
        """Retrieve the run context. Must be overridden by subclasses."""
        raise NotImplementedError

    @property
    def run_id(self) -> str:
        """
        Get the run id associated with the run wrapped by this run context. The run id is assumed to be immutable.

        :return: the run id
        """
        if self._run_id is None:
            with self.get_run() as run:
                self._run_id = run.id
        return cast(str, self._run_id)

    @contextmanager
    def get_run(self):
        """
        Yield a run context.

        Wrapped by contextlib to convert it to a context manager. Nested invocations will return the same run context.
        """
        yield self._get_run_internal()

    def save_model_output(self, fitted_pipeline: Any, remote_path: str) -> None:
        """
        Save the given fitted model to the given path using this run context.

        :param fitted_pipeline: the fitted model to save
        :param remote_path: the path to save to
        """
        self._save_model(fitted_pipeline, remote_path, self._save_python_model)

    def save_onnx_model_output(self, onnx_model: object, remote_path: str) -> None:
        """
        Save the given onnx model to the given remote path using this run context.

        :param onnx_model: the onnx model to save
        :param remote_path: the path to save to
        """
        self._save_model(onnx_model, remote_path, self._save_onnx_model)

    def save_onnx_model_resource(self, onnx_resource: Dict[Any, Any], remote_path: str) -> None:
        """
        Save the given onnx model resource to the given remote path using this run context.

        :param onnx_resource: the onnx model resource dict to save
        :param remote_path: the path to save to
        """
        self._save_file(onnx_resource, remote_path, binary_mode=False,
                        serialization_method=self._save_dict_to_json_output)

    def _save_model(self, model_object: Any, remote_path: str,
                    serialization_method: "Callable[..., Optional[Any]]") -> None:
        self._save_file(model_object, remote_path, binary_mode=True, serialization_method=serialization_method)

    def _save_file(self, save_object: Any, remote_path: str, binary_mode: bool,
                   serialization_method: "Callable[..., Optional[Any]]") -> None:
        output = None
        if binary_mode:
            write_mode = "wb+"
            read_mode = "rb"
        else:
            write_mode = "w+"
            read_mode = "r"
        try:
            output = tempfile.NamedTemporaryFile(mode=write_mode, delete=False)
            serialization_method(save_object, output)
            with(open(output.name, read_mode)):
                with self.get_run() as run_object:
                    run_object.upload_file(remote_path, output.name)
        finally:
            if output is not None:
                output.close()
                os.unlink(output.name)

    def _save_onnx_model(self, model_object: Any, model_output: Any) -> None:
        OnnxConverter.save_onnx_model(model_object, model_output.name)

    def _save_python_model(self, model_object: Any, model_output: Any) -> None:
        with(open(model_output.name, 'wb')):
            pickle.dump(model_object, model_output)
            model_output.flush()

    def _save_str_output(self, str_object: Any, output: Any) -> None:
        with open(output.name, "w") as f:
            f.write(str_object)

    def _save_dict_to_json_output(self, dict_object: Dict[Any, Any], output: Any) -> None:
        with open(output.name, 'w') as f:
            json.dump(dict_object, f)

    def save_str_output(self, input_str: str, remote_path: str) -> None:
        """
        Save the str file as a txt into the Artifacts.

        :param input_str: the input string.
        :paran remote_path: the file name in the Artifacts.
        """
        self._save_file(input_str, remote_path, binary_mode=False, serialization_method=self._save_str_output)
