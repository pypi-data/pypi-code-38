# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Location closest selector class."""

from ..aggregators.aggregator import Aggregator
from ..accessories.customer_data import CustomerData
from .enricher_selector import EnricherLocationSelector
from ..granularities.granularity import LocationClosestGranularity
from ..accessories.location_data import LocationData
from .._utils.random_utils import random_tag

import copy
import math

from ..environ import SparkEnv, PandasEnv
from multimethods import multimethod
from pyspark.sql.functions import rank, udf, col, dense_rank
from pyspark.sql.types import BooleanType, DoubleType
from pyspark.sql.window import Window


class LocationClosestSelector (EnricherLocationSelector):
    """Join the customer_data with public_data on closest spherical distance."""

    def __init__(self, _granularity: LocationClosestGranularity):
        """Initialize with location granularity."""
        self.granularity = _granularity

        self.location_id = 'location_id' + random_tag()
        self.location_lat = 'location_lat' + random_tag()
        self.location_long = 'location_long' + random_tag()
        self.rank1 = 'rank1' + random_tag()
        self.public_rankgroup = 'public_rankgroup' + random_tag()
        self.customer_rankgroup = 'customer_rankgroup' + random_tag()
        self.distance_name = 'distance_name' + random_tag()

    @multimethod(SparkEnv, LocationData)
    def _find_lat_long_boundary(self, env, customer_data):
        """
        Find the max/min latitude/longitude of the input customer data.

        :param customer_data: an instance of LocationData class
        :return: max longtitude, min longitude, max latiduce, min latitude
        """
        # if normal latlong, just find min max
        customer_dataset = customer_data.data
        maxLong = float((customer_dataset.agg({customer_data.longitude_column_name: "max"}).collect())[0][0])
        minLong = float((customer_dataset.agg({customer_data.longitude_column_name: "min"}).collect())[0][0])
        maxLat = float((customer_dataset.agg({customer_data.latitude_column_name: "max"}).collect())[0][0])
        minLat = float((customer_dataset.agg({customer_data.latitude_column_name: "min"}).collect())[0][0])
        return maxLong, minLong, maxLat, minLat

    @multimethod(PandasEnv, LocationData)
    def _find_lat_long_boundary(self, env, customer_data):
        """
        Find the max/min latitude/longitude of the input customer data.

        :param env: PandasEnv instance
        :param customer_data: an instance of LocationData class
        :return: max longtitude, min longitude, max latiduce, min latitude
        """
        # if normal latlong, just find min max
        customer_dataset = customer_data.data
        maxLong = customer_dataset[customer_data.longitude_column_name].max()
        minLong = customer_dataset[customer_data.longitude_column_name].min()
        maxLat = customer_dataset[customer_data.latitude_column_name].max()
        minLat = customer_dataset[customer_data.latitude_column_name].min()
        return maxLong, minLong, maxLat, minLat

    @multimethod(SparkEnv, LocationData, LocationData, int)
    def _get_public_data_filtered_locations(self, env, customer_data, public_data, cord_count):
        """
        Given inpt customer data, find the latitude/longitude boundary.

        It will filter the public data within the boundary +/- some degrees.
        """
        public_dataset = public_data.data
        maxLong, minLong, maxLat, minLat = self._find_lat_long_boundary(env, customer_data)

        # get all unique public_data_filtered_location from 3p dataset
        public_data_filtered_location = public_dataset.select(
            public_dataset[public_data.id].alias(self.location_id),
            public_dataset[public_data.latitude_column_name].alias(self.location_lat),
            public_dataset[public_data.longitude_column_name].alias(self.location_long)).dropDuplicates()

        fuzzy_boundary = self.granularity.lower_fuzzy_boundary \
            if cord_count > self.granularity.cord_limit \
            else self.granularity.upper_fuzzy_boundary
        public_data_filtered_location = public_data_filtered_location. \
            filter(public_data_filtered_location[self.location_long] < maxLong + fuzzy_boundary). \
            filter(public_data_filtered_location[self.location_long] > minLong - fuzzy_boundary). \
            filter(public_data_filtered_location[self.location_lat] < maxLat + fuzzy_boundary). \
            filter(public_data_filtered_location[self.location_lat] > minLat - fuzzy_boundary)

        return public_data_filtered_location

    @multimethod(PandasEnv, LocationData, LocationData, int)
    def _get_public_data_filtered_locations(self, env, customer_data, public_data, cord_count):
        """
        Given inpt customer data, find the latitude/longitude boundary.

        It will filter the public data within the boundary +/- some degrees.
        """
        public_dataset = public_data.data
        maxLong, minLong, maxLat, minLat = self._find_lat_long_boundary(env, customer_data)

        # get all unique public_data_filtered_location from 3p dataset
        public_data_filtered_location = public_dataset[[
            public_data.id,
            public_data.latitude_column_name,
            public_data.longitude_column_name]].rename(
                index=str,
                columns={
                    public_data.id: self.location_id,
                    public_data.latitude_column_name: self.location_lat,
                    public_data.longitude_column_name: self.location_long}).drop_duplicates()

        fuzzy_boundary = self.granularity.lower_fuzzy_boundary \
            if cord_count > self.granularity.cord_limit else self.granularity.upper_fuzzy_boundary
        public_data_filtered_location = public_data_filtered_location[
            (public_data_filtered_location[self.location_long] < maxLong + fuzzy_boundary) & (
                public_data_filtered_location[self.location_long] > minLong - fuzzy_boundary) & (
                    public_data_filtered_location[self.location_lat] < maxLat + fuzzy_boundary) & (
                        public_data_filtered_location[self.location_lat] > minLat - fuzzy_boundary)]

        return public_data_filtered_location

    @multimethod(SparkEnv, LocationData, LocationData, list)
    def _get_possible_locations(self, env, customer_data, public_data, join_keys):
        """Get possible public data locations that are close to customer data locations."""
        # get unique public_data_filtered_location as customer_datacord from customer customer_data
        keys = [customer_data.longitude_column_name, customer_data.latitude_column_name]
        for pair in join_keys:
            keys.append(pair[0])
        customer_datacord = customer_data.data.select(keys).dropDuplicates()

        cord_count = customer_datacord.count()
        public_data_filtered_location = self._get_public_data_filtered_locations(
            env, customer_data, public_data, cord_count)

        return public_data_filtered_location, customer_datacord

    @multimethod(PandasEnv, LocationData, LocationData, list)
    def _get_possible_locations(self, env, customer_data, public_data, join_keys):
        """Get possible public data locations that are close to customer data locations."""
        # get unique public_data_filtered_location as customer_data_cord from customer customer_data
        keys = [customer_data.longitude_column_name, customer_data.latitude_column_name]
        for pair in join_keys:
            keys.append(pair[0])
        customer_data_cord = customer_data.data[keys].drop_duplicates()

        cord_count = len(customer_data_cord.index)
        public_data_filtered_location = self._get_public_data_filtered_locations(
            env, customer_data, public_data, cord_count)

        return public_data_filtered_location, customer_data_cord

    @multimethod(SparkEnv, CustomerData, object, object, object, object)
    def _get_closest_location(
            self,
            env,
            customer_data,
            public_data_filtered_location,
            customer_data_cord,
            close_to_udf,
            distance_udf):
        """
        Get closest 3p location to each customer location.

        public_data_filtered_location is latlong from third party,
        customer_data_cord is latlong from customer data.
        """
        # try binary search instead later for optimize, for now
        # cross join 3p data and custome rdata lat long. try to find closest lat/long pairing
        result = public_data_filtered_location.alias('a').crossJoin(customer_data_cord.alias('b'))
        result = result.filter(
            close_to_udf(
                self.location_long,
                self.location_lat,
                customer_data.longitude_column_name,
                customer_data.latitude_column_name))
        result = result.withColumn(
            self.distance_name,
            distance_udf(
                self.location_long,
                self.location_lat,
                customer_data.longitude_column_name,
                customer_data.latitude_column_name))

        result = result.select('*', dense_rank().over(
            Window.orderBy(
                customer_data.latitude_column_name,
                customer_data.longitude_column_name)).alias(self.public_rankgroup))

        result = result.withColumn(self.customer_rankgroup, col(self.public_rankgroup))

        # only keep shortest distance row for each store
        window = Window.partitionBy(customer_data.latitude_column_name, customer_data.longitude_column_name).orderBy(
            result[self.distance_name].asc())

        top = result.select('*', rank().over(window).alias(self.rank1))
        top = top.filter(top[self.rank1] <= self.granularity.closest_top_n)
        return top

    @multimethod(PandasEnv, CustomerData, object, object, object, object)
    def _get_closest_location(
            self,
            env,
            customer_data,
            public_data_filtered_location,
            customer_data_cord,
            close_to,
            get_distance):
        """
        Get closest 3p location to each customer location.

        public_data_filtered_location is latlong from third party,
        customer_data_cord is latlong from customer data.
        """
        # try binary search instead later for optimize, for now
        # cross join 3p data and custome rdata lat long. try to find closest lat/long pairing
        result = public_data_filtered_location.assign(key=1).merge(
            customer_data_cord.assign(key=1), on='key').drop('key', 1)
        column_close_to = 'column_close_to' + random_tag()
        result[column_close_to] = result[[
            self.location_long,
            self.location_lat,
            customer_data.longitude_column_name,
            customer_data.latitude_column_name]].apply(close_to, axis=1)
        result = result[result[column_close_to]].drop(columns=[column_close_to], axis=1)
        result[self.distance_name] = result[[
            self.location_long,
            self.location_lat,
            customer_data.longitude_column_name,
            customer_data.latitude_column_name]].apply(get_distance, axis=1)

        column_tmp = 'column_tmp' + random_tag()

        result[column_tmp] = result[[
            customer_data.latitude_column_name,
            customer_data.longitude_column_name]].fillna(0).apply(
                lambda x: math.ceil((90 + float(x[0])) * 1000) * 1000000 + math.ceil(
                    (180 + float(x[1])) * 1000), axis=1)
        result[self.public_rankgroup] = result[column_tmp].rank(axis=0, method='dense').astype(int)
        result[self.customer_rankgroup] = result[self.public_rankgroup]

        # only keep shortest distance row for each store
        result[column_tmp] = result[self.distance_name].groupby([
            result[customer_data.latitude_column_name],
            result[customer_data.longitude_column_name]]).rank()

        top = result[result[column_tmp] <= self.granularity.closest_top_n].drop(
            columns=[column_tmp], axis=1)

        return top

    @multimethod(SparkEnv, LocationData, LocationData, Aggregator, list, bool)
    def process(self, env, customer_data, public_data, aggregator, join_keys, debug):
        """
        Do the join.

        :param customer_data: an instance of LocationData derived class
        :param public_data: an instance of LocationData derived class
        :param aggregator: a specified aggregator
        :param join_keys: list of join key pairs
        :param debug: print debug logs if True
        :return: a tuple of:
            altered customer data class instance
            altered public data class instance
            a list of join key pairs
        """
        public_dataset = public_data.data

        public_dataset = aggregator.process_public_dataset(env, public_dataset, public_data.cols, join_keys)

        if debug:
            print(
                '* public_dataset in location_closest_selector: %d' %
                public_dataset.count())
            print(public_dataset)

        # get possible 3p public_data_filtered_location that are close to customer data public_data_filtered_location
        public_data_filtered_location, customer_data_cord = \
            self._get_possible_locations(env, customer_data, public_data, join_keys)

        if debug:
            print('* public_data_filtered_location: %d' % public_data_filtered_location.count())
            print(public_data_filtered_location)
            print('* customer_data_cord: %d' % customer_data_cord.count())
            print(customer_data_cord)

        # initialize udfs
        # find distance between two lat long pairs
        distance_udf = udf(self.get_distance, DoubleType())
        # find if two lat long pairs are within 10 degrees of each other
        close_to_udf = udf(self.close_to, BooleanType())

        # get closest 3p location to each customer location
        # top customer_dataset contains rows that have customer lat long pair and closest 3p lat long pair and 3p id
        top = self._get_closest_location(
            env,
            customer_data,
            public_data_filtered_location,
            customer_data_cord,
            close_to_udf,
            distance_udf)
        top.cache()

        if debug:
            print('* top: %d' % top.count())
            print(top)

        # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
        join_keys.append((self.location_id, public_data.id))

        join_conditions = []
        for pair in join_keys:
            join_conditions.append(top[pair[0]] == public_dataset[pair[1]])
        public_dataset = public_dataset.alias('a').join(
            top.alias('b'),
            join_conditions)\
            .select('a.*', '.'.join(['b', self.public_rankgroup]))\
            .drop(public_data.latitude_column_name, public_data.longitude_column_name, public_data.id)

        join_keys.remove((self.location_id, public_data.id))

        # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
        join_keys.append((self.customer_rankgroup, self.public_rankgroup))

        if debug:
            print('* public_dataset after join with top: %d' % public_dataset.count())
            print(public_dataset)
            print('* distance_name: %s' % self.distance_name)
            print('* location_id: %s' % self.location_id)

        altered_public_data = copy.copy(public_data)
        altered_public_data.data = public_dataset
        altered_public_data.id = self.public_rankgroup

        if debug:
            altered_customer_dataset = customer_data.data.alias('a').join(
                top.alias('b'),
                [customer_data.latitude_column_name, customer_data.longitude_column_name],
                how='left').select(
                    'a.*',
                    self.distance_name,
                    self.location_id,
                    '.'.join(['b', self.customer_rankgroup])).dropDuplicates()
        else:
            altered_customer_dataset = customer_data.data.alias('a').join(
                top.alias('b'),
                [customer_data.latitude_column_name, customer_data.longitude_column_name],
                how='left').select(
                    'a.*',
                    '.'.join(['b', self.customer_rankgroup])).dropDuplicates()

        altered_customer_dataset.cache()

        altered_customer_data = copy.copy(customer_data)
        altered_customer_data.data = altered_customer_dataset

        if debug:
            print('* join_keys: %s' % str(join_keys))

        altered_public_data.data.cache()

        return altered_customer_data, altered_public_data, join_keys

    @multimethod(PandasEnv, LocationData, LocationData, Aggregator, list, bool)
    def process(self, env, customer_data, public_data, aggregator, join_keys, debug):
        """
        Do the join.

        :param customer_data: an instance of LocationData derived class
        :param public_data: an instance of LocationData derived class
        :param aggregator: a specified aggregator
        :param join_keys: list of join key pairs
        :param debug: print debug logs if True
        :return: a tuple of:
            altered customer data class instance
            altered public data class instance
            a list of join key pairs
        """
        public_dataset = public_data.data

        public_dataset = aggregator.process_public_dataset(env, public_dataset, public_data.cols, join_keys)

        if debug:
            print('* public_dataset in location_closest_selector: %d' % len(public_dataset.index))
            print(public_dataset.head(5))

        # get possible 3p public_data_filtered_location that are close to customer data public_data_filtered_location
        public_data_filtered_location, customer_data_cord = self._get_possible_locations(
            env, customer_data, public_data, join_keys)

        if debug:
            print('* public_data_filtered_location: %d' % len(public_data_filtered_location.index))
            print(public_data_filtered_location.head(5))
            print('* customer_data_cord: %d' % len(customer_data_cord.index))
            print(customer_data_cord.head(5))

        # initialize udfs
        # find distance between two lat long pairs
        def distance_udf(x):
            return self.get_distance(x[0], x[1], x[2], x[3])

        # find if two lat long pairs are within 10 degrees of each other
        def close_to_udf(x):
            return self.close_to(x[0], x[1], x[2], x[3])

        # get closest 3p location to each customer location
        # top customer_dataset contains rows that have customer lat long pair and closest 3p lat long pair and 3p id
        top = self._get_closest_location(
            env,
            customer_data,
            public_data_filtered_location,
            customer_data_cord,
            close_to_udf,
            distance_udf)

        # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
        join_keys.append((self.location_id, public_data.id))
        customer_keys, public_keys = list(zip(*join_keys))

        if debug:
            print('* top: %d' % len(top.index))
            print(top.head(5))
            print(public_keys)
            print(customer_keys)

        public_dataset = public_dataset.merge(
            top,
            left_on=list(public_keys),
            right_on=list(customer_keys))[list(public_dataset.columns) + [self.public_rankgroup]]
        public_dataset = public_dataset[list(public_dataset.columns)].drop(
            columns=[
                public_data.latitude_column_name,
                public_data.longitude_column_name,
                public_data.id], axis=1)

        join_keys.remove((self.location_id, public_data.id))

        # Filter public_dataset(3p) data to only be the closest to the customer data to decrease time join time
        join_keys.append((self.customer_rankgroup, self.public_rankgroup))

        if debug:
            print('* public_dataset after join with top: %d' % len(public_dataset.index))
            print(public_dataset.head(5))
            print('* distance_name: %s' % self.distance_name)
            print('* location_id: %s' % self.location_id)
            print('* public_rankgroup: %s' % self.public_rankgroup)

        altered_public_data = copy.copy(public_data)
        altered_public_data.data = public_dataset
        altered_public_data.id = self.public_rankgroup

        altered_customer_dataset = customer_data.data.merge(
            top,
            on=[customer_data.latitude_column_name, customer_data.longitude_column_name],
            how='left')
        if debug:
            print(altered_customer_dataset.head(3))
            altered_customer_dataset = altered_customer_dataset[
                list(customer_data.data.columns) + [
                    self.distance_name, self.location_id, self.customer_rankgroup]].drop_duplicates()
        else:
            altered_customer_dataset = altered_customer_dataset[
                list(customer_data.data.columns) + [self.customer_rankgroup]].drop_duplicates()

        altered_customer_data = copy.copy(customer_data)
        altered_customer_data.data = altered_customer_dataset

        if debug:
            print('* join_keys: ' + str(join_keys))

        return altered_customer_data, altered_public_data, join_keys
