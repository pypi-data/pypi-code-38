from datalogue.models.transformations.commons import Transformation, DataType
from datalogue.utils import _parse_string_list, SerializableStringEnum
from datalogue.errors import _enum_parse_error, DtlError, _property_not_found, _invalid_property_type
from typing import List, Union


class Period:

    def __init__(self, identifier: str, value: int, unit: str):
        self.identifier = identifier
        self.value = value
        self.unit = unit

    def __eq__(self, other: 'Period'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Period(identifier: {self.identifier}, value: {self.value}, unit: {self.unit})"

    def _as_payload(self) -> dict:
        return {
            "identifier": self.identifier,
            "value": self.value,
            "unit": self.unit
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Period']:
        identifier = json.get("identifier")
        if identifier is None:
            return _property_not_found("identifier", json)

        value = json.get("value")
        if value is  None:
            return _property_not_found("value", json)

        unit = json.get("unit")
        if unit is  None:
            return _property_not_found("unit", json)

        return Period(identifier, value, unit)


class Format:

    def __init__(self, start: str, end: str, separator: str):
        self.start = start
        self.end = end
        self.separator = separator

    def __eq__(self, other: 'Format'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Format(start: {self.start}, end: {self.end}, separator: {self.separator})"

    def _as_payload(self) -> dict:
        return {
            "start": self.start,
            "separator": self.separator,
            "end": self.end
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Format']:
        start = json.get("start")
        if start is None:
            return _property_not_found("start", json)

        separator = json.get("separator")
        if separator is  None:
            return _property_not_found("separator", json)

        end = json.get("end")
        if end is  None:
            return _property_not_found("end", json)

        return Format(start, end, separator)


class Output:

    def __init__(self, start_label: str, end_label: str, format: str):
        self.start_label = start_label
        self.end_label = end_label
        self.format = format

    def __eq__(self, other: 'Output'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"Output(start: {self.start_label}, end: {self.end_label}, separator: {self.format})"

    def _as_payload(self) -> dict:
        return {
            "startLabel": self.start_label,
            "endLabel": self.end_label,
            "format": self.format
        }

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'Output']:
        start_label = json.get("startLabel")
        if start_label is None:
            return _property_not_found("startLabel", json)

        end_label = json.get("endLabel")
        if end_label is  None:
            return _property_not_found("endLabel", json)

        format = json.get("format")
        if format is  None:
            return _property_not_found("format", json)

        return Output(start_label, end_label, format)


class ParseDatesAndCreatePeriodNodes(Transformation):

    type_str = "ParseDatesAndCreatePeriodNodes"

    def __init__(self, path: List[str], period: Period, date_format: Format, output: Output):
        Transformation.__init__(self, ParseDatesAndCreatePeriodNodes.type_str)
        self.path = path
        self.period = period
        self.format = date_format
        self.output = output

    def __eq__(self, other: 'ParseDatesAndCreatePeriodNodes'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"ParseDatesAndCreatePeriodNodes(path: {self.path!r}, period: {self.period}, format: {self.format}, output: {self.output})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["period"] = self.period._as_payload()
        base["format"] = self.format._as_payload()
        base["output"] = self.output._as_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'ParseDatesAndCreatePeriodNodes']:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        period = json.get("period")
        if period is None:
            return _property_not_found("period", json)

        period = Period._from_payload(period)
        if isinstance(period, DtlError):
            return period

        date_format = json.get("format")
        if date_format is None:
            return _property_not_found("format", json)

        date_format = Format._from_payload(date_format)
        if isinstance(date_format, DtlError):
            return date_format

        output = json.get("output")
        if output is None:
            return _property_not_found("output", json)

        output = Output._from_payload(output)
        if isinstance(output, DtlError):
            return output

        return ParseDatesAndCreatePeriodNodes(path, period, date_format, output)


class InterpretAsDateAndCreatePeriodNodes(Transformation):

    type_str = "InterpretAsDateAndCreatePeriodNodes"

    def __init__(self, path: List[str], period: str, year: int, output: Output):
        Transformation.__init__(self, InterpretAsDateAndCreatePeriodNodes.type_str)
        self.path = path
        self.period = period
        self.year = year
        self.output = output

    def __eq__(self, other: 'InterpretAsDateAndCreatePeriodNodes'):
        if isinstance(self, other.__class__):
            return self._as_payload() == other._as_payload()
        return False

    def __repr__(self):
        return f"InterpretAsDateAndCreatePeriodNodes(path: {self.path!r}, period: {self.period}, year: {self.year}, output: {self.output})"

    def _as_payload(self) -> dict:
        base = self._base_payload()
        base["path"] = self.path
        base["period"] = self.period
        base["year"] = self.year
        base["output"] = self.output._as_payload()
        return base

    @staticmethod
    def _from_payload(json: dict) -> Union[DtlError, 'InterpretAsDateAndCreatePeriodNodes']:
        path = json.get("path")
        if path is None:
            return _property_not_found("path", json)

        path = _parse_string_list(path)
        if isinstance(path, DtlError):
            return path

        period = json.get("period")
        if period is None:
            return _property_not_found("period", json)

        year = json.get("year")
        if year is None:
            return _property_not_found("year", json)

        output = json.get("output")
        if output is None:
            return _property_not_found("output", json)

        output = Output._from_payload(output)
        if isinstance(output, DtlError):
            return output

        return InterpretAsDateAndCreatePeriodNodes(path, period, year, output)
