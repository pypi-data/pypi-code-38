import graphene


class Order(graphene.Enum):
    DATE_CREATED_ASC = "dt_created_asc"
    DATE_CREATED_DESC = "dt_created_desc"
    DATE_MODIFIED_ASC = "dt_modified_asc"
    DATE_MODIFIED_DESC = "dt_modified_desc"


class ConnectionField(graphene.relay.ConnectionField):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("order_by", graphene.Argument(Order))
        super(ConnectionField, self).__init__(type, *args, **kwargs)


class EmployeeStatus(graphene.Enum):
    ACTIVE = "active"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    SUSPENDED = "suspended"
    DECEASED = "deceased"


class Gender(graphene.Enum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"


class Holiday(graphene.ObjectType):
    __tablename__ = "holiday"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    date = graphene.types.datetime.Date()


class HolidaySchedule(graphene.ObjectType):
    __tablename__ = "holiday_schedule"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    holidays = graphene.List(Holiday)  # FIXME


class LeaveType(graphene.Enum):
    PERSONAL = "personal"
    SICK = "sick"
    OTHER = "other"


class LeaveDuration(graphene.Enum):
    FULL_DAY = "full"
    FIRST_HALF = "1sthalf"
    SECOND_HALF = "2ndhalf"


class _Leave(graphene.ObjectType):
    __tablename__ = "leave"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    employee = graphene.Field(lambda: Employee)
    type = graphene.Field(lambda: LeaveType)
    date = graphene.types.datetime.Date()
    duration = graphene.Field(lambda: LeaveDuration)


class Leave(_Leave):
    date = graphene.String()


class WorkLocation(graphene.ObjectType):
    __tablename__ = "work_location"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    time_zone = graphene.String()
    holiday_schedule = graphene.Field(lambda: HolidaySchedule)


class WorkSchedule(graphene.ObjectType):
    __tablename__ = "work_schedule"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()

    sunday_start_time = graphene.types.datetime.Time()
    sunday_end_time = graphene.types.datetime.Time()

    monday_start_time = graphene.types.datetime.Time()
    monday_end_time = graphene.types.datetime.Time()

    tuesday_start_time = graphene.types.datetime.Time()
    tuesday_end_time = graphene.types.datetime.Time()

    wednesday_start_time = graphene.types.datetime.Time()
    wednesday_end_time = graphene.types.datetime.Time()

    thursday_start_time = graphene.types.datetime.Time()
    thursday_end_time = graphene.types.datetime.Time()

    friday_start_time = graphene.types.datetime.Time()
    friday_end_time = graphene.types.datetime.Time()

    saturday_start_time = graphene.types.datetime.Time()
    saturday_end_time = graphene.types.datetime.Time()


class Employee(graphene.ObjectType):
    __tablename__ = "employee"

    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    nick_name = graphene.String()

    gender = graphene.Field(lambda: Gender)
    birth_date = graphene.types.datetime.Date()

    phone = graphene.String()  # FIXME: define custom phone scalar
    email = graphene.String()  # FIXME: define custom email scalar
    address = graphene.String()

    joining_date = graphene.types.datetime.Date()
    title = graphene.String()
    department = graphene.String()
    time_zone = graphene.String()  # FIXME: Enum?

    reporting_to = graphene.Field(lambda: Employee)
    status = graphene.Field(lambda: EmployeeStatus)

    work_location = graphene.Field(lambda: WorkLocation)
    work_schedule = graphene.Field(lambda: WorkSchedule)
    holiday_schedule = graphene.Field(lambda: HolidaySchedule)


class GlobalSetting(graphene.ObjectType):
    __tablename__ = "global_setting"

    class Meta:
        interfaces = (graphene.relay.Node,)

    work_schedule = graphene.Field(lambda: WorkSchedule)
    work_location = graphene.Field(lambda: WorkLocation)


class EmployeeConnection(graphene.relay.Connection):
    class Meta:
        node = Employee


class HolidayConnection(graphene.relay.Connection):
    class Meta:
        node = Holiday


class HolidayScheduleConnection(graphene.relay.Connection):
    class Meta:
        node = HolidaySchedule


class LeaveConnection(graphene.relay.Connection):
    class Meta:
        node = Leave


class WorkLocationConnection(graphene.relay.Connection):
    class Meta:
        node = WorkLocation


class WorkScheduleConnection(graphene.relay.Connection):
    class Meta:
        node = WorkSchedule


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    global_setting = graphene.Field(lambda: GlobalSetting)

    employees = ConnectionField(lambda: EmployeeConnection)
    holidays = ConnectionField(lambda: HolidayConnection)
    holiday_schedules = ConnectionField(lambda: HolidayScheduleConnection)
    leaves = ConnectionField(lambda: LeaveConnection)
    work_locations = ConnectionField(lambda: WorkLocationConnection)
    work_schedules = ConnectionField(lambda: WorkScheduleConnection)


def make_schema():
    schema = graphene.Schema(query=Query)
    return schema
