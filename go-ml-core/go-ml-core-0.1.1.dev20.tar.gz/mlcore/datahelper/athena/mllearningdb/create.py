import sys
import logging

logging.basicConfig(stream=sys.stdout,
                    level=logging.INFO,
                    format='%(asctime)-s %(levelname)-7s %(name)-s.%(funcName)s(): %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class Creator():
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    #######################################################################################
    #
    #  Hive tables with partition
    #
    #######################################################################################
    def create_battery_swap_log(self, database, s3bucket='gogoro-ml-dev-model'):
        sql = '''
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
  `data` array< 
    struct< 
      `_id`: string,
      `create_time`: bigint,
      `exchange_time`: bigint,
      `swap_id`: bigint,
      `scooter_guid`: string,
      `vm_guid`: string,
      `rating`: double,
      `base_price`: double,
      `pps_price`: double,
      `rating_rule_id`: string,
      `eject_new_candidate`: boolean,
      `swap_in`:array<
        struct<
          `battery_guid`: string,
          `slot_id`: int,
          `slot_serial_id`: string,
          `healthy`: int,
          `cell_type`: int,
          `case_type`: int,
          `temp_cell`: int,
          `temp_mos`: int,
          `is_locked`: int,
          `fcc`: int,
          `consumption`: double,
          `charging_rate`: double,
          `max_charging_rate`: double,
          `chargeable`: boolean,
          `dischargeable`: boolean,
          `payload_raw`: string,
          `payload`: struct<
            `soc`: int,
            `capacity_level`: int,
            `initial_capacity`: int,
            `current_capacity`: int,
            `lifetime_charged_capacity`: int,
            `lifetime_discharged_capacity`: int,
            `fcc`: int,
            `max_cell_temp`: int,
            `min_cell_temp`: int,
            `recycle_count`: int
          >,
          `sgen_payload_version`: int,
          `hw_info_version`: int,
          `hw_info`: string,
          `ups`: int
      >>,
      `swap_out`:array<
        struct<
          `battery_guid`: string,
          `slot_id`: int,
          `slot_serial_id`: string,
          `healthy`: int,
          `cell_type`: int,
          `case_type`: int,
          `temp_cell`: int,
          `temp_mos`: int,
          `is_locked`: int,
          `fcc`: int,
          `consumption`: double,
          `charging_rate`: double,
          `max_charging_rate`: double,
          `chargeable`: boolean,
          `dischargeable`: boolean,
          `payload_raw`: string,
          `payload`: struct<
            `soc`: int,
            `capacity_level`: int,
            `initial_capacity`: int,
            `current_capacity`: int,
            `lifetime_charged_capacity`: int,
            `lifetime_discharged_capacity`: int,
            `fcc`: int,
            `max_cell_temp`: int,
            `min_cell_temp`: int,
            `recycle_count`: int
          >,
          `sgen_payload_version`: int,
          `hw_info_version`: int,
          `hw_info`: string,
          `ups`: int
      >>,
      scooter_data: struct<
        `swap_span`: int,
        `version`: string,
        `total_consumption`: double,
        `riding_distance`: double,
        `riding_history_raw`: string,
        `riding_history`: struct<
          `max_speed`: int,
          `avg_speed`: double,
          `idle_time`: int,
          `riding_time`: int,
          `total_consumption`: double
        >,
        `total_distance`: double
      >,
      trip_consumption: double
  >> 
) 
PARTITIONED BY (`dt` string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
LOCATION 's3://%s/ml/etl-workspace/battery-swap-log/' 
TBLPROPERTIES ('has_encrypted_data'='false');
        ''' % (database, 'battery_swap_log', s3bucket)

        return sql

    def create_vm_status(self, database, s3bucket='gogoro-ml-dev-model'):
        sql = '''
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
  `data` array< 
    struct< 
      `_id`: string,
      `create_time`: bigint,
      `snap_time`: bigint,
      `vm_guid`: string,
      `state`: int,
      `temperature`: int,
      `rack_temperature`: array<int>,
      `battery_single_count`: int,
      `battery_pair_count`: int,
      `power_meter`: double,
      `power_state`: int
  >> 
) 
PARTITIONED BY (`dt` string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
LOCATION 's3://%s/ml/etl-workspace/vm-status/' 
TBLPROPERTIES ('has_encrypted_data'='false');
        ''' % (database, 'vm_status', s3bucket)

        return sql

    def create_vm_battery_count(self, database, s3bucket='gogoro-ml-dev-model'):
        sql = '''
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
  `data` array< 
    struct< 
      `time_str`: string,
      `battery_counts`: array<
        struct<
          `vm_guid`: string,
          `battery_single_count`: int,
          `battery_pair_count`: int
      >>
  >> 
) 
PARTITIONED BY (`dt` string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
LOCATION 's3://%s/ml/etl-workspace/vm-battery-count/' 
TBLPROPERTIES ('has_encrypted_data'='false');
        ''' % (database, 'vm_battery_count', s3bucket)

        return sql

    def create_vm_exchange_count(self, database, s3bucket='gogoro-ml-dev-model'):
        sql = '''
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
  `data` array< 
    struct< 
      `vm_guid`: string,
      `swap_count`: int,
      `swap_battery_count`: int
  >> 
) 
PARTITIONED BY (`dt` string)
ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
LOCATION 's3://%s/ml/etl-workspace/vm-exchange-count/' 
TBLPROPERTIES ('has_encrypted_data'='false');
        ''' % (database, 'vm_exchange_count', s3bucket)

        return sql

    def create_demand_prediction(self, database, s3bucket='gogoro-ml-dev-model'):
        sql = '''
CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
  `vm_id` string,
  `prediction` double 
) PARTITIONED BY (
  dt string 
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
WITH SERDEPROPERTIES (
  'serialization.format' = ',',
  'field.delim' = ','
) LOCATION 's3://%s/ml/job-workspace/demand-prediction/'
TBLPROPERTIES ('has_encrypted_data'='false');
        ''' % (database, 'demand_prediction', s3bucket)

    #######################################################################################
    #
    #  Hive tables without partition
    #
    #######################################################################################
#     def create_vm_list(self, database, s3bucket='gogoro-ml-dev-model'):
#         sql = '''
# CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
#   `data` array< 
#     struct< 
#       `vm_id`: string,
#       `vm_guid`: string,
#       `vm_rid`: string,
#       `name`: struct <
#         `en-US`: string,
#         `zh-TW`: string
#       >,
#       `name_code`: int,
#       `latitude`: double,
#       `longitude`: double,
#       `address`: struct<
#         `en-US`: string,
#         `zh-TW`: string
#       >,
#       `district`: struct<
#         `en-US`: string,
#         `zh-TW`: string
#       >,
#       `city`: struct<
#         `en-US`: string,
#         `zh-TW`: string
#       >,
#       `zip_code`: int,
#       `country_code`: string,
#       `status`: int,
#       `battery_slot_count`: int,
#       `mainboard_guid`: string,
#       `charger_count`: int,
#       `power_supply_capacity`: int,
#       `available_time`: string,
#       `cell_config`: struct<
#         `CellConfigData`: array<
#           struct<
#             `CellType`: int,
#             `MaxChargeSpeed`: int,
#             `MaxReleaseTemperature`: int,
#             `SpeedLimitProfileType`: int
#         >>
#       >,
#       `update_time`: bigint,
#       `create_time`: bigint,
#       `battery_count`: int,
#       `battery_pair_count`: int
#   >> 
# ) 
# ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
# WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
# LOCATION 's3://%s/ml/rawdata-workspace/vm-list/latest/' 
# TBLPROPERTIES ('has_encrypted_data'='false');
#         ''' % (database, 'vm-list', s3bucket)

#         return sql

#     def create_vm_nearby(self, database, s3bucket='gogoro-ml-dev-model'):
#         sql = '''
# CREATE EXTERNAL TABLE IF NOT EXISTS %s.%s (
#   `data` array< 
#     struct< 
#       `vm_id`: string,
#       `nearby_vms`: array<
#           array<
#             `vm_id`: string,
#             `distance`: string,
#             `latitude`: double,
#             `longitude`: double,
#           >
#       >
# ) 
# ROW FORMAT SERDE 'org.openx.data.jsonserde.JsonSerDe'
# WITH SERDEPROPERTIES ('serialization.format' = '1' ) 
# LOCATION 's3://%s/ml/rawdata-workspace/vm-nearby/latest/' 
# TBLPROPERTIES ('has_encrypted_data'='false');
#         ''' % (database, 'vm-nearby', s3bucket)