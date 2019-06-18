from enum import Enum


class SlotDimensions(Enum):
    ORIGIN_CLUSTER_ID = "origin_cluster_id"
    DESTINATION_CLUSTER_ID = "destination_cluster_id"
    ROUTE_ID = "route_id"
    ZONE_ID = "zone_id"
    START_TIME = "start_time"
    END_TIME = "end_time"
    TIME_WINDOW = "time_window"
    SESSION = "session"
    TRAVEL_DISTANCE = "travel_distance"
    VEHICLE_TYPE = "vehicle_type"


class UserDimensions(Enum):
    BLACKLISTED = "blacklisted"
    PASS_PURCHASE_COUNT = "pass_purchase_count"
    ID = "id"
