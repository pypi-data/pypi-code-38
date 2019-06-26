import base64
import datetime
import hashlib
from itertools import groupby

import graphene
import requests
import deeputil
from promise import Promise
from promise.dataloader import DataLoader
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from .exception import ZOHOAPICallFailed, ZOHOAPIAuthFailed

MAX_NUM_PER_PAGE = 200


class DataLoader(DataLoader):
    MAX_PARALLEL = 16

    def __init__(
        self,
        *args,
        auth_key=None,
        threadpool=None,
        memoizer=None,
        cache_duration=0,
        **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.auth_key = auth_key
        self.threadpool = threadpool
        self.memoizer = memoizer
        self.cache_duration = cache_duration

    def batch_load_fn(self, keys):
        return Promise.resolve(self._get_data(keys))


class EmployeeLoader(DataLoader):
    def _get_data(self, keys):
        emps = list(
            self.threadpool.map(self._get_emp, keys, chunksize=self.MAX_PARALLEL)
        )
        return emps

    def _get_emp(self, key):
        def fn():
            url = "https://people.zoho.com/people/api/forms/employee/getDataByID"
            r = requests.get(url, params=dict(authtoken=self.auth_key, recordId=key))
            return r.json()["response"]["result"][0]

        auth_key_hash = hashlib.md5(self.auth_key.encode("utf8")).hexdigest()
        mkey = "EmployeeLoader._get_emp.{}.{}".format(key, auth_key_hash)
        return self.memoizer.get(mkey, fn, max_age=self.cache_duration)


class HolidaysLoader(DataLoader):
    def _get_data(self, keys):
        holiday_listings = list(
            self.threadpool.map(self._get_hols, keys, chunksize=self.MAX_PARALLEL)
        )
        return holiday_listings

    def _get_hols(self, key):
        def fn():
            r = requests.get(
                "https://people.zoho.com/people/api/leave/getHolidays",
                params={"authtoken": self.auth_key, "userId": key},
            )
            return r.json()["response"].get("result", [])

        auth_key_hash = hashlib.md5(self.auth_key.encode("utf8")).hexdigest()
        mkey = "HolidaysLoader._get_hols.{}.{}".format(key, auth_key_hash)
        return self.memoizer.get(mkey, fn, max_age=self.cache_duration)


class IDMappingsLoader(DataLoader):
    def _get_data(self, keys):

        _keys = set(keys)

        mappings = get_all_form_records(
            None,
            "IDMapping_View",
            auth_key=self.auth_key,
            memoizer=self.memoizer,
            cache_duration=self.cache_duration,
        )

        _mappings = []

        for m in mappings:
            eid = m["Lookup 1"].split(" ", 1)[0]
            if eid not in _keys:
                continue

            _mappings.append(
                EmployeeIDMapping(
                    employee=eid, property=m["Property"], id=m["Identifier"]
                )
            )

        _mappings = {
            k: list(v) for k, v in groupby(_mappings, key=lambda x: x.employee)
        }

        mappings = [_mappings.get(k) for k in keys]
        return mappings


class TimezoneLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve(self._get_data(keys))

    def _get_data(self, keys):
        geolocator = Nominatim(user_agent="hrisapi_zoho")
        tf = TimezoneFinder()

        tzs = []

        for k in keys:
            loc = geolocator.geocode(k)
            tzs.append(tf.timezone_at(lng=loc.longitude, lat=loc.latitude))

        return tzs


def iter_days(from_dt, to_dt):
    delta = to_dt - from_dt

    for i in range(delta.days + 1):
        yield from_dt + datetime.timedelta(i)


def _get_all_form_records(form, auth_key, search_column=None, search_value=None):

    url = "https://people.zoho.com/people/api/forms/{}/records".format(form)

    index = 0
    num_per_page = MAX_NUM_PER_PAGE

    recs = []

    while 1:
        params = dict(authtoken=auth_key, sIndex=index, rec_limit=num_per_page)
        if search_column:
            params["searchColumn"] = search_column
            params["searchValue"] = search_value

        res = requests.get(url, params=params)
        r = res.json()

        if not res.ok:
            e = r["response"]["errors"]
            emsg, ecode = e["message"], e["code"]

            if ecode == 7202:
                raise ZOHOAPIAuthFailed(emsg, ecode)
            else:
                raise ZOHOAPICallFailed(emsg, ecode)

        for rec in r:
            index += 1
            recs.append(rec)

        if len(r) < num_per_page:
            break

    return recs


def get_all_form_records(
    info,
    form,
    search_column=None,
    search_value=None,
    auth_key=None,
    memoizer=None,
    cache_duration=0,
):

    info = info or deeputil.AttrDict(context={})
    auth_key = info.context.get("auth_key", auth_key)
    memoizer = info.context.get("memoizer", memoizer)
    cache_duration = info.context.get("cache_duration", cache_duration)

    def fn():
        return _get_all_form_records(form, auth_key, search_column, search_value)

    mkey = "get_all_form_records.{}".format(
        str(
            list(
                sorted(
                    dict(
                        auth=hashlib.md5(auth_key.encode("utf8")).hexdigest(),
                        form=form,
                        search_column=search_column,
                        search_value=search_value,
                    ).items()
                )
            )
        )
    )

    return memoizer.get(mkey, fn, max_age=cache_duration)


def get_leaves(
    info, employee_id=None, min_date=None, max_date=None, leave_type=None, status=None
):

    if min_date and not isinstance(min_date, datetime.datetime):
        min_date = datetime.datetime.strptime(min_date, "%Y-%m-%d")

    if max_date and not isinstance(max_date, datetime.datetime):
        max_date = datetime.datetime.strptime(max_date, "%Y-%m-%d")

    filter_kwargs = {}
    if employee_id:
        filter_kwargs = dict(search_column="EMPLOYEEID", search_value=employee_id)

    r = get_all_form_records(info, "P_ApplyLeaveView", **filter_kwargs)

    leaves = []
    for lr in r:
        from_dt = datetime.datetime.strptime(lr["From"], "%d-%b-%Y")
        to_dt = datetime.datetime.strptime(lr["To"], "%d-%b-%Y")

        for dt in iter_days(from_dt, to_dt):

            if min_date and dt < min_date:
                continue

            if max_date and dt > max_date:
                continue

            leave = Leave(
                id=lr["recordId"],
                employee=Employee(id=lr["ownerID"]),
                type=dict(
                    personal=LeaveType.PERSONAL,
                    sick=LeaveType.SICK,
                    other=LeaveType.OTHER,
                ).get(lr["Leave Type"].lower(), "other"),
                date=dt,
                duration=LeaveDuration.FULL_DAY,
                status=dict(
                    pending=LeaveStatus.PENDING,
                    approved=LeaveStatus.APPROVED,
                    rejected=LeaveStatus.REJECTED,
                    cancelled=LeaveStatus.CANCELLED,
                ).get(lr["ApprovalStatus"].lower(), LeaveStatus.PENDING),
            )

            if leave_type and leave.type.value != leave_type:
                continue
            if status and leave.status.value != status:
                continue

            leaves.append(leave)

    return leaves


def work_location_from_emp(emp):
    w_id = emp["LocationName.ID"]
    if not w_id:
        return None

    return WorkLocation(
        id=w_id, name=emp["LocationName"], one_emp_display_id=emp["EmployeeID"]
    )


def get_work_locations(info):
    # ZOHO API doesn't appear to offer an endpoint to list work locations!
    # The process therefore is to first get a list of ALL employees,
    # Per employee, get Work location with an additional API call

    emps = get_all_form_records(info, "P_EmployeeView")
    emp_ids = [e["recordId"] for e in emps]

    def _load_many(emps):
        wlocs = [work_location_from_emp(e) for e in emps]
        wlocs = [w for w in wlocs if w]
        wlocs = sorted(wlocs, key=lambda w: w.name)
        wlocs = groupby(wlocs, key=lambda w: w.name)
        wlocs = [
            list(sorted(g, key=lambda x: x.one_emp_display_id))[0] for _, g in wlocs
        ]
        return wlocs

    return info.context["employee_loader"].load_many(emp_ids).then(_load_many)


def wsched_from_data(w, id=None):
    timings = {}

    for day in (
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ):
        skey = "{}_Start_Time".format(day)
        ekey = "{}_Stop_Time".format(day)

        for k in (skey, ekey):
            v = w[k] if k in w else w[k.replace("_", " ")]
            v = v or None
            if not v:
                continue

            h, m = [int(x) for x in v.split(":", 1)]
            v = datetime.time(h, m)
            timings[k.lower()] = v

    return WorkSchedule(id=id or w["recordId"], name=w["Name"], **timings)


class TimestampsMixin:
    created_at = graphene.types.datetime.DateTime()
    modified_at = graphene.types.datetime.DateTime()


class Order(graphene.Enum):
    DATE_CREATED_ASC = "dt_created_asc"
    DATE_CREATED_DESC = "dt_created_desc"
    DATE_MODIFIED_ASC = "dt_modified_asc"
    DATE_MODIFIED_DESC = "dt_modified_desc"


class ConnectionField(graphene.relay.ConnectionField):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault("order_by", graphene.Argument(Order))
        super(ConnectionField, self).__init__(type, *args, **kwargs)


class LeaveConnectionField(ConnectionField):
    def __init__(self, type, *args, **kwargs):
        kwargs.setdefault(
            "min_date", graphene.Argument(graphene.types.datetime.DateTime)
        )
        kwargs.setdefault(
            "max_date", graphene.Argument(graphene.types.datetime.DateTime)
        )
        kwargs.setdefault("leave_type", graphene.Argument(LeaveType))
        kwargs.setdefault("status", graphene.Argument(LeaveStatus))
        super().__init__(type, *args, **kwargs)


class EmployeeStatus(graphene.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"
    RESIGNED = "resigned"
    SUSPENDED = "suspended"
    DECEASED = "deceased"


class Gender(graphene.Enum):
    MALE = "male"
    FEMALE = "female"
    UNSPECIFIED = "unspecified"


class Holiday(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    description = graphene.String()
    date = graphene.types.datetime.Date()


class HolidaySchedule(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    holidays = ConnectionField(lambda: HolidayConnection)

    # Only for ZOHO; not general schema
    # in ZOHO, we have a one to one relation between work location and holiday schedule
    work_location = graphene.Field(lambda: WorkLocation)

    def resolve_holidays(
        self, info, first=None, last=None, before=None, after=None, order_by=None
    ):
        def fn(r):
            hols = []
            for h in r:
                from_dt = datetime.datetime.strptime(h["fromDate"], "%Y-%m-%d")
                to_dt = datetime.datetime.strptime(h["toDate"], "%Y-%m-%d")

                for dt in iter_days(from_dt, to_dt):
                    h = Holiday(
                        id=h["Id"], name=h["Name"], description=h["Remarks"], date=dt
                    )
                    hols.append(h)

            return hols

        return (
            info.context["holidays_loader"]
            .load(self.work_location.one_emp_display_id)
            .then(fn)
        )


class LeaveType(graphene.Enum):
    PERSONAL = "personal"
    SICK = "sick"
    OTHER = "other"


class LeaveDuration(graphene.Enum):
    FULL_DAY = "full"
    FIRST_HALF = "1sthalf"
    SECOND_HALF = "2ndhalf"


class LeaveStatus(graphene.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Leave(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    employee = graphene.Field(lambda: Employee)
    type = graphene.Field(lambda: LeaveType)
    date = graphene.types.datetime.Date()
    duration = graphene.Field(lambda: LeaveDuration)
    status = graphene.Field(lambda: LeaveStatus)

    @classmethod
    def get_node(cls, info, id):
        # FIXME
        pass


class WorkLocation(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()
    time_zone = graphene.String()
    holiday_schedule = graphene.Field(lambda: HolidaySchedule)

    # Only required for ZOHO; Not general schema
    one_emp_display_id = graphene.String()

    def resolve_time_zone(self, info):
        return info.context["timezone_loader"].load(self.name)

    def resolve_holiday_schedule(self, info):
        return HolidaySchedule(id=self.name, name=self.name, work_location=self)


class WorkSchedule(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)
    name = graphene.String()

    sunday_start_time = graphene.types.datetime.Time()
    sunday_stop_time = graphene.types.datetime.Time()

    monday_start_time = graphene.types.datetime.Time()
    monday_stop_time = graphene.types.datetime.Time()

    tuesday_start_time = graphene.types.datetime.Time()
    tuesday_stop_time = graphene.types.datetime.Time()

    wednesday_start_time = graphene.types.datetime.Time()
    wednesday_stop_time = graphene.types.datetime.Time()

    thursday_start_time = graphene.types.datetime.Time()
    thursday_stop_time = graphene.types.datetime.Time()

    friday_start_time = graphene.types.datetime.Time()
    friday_stop_time = graphene.types.datetime.Time()

    saturday_start_time = graphene.types.datetime.Time()
    saturday_stop_time = graphene.types.datetime.Time()


class EmployeeIDMapping(TimestampsMixin, graphene.ObjectType):
    employee = graphene.Field(lambda: Employee)

    property = graphene.String(
        description="System where this ID applies. Eg: Google, Docker etc."
    )
    id = graphene.String(description="Identifier for this employee on the property")


class Employee(TimestampsMixin, graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    id = graphene.ID(required=True)  # database id
    display_id = graphene.String()  # Employee Number / ID

    name = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    nick_name = graphene.String()

    gender = graphene.Field(lambda: Gender)
    birth_date = graphene.types.datetime.Date()

    phone = graphene.String()
    email = graphene.String()
    address = graphene.String()

    joining_date = graphene.types.datetime.Date()
    title = graphene.String()
    department = graphene.String()
    time_zone = graphene.String()

    reporting_to = graphene.Field(lambda: Employee)
    status = graphene.Field(lambda: EmployeeStatus)

    leaves = LeaveConnectionField(lambda: LeaveConnection)

    work_location = graphene.Field(lambda: WorkLocation)
    work_schedule = graphene.Field(lambda: WorkSchedule)
    holiday_schedule = graphene.Field(lambda: HolidaySchedule)

    id_mappings = graphene.List(lambda: EmployeeIDMapping)

    def _info(self, info, fn):
        return info.context["employee_loader"].load(self.id).then(fn)

    def resolve_display_id(self, info):
        return self._info(info, lambda e: e["EmployeeID"])

    def resolve_email(self, info):
        return self._info(info, lambda e: e["EmailID"])

    def resolve_name(self, info):
        return self._info(info, lambda e: "{} {}".format(e["FirstName"], e["LastName"]))

    def resolve_first_name(self, info):
        return self._info(info, lambda e: e["FirstName"])

    def resolve_last_name(self, info):
        return self._info(info, lambda e: e["LastName"])

    def resolve_created_at(self, info):
        return self._info(
            info,
            lambda e: datetime.datetime.strptime(e["AddedTime"], "%d-%b-%Y %H:%M:%S"),
        )

    def resolve_modified_at(self, info):
        return self._info(
            info,
            lambda e: datetime.datetime.strptime(
                e["ModifiedTime"], "%d-%b-%Y %H:%M:%S"
            ),
        )

    def resolve_joining_date(self, info):
        return self._info(
            info,
            lambda e: datetime.datetime.strptime(e["Dateofjoining"], "%d-%b-%Y")
            if e.get("Dateofjoining")
            else None,
        )

    def resolve_title(self, info):
        return self._info(info, lambda e: e["Designation"])

    def resolve_department(self, info):
        return self._info(info, lambda e: e["Department"])

    def resolve_reporting_to(self, info):
        return self._info(
            info,
            lambda e: Employee(id=e["Reporting_To.ID"])
            if e.get("Reporting_To.ID")
            else None,
        )

    def resolve_nick_name(self, info):
        return self._info(info, lambda e: e["Nick_Name"])

    def resolve_gender(self, info):
        return self._info(
            info,
            lambda e: dict(male=Gender.MALE, female=Gender.FEMALE).get(
                e.get("Gender", "").lower(), Gender.UNSPECIFIED
            ),
        )

    def resolve_birth_date(self, info):
        return self._info(
            info,
            lambda e: datetime.datetime.strptime(e["Date_of_birth"], "%d-%b-%Y")
            if e.get("Date_of_birth")
            else None,
        )

    def resolve_phone(self, info):
        return self._info(info, lambda e: e.get("Mobile"))

    def resolve_address(self, info):
        return self._info(info, lambda e: e.get("Address"))

    def resolve_status(self, info):
        return self._info(
            info,
            lambda e: dict(
                active=EmployeeStatus.ACTIVE,
                inactive=EmployeeStatus.INACTIVE,
                terminated=EmployeeStatus.TERMINATED,
                resigned=EmployeeStatus.RESIGNED,
                suspended=EmployeeStatus.SUSPENDED,
                deceased=EmployeeStatus.DECEASED,
            )[e.get("Employeestatus", "inactive").lower()],
        )

    def resolve_work_location(self, info):
        return self._info(info, work_location_from_emp)

    def resolve_leaves(
        self,
        info,
        first=None,
        last=None,
        before=None,
        after=None,
        order_by=None,
        min_date=None,
        max_date=None,
        leave_type=None,
        status=None,
    ):
        return self.resolve_display_id(info).then(
            lambda x: get_leaves(
                info,
                employee_id=x,
                min_date=min_date,
                max_date=max_date,
                leave_type=leave_type,
                status=status,
            )
        )

    def resolve_time_zone(self, info):
        return self.resolve_work_location(info).then(
            lambda wloc: wloc.resolve_time_zone(info) if wloc else None
        )

    def resolve_work_schedule(self, info):
        def fn(e):
            wid = e.get("Work_Schedule.ID")
            if not wid:
                return

            r = requests.get(
                "https://people.zoho.com/people/api/forms/Work_Schedule/getDataByID",
                params=dict(authtoken=info.context["auth_key"], recordId=wid),
            )
            r = r.json()["response"]["result"][0]
            return wsched_from_data(r, id=wid)

        return self._info(info, fn)

    def resolve_holiday_schedule(self, info):
        return self.resolve_work_location(info).then(
            lambda wloc: wloc.resolve_holiday_schedule(info) if wloc else None
        )

    def resolve_id_mappings(self, info):
        return self.resolve_display_id(info).then(
            lambda x: info.context["idmappings_loader"].load(x).then(lambda x: x)
        )


class GlobalSetting(graphene.ObjectType):
    class Meta:
        interfaces = (graphene.relay.Node,)

    work_schedule = graphene.Field(lambda: WorkSchedule)
    work_location = graphene.Field(lambda: WorkLocation)

    # FIXME How to map?


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
    holiday_schedules = ConnectionField(lambda: HolidayScheduleConnection)
    leaves = LeaveConnectionField(lambda: LeaveConnection)
    work_locations = ConnectionField(lambda: WorkLocationConnection)
    work_schedules = ConnectionField(lambda: WorkScheduleConnection)

    def resolve_employees(
        self, info, first=None, last=None, before=None, after=None, order_by=None
    ):
        emps = get_all_form_records(info, "P_EmployeeView")
        r = [Employee(id=e["recordId"]) for e in emps]
        return r

    def resolve_work_locations(
        self, info, first=None, last=None, before=None, after=None, order_by=None
    ):
        wlocs = get_work_locations(info)
        return wlocs

    def resolve_holiday_schedules(
        self, info, first=None, last=None, before=None, after=None, order_by=None
    ):
        def fn(wlocs):
            return [
                HolidaySchedule(id=w.id, name=w.name, work_location=w) for w in wlocs
            ]

        return get_work_locations(info).then(fn)

    def resolve_leaves(
        self,
        info,
        first=None,
        last=None,
        before=None,
        after=None,
        order_by=None,
        min_date=None,
        max_date=None,
        leave_type=None,
        status=None,
    ):
        return get_leaves(
            info,
            min_date=min_date,
            max_date=max_date,
            leave_type=leave_type,
            status=status,
        )

    def resolve_work_schedules(
        self, info, first=None, last=None, before=None, after=None, order_by=None
    ):
        wscheds = get_all_form_records(info, "Work_Schedule_View")
        wscheds = [wsched_from_data(w) for w in wscheds]
        return wscheds


def make_schema():
    schema = graphene.Schema(query=Query)
    return schema
