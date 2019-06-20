"""
Provides functionality for handling the request format for using in the
EHubModel.
"""
from collections import defaultdict
from typing import List, Optional, Dict, TypeVar, Iterable, Union

import pandas as pd
#import logging

from data_formats.request_format import (
    Capacity, Converter, Stream, Storage, TimeSeries, Network_links
)
from energy_hub.utils import cached_property

T = TypeVar('T')


class InputData:
    """Provides convenient access to needed data to implement an energy hub
    model."""

    def __init__(self, request: dict) -> None:
        """Create a new instance.

        Args:
            request: A dictionary in request format
        """
        self._request = request

    @cached_property
    def capacities(self) -> List[Capacity]:
        """The list of capacities."""
        return [Capacity(capacity) for capacity in self._request['capacities']]

    def _get_capacity(self, name: str) -> Optional[dict]:
        """Get the capacity in the request format with this name.

        Args:
            name: The name of the capacity

        Returns:
            Either the capacity in the request format or None
        """
        capacities = self._request['capacities']

        for capacity in capacities:
            if capacity['name'] == name:
                return capacity

        return None

    @cached_property
    def storages(self) -> List[Storage]:
        """The list of storages."""
        def _make(storage):
            capacity = self._get_capacity(storage['capacity'])

            return Storage(storage, capacity)

        return [_make(storage) for storage in self._request['storages']]

    @property
    def storage_names(self) -> List[str]:
        """Return the names of the storages."""
        return [storage.name for storage in self.storages]

    @cached_property
    def converters(self) -> List[Converter]:
        """The list of converters."""
        def _make(converter):
            capacity = self._get_capacity(converter['capacity'])

            return Converter(converter, capacity)

        return [_make(converter) for converter in self._request['converters']]

    @property
    def converter_names(self) -> List[str]:
        """Return the names of the converters."""
        return [converter.name for converter in self.converters]

    @cached_property
    def time_series_list(self) -> List[TimeSeries]:
        """The list of time series."""
        return [TimeSeries(time_series)
                for time_series in self._request['time_series']]

    @cached_property
    def streams(self) -> List[Stream]:
        """The list of streams."""
        return [Stream(stream, self._request)
                for stream in self._request['streams']]

    @cached_property
    def stream_names(self) -> List[str]:
        """Return the names of the streams."""
        return [stream.name for stream in self.streams]

    @cached_property
    def output_stream_names(self):
        """The sorted list of output streams names."""
        names = (output for tech in self.converters for output in tech.outputs)

        return sorted(set(names))

    @cached_property
    def demand_stream_names(self):
        """The sorted list of demand streams names."""
        names = (demand.stream for demand in self.demands)
        return sorted(set(names))

    @cached_property
    def import_streams(self) -> List[str]:
        """The names of streams that are importable."""
        return [stream.name for  stream in self.streams
                if stream.importable]

    @cached_property
    def export_streams(self) -> List[str]:
        """The names of streams that are exportable."""
        return [stream.name for  stream in self.streams
                if stream.exportable]

    @property
    def demands(self) -> Iterable[TimeSeries]:
        """Return the TimeSeries that are demands."""
        return (demand for demand in self.time_series_list
                if demand.is_demand)

    @property
    def source(self) -> Iterable[TimeSeries]:
        """Return the TimeSeries that are sources."""
        return (source for source in self.time_series_list
                if source.is_source)

    @cached_property
    def source_stream_names(self):
        """The sorted list of source streams names."""
        names = (source.stream for source in self.source)
        return sorted(set(names))

    @cached_property
    def time_series_data(self) -> Dict[str, Dict[int, float]]:
        """The data for the availability time series as a dictionary that is indexed
        by time."""
        return {
            time_series.name: {
                t: time_series.data[t] for t in self.time
            } for time_series in self.time_series_list
        }
        #return {t: solar.data[t] for t in self.time}

    # @property
    # def availabilities(self) -> Iterable[TimeSeries]:
    #     """Return the TimeSeries that are stream availability."""
    #     return (avail for avail in self.time_series_list
    #             if avail.is_source)

    @cached_property
    def time(self) -> List[int]:
        """Return the time steps of the model."""
        # Assume all time series have data for all time steps
        example_series = list(self.demands)[0]
        time = example_series.data.keys()

        return list(time)

    @property
    def loads(self) -> Dict[str, Dict[int, float]]:
        """The data for all demands as a dictionary that is indexed by (demand
        time series ID, time)."""
        return {
            demand.stream: {
                t: demand.data[t] for t in self.time
            } for demand in self.demands
        }

    # @cached_property
    # def roof_tech(self) -> List[str]:
    #     """The names of the converters that can be put on a roof."""
    #     return [tech.name for tech in self.converters if tech.is_roof_tech]

    @property
    def c_matrix(self) -> Dict[str, Dict[str, float]]:
        """Return a dictionary-format for the C matrix.

        The format is like {converter name: {stream name: ...}, ...}
        """
        c_matrix = pd.DataFrame(0, index=self.converter_names,
                                columns=self.stream_names, dtype=float)
        for tech in self.converters:
            efficiency = tech.efficiency

            for input_ in tech.inputs:
                if input_ not in self.source_stream_names:
                    c_matrix[input_][tech.name] = -1

            for output in tech.outputs:
                output_ratio = tech.output_ratios[output]
                c_matrix[output][tech.name] = efficiency * output_ratio

        return c_matrix.T.to_dict()

    @cached_property
    def part_load(self) -> Dict[str, Dict[str, float]]:
        """Return the part load for each tech and each of its outputs."""
        part_load = defaultdict(defaultdict)  # type: Dict[str, Dict[str, float]]
        for tech in self.converters:
            for output_stream in self.output_stream_names:
                if output_stream in tech.outputs:
                    min_load = tech.min_load
                    if min_load is not None:
                        part_load[tech.name][output_stream] = min_load

        return part_load

    @property
    def converters_capacity(self) -> Dict[str, float]:
        """Return the capacities of the converters."""
        return {tech.name: tech.capacity
                for tech in self.converters}

    @property
    def stream_timeseries(self) -> Dict[str, float]:
        """Return the streams that have an availability timeseries."""
        return {stream.name: stream.timeseries
                for stream in self.streams
                if stream.timeseries}

    @property
    def part_load_techs(self) -> List[str]:
        """The names of the converters that have a part load."""
        return [tech.name for tech in self.converters if tech.has_part_load]

    @cached_property
    def linear_cost(self) -> Dict[str, float]:
        """Return the linear cost for each tech."""
        return {converter.name: converter.capital_cost
                for converter in self.converters}

    @cached_property
    def fixed_capital_costs(self) -> Dict[str, float]:
        """Return the fixed capital cost for each converter."""
        return {converter.name: converter.fixed_capital_cost
                for converter in self.converters}

    @cached_property
    def interest_rate(self) -> float:
        """The interest rate."""
        return self._request['general']['interest_rate']

    def _calculate_npv(self, lifetime: float) -> float:
        """Calculate the net present value of an asset giving its lifetime.

        Args:
            lifetime: The lifetime of the asset

        Returns:
            The net present value of the asset
        """
        r = self.interest_rate

        return 1 / (
            ((1 + r)**lifetime - 1) / (r * (1 + r)**lifetime)
        )

    @cached_property
    def tech_npv(self) -> Dict[str, float]:
        """The net present value of each converter."""
        return {tech.name: round(self._calculate_npv(tech.lifetime), 4)
                for tech in self.converters}

    @cached_property
    def variable_maintenance_cost(self) -> Dict[str, float]:
        """The variable maintenance cost of each converter."""
        return {tech.name: tech.usage_maintenance_cost
                for tech in self.converters}

    @cached_property
    def carbon_factors(self) -> Dict[str, Union[float, str]]:
        """The carbon factor of each stream."""
        carbon_factors = {}
        for stream in self.streams:
            carbon_factors[stream.name] = stream.co2

        return carbon_factors

    @cached_property
    def carbon_credits(self) -> Dict[str, Union[float, str]]:
        """The carbon credit of each stream."""
        carbon_credits = {}
        for stream in self.streams:
            carbon_credits[stream.name] = stream.co2_credit

        return carbon_credits

    @cached_property
    def fuel_price(self) -> Dict[str, Union[float,str]]:
        """Return the price of each fuel."""
        return {stream.name: stream.price
                for stream in self.streams}

    @cached_property
    def feed_in(self) -> Dict[str,Union[float, str]]:
        """The export price of each output stream."""
        return {stream.name: stream.export_price
                for stream in self.streams
                if stream.exportable}
    @property
    def storage_capacity(self):
        """The capacity of each storage."""
        return self._get_from_storages('capacity')

    @cached_property
    def storage_charge(self) -> Dict[str, float]:
        """The maximum charge of each storage."""
        return self._get_from_storages('max_charge')

    @cached_property
    def storage_discharge(self) -> Dict[str, float]:
        """The maximum discharge of each storage."""
        return self._get_from_storages('max_discharge')

    @cached_property
    def storage_loss(self) -> Dict[str, float]:
        """The decay of each storage."""
        return self._get_from_storages('decay')

    @cached_property
    def storage_ef_ch(self) -> Dict[str, float]:
        """The charging efficiency of each storage."""
        return self._get_from_storages('charge_efficiency')

    @cached_property
    def storage_ef_disch(self) -> Dict[str, float]:
        """The discharging efficiency of each storage."""
        return self._get_from_storages('discharge_efficiency')

    @cached_property
    def storage_min_soc(self) -> Dict[str, float]:
        """The minimum state of charge of each storage."""
        return self._get_from_storages('min_state')

    @cached_property
    def storage_lin_cost(self) -> Dict[str, float]:
        """The linear cost of each storage."""
        return self._get_from_storages('cost')

    @cached_property
    def storage_annual_maintenance_cost(self)->Dict[str,float]:
        """Returns annual maintenance cost of each storage"""
        return self._get_from_storages('annual_maintenance_cost')

    @cached_property
    def storage_fixed_capital_cost(self)-> Dict[str,float]:
        """Returns fixed capital cost of each storage"""
        return self._get_from_storages('fixed_capital_cost')

    def _get_from_storages(self, attribute: str) -> Dict[str, T]:
        """Return the attribute of each storage as a dictionary."""
        return {storage.name: getattr(storage, attribute)
                for storage in self.storages}

    @cached_property
    def storage_npv(self) -> Dict[str, float]:
        """The net present value of each storage."""
        return {storage.name: self._calculate_npv(storage.lifetime)
                for storage in self.storages}

    @property
    def links(self) -> List[Network_links]:
        def _make(link):
            capacity = self._get_capacity(link['capacity'])

            return Network_links(link, capacity)

        return [_make(link) for link in self._request['links']]

    @cached_property
    def links_ids(self)->List[int]:
        """Returns a list of id of all the links"""
        return [link.link_id for link in self.links]

    def _get_from_links(self, attribute: str) -> Dict[int,T]:
        return {link.link_id: getattr(link, attribute)
                for link in self.links}

    @cached_property
    def link_length(self) ->  Dict[int, float]:
        """Returns the length of each link"""
        return self._get_from_links('length')

    @cached_property
    def link_capacity(self) -> Dict[int, float]:
        """Return the capacities of the converters."""
        return {link.link_id: link.link_capacity
                for link in self.links}

    @cached_property
    def link_start(self) -> Dict[int, int]:
        """Return the id of the start node"""
        return self._get_from_links('start_id')

    @cached_property
    def link_end(self)->Dict[int,int]:
        """Return the id of the end node"""
        return self._get_from_links('end_id')


    @cached_property
    def link_thermal_loss(self) -> [int, float]:
        """Return the thermal loss of each link"""
        return self._get_from_links('total_thermal_loss')


    @cached_property
    def fixed_network_investment_cost(self)->float:
        return self._request['network']['fixed_network_investment_cost']

    @cached_property
    def link_proportional_cost(self) -> float:
        return self._request['network']['link_proportional_cost']
