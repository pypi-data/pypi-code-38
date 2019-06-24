#pylint: disable=too-few-public-methods,C0330
"""
Schema and SQLAlchemy declaratives for *hynet* grid databases.
"""

import math

from sqlalchemy import (Column,
                        String,
                        Integer,
                        Boolean,
                        Float,
                        Enum,
                        ForeignKey)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from hynet.types_ import (hynet_eps,
                          BusType,
                          BranchType,
                          InjectorType,
                          EntityType,
                          DBInfoKey)


SCHEMA_VERSION = '1.0'  # Version of the database scheme.

DEFAULT_SHORT_STRING_LENGTH = 1024
DEFAULT_LONG_STRING_LENGTH = 65535

Base = declarative_base()


def _enum_to_value(x):
    return [e.value for e in x]


class DBInfo(Base):
    """Dataset for a *hynet* grid database setting."""

    __tablename__ = 'db_info'

    # Use an unconstrained enum to parse keys from database
    key = Column(Enum(DBInfoKey,
                      native_enum=False,
                      values_callable=_enum_to_value,
                      create_constraint=False,
                      validate_strings=False),
                 primary_key=True, nullable=False)
    value = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)


class DBBus(Base):
    """Dataset for a bus."""

    __tablename__ = 'bus'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(BusType, values_callable=_enum_to_value),
                  nullable=False)
    ref = Column(Boolean, nullable=False)
    base_kv = Column(Float, nullable=False)
    v_min = Column(Float, nullable=False)
    v_max = Column(Float, nullable=False)
    zone = Column(Integer, nullable=True)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __repr__(self):
        return "{0.id}: {0.type}, {0.annotation}".format(self)

    def __eq__(self, other):
        """Return True if the data is equivalent."""
        if other is None:
            return False
        return (self.id == other.id and
                self.type == other.type and
                self.ref == other.ref and
                self.base_kv == other.base_kv and
                self.v_min == other.v_min and
                self.v_max == other.v_max and
                self.zone == other.zone and
                self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBBranch(Base):
    """Dataset for a branch."""

    __tablename__ = 'branch'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(BranchType, values_callable=_enum_to_value),
                  nullable=False)
    src_id = Column(Integer, ForeignKey('bus.id'))
    src = relationship('DBBus', foreign_keys=[src_id])
    dst_id = Column(Integer, ForeignKey('bus.id'))
    dst = relationship('DBBus', foreign_keys=[dst_id])
    r = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    b_src = Column(Float, nullable=False)
    b_dst = Column(Float, nullable=False)
    ratio_src = Column(Float, nullable=False)
    phase_src = Column(Float, nullable=False)
    ratio_dst = Column(Float, nullable=False)
    phase_dst = Column(Float, nullable=False)
    length = Column(Float, nullable=True)
    rating = Column(Float, nullable=True)
    angle_min = Column(Float, nullable=True)
    angle_max = Column(Float, nullable=True)
    drop_min = Column(Float, nullable=True)
    drop_max = Column(Float, nullable=True)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __repr__(self):
        return "{0.id}: {0.src_id}, {0.dst_id}, \"{0.annotation}\"" \
            .format(self)

    def __eq__(self, other):
        """Return True if the data is equivalent."""
        if other is None:
            return False
        return (self.id == other.id and
                self.type == other.type and
                self.src_id == other.src_id and
                self.dst_id == other.dst_id and
                self.r == other.r and
                self.x == other.x and
                self.b_src == other.b_src and
                self.b_dst == other.b_dst and
                math.isclose(self.ratio_src, other.ratio_src,
                             rel_tol=hynet_eps * 10) and
                math.isclose(self.phase_src, other.phase_src,
                             rel_tol=hynet_eps * 10) and
                math.isclose(self.ratio_dst, other.ratio_dst,
                             rel_tol=hynet_eps * 10) and
                math.isclose(self.phase_dst, other.phase_dst,
                             rel_tol=hynet_eps * 10) and
                self.length == other.length and
                self.rating == other.rating and
                self.angle_min == other.angle_min and
                self.angle_max == other.angle_max and
                self.drop_min == other.drop_min and
                self.drop_max == other.drop_max and
                self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBConverter(Base):
    """Dataset for a converter."""

    __tablename__ = 'converter'

    id = Column(Integer, primary_key=True)
    src_id = Column(Integer, ForeignKey('bus.id'))
    src = relationship('DBBus', foreign_keys=[src_id])
    dst_id = Column(Integer, ForeignKey('bus.id'))
    dst = relationship('DBBus', foreign_keys=[dst_id])
    cap_src_id = Column(Integer, ForeignKey('capability_region.id'))
    cap_src = relationship('DBCapabilityRegion', foreign_keys=[cap_src_id])
    cap_dst_id = Column(Integer, ForeignKey('capability_region.id'))
    cap_dst = relationship('DBCapabilityRegion', foreign_keys=[cap_dst_id])
    loss_fwd = Column(Float, nullable=False)
    loss_bwd = Column(Float, nullable=False)
    loss_fix = Column(Float, nullable=False)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __eq__(self, other):
        """
        Return True if the data *excl. the capability regions* is equivalent.

        **This is a customized equality operation and designed for the use
        during the saving of scenarios to a database. Apply with caution.**
        """
        if other is None:
            return False
        return (self.id == other.id and
                self.src_id == other.src_id and
                self.dst_id == other.dst_id and
                # self.cap_src_id == other.cap_src_id and
                # self.cap_dst_id == other.cap_dst_id and
                self.loss_fwd == other.loss_fwd and
                self.loss_bwd == other.loss_bwd and
                self.loss_fix == other.loss_fix and
                self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBCapabilityRegion(Base):
    """Dataset for a capability region."""

    __tablename__ = 'capability_region'

    id = Column(Integer, primary_key=True)
    p_min = Column(Float, nullable=False)
    p_max = Column(Float, nullable=False)
    q_min = Column(Float, nullable=False)
    q_max = Column(Float, nullable=False)
    lt_ofs = Column(Float, nullable=True)
    lt_slp = Column(Float, nullable=True)
    rt_ofs = Column(Float, nullable=True)
    rt_slp = Column(Float, nullable=True)
    lb_ofs = Column(Float, nullable=True)
    lb_slp = Column(Float, nullable=True)
    rb_ofs = Column(Float, nullable=True)
    rb_slp = Column(Float, nullable=True)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __eq__(self, other):
        """
        Return True if the data *excl. the ID, box, and annotation* is equivalent.

        **This is a customized equality operation and designed for the use
        during the saving of scenarios to a database. Apply with caution.**
        """
        if other is None:
            return False
        return (# self.id == other.id and
                # self.p_min == other.p_min and
                # self.p_max == other.p_max and
                # self.q_min == other.q_min and
                # self.q_max == other.q_max and
                self.lt_ofs == other.lt_ofs and
                self.lt_slp == other.lt_slp and
                self.rt_ofs == other.rt_ofs and
                self.rt_slp == other.rt_slp and
                self.lb_ofs == other.lb_ofs and
                self.lb_slp == other.lb_slp and
                self.rb_ofs == other.rb_ofs and
                self.rb_slp == other.rb_slp)
                # self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBShunt(Base):
    """Dataset for a shunt."""

    __tablename__ = 'shunt'

    id = Column(Integer, primary_key=True)
    bus_id = Column(Integer, ForeignKey('bus.id'))
    bus = relationship('DBBus', foreign_keys=[bus_id])
    p = Column(Float, nullable=False)
    q = Column(Float, nullable=False)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __eq__(self, other):
        """
        Return True if the data *excl. the ID and annotation* is equivalent.

        **This is a customized equality operation and designed for the use
        during the saving of scenarios to a database. Apply with caution.**
        """
        if other is None:
            return False
        return (# self.id == other.id and
                self.bus_id == other.bus_id and
                self.p == other.p and
                self.q == other.q)
                # self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBInjector(Base):
    """Dataset for an injector."""

    __tablename__ = 'injector'

    id = Column(Integer, primary_key=True)
    type = Column(Enum(InjectorType, values_callable=_enum_to_value),
                  nullable=False)
    bus_id = Column(Integer, ForeignKey('bus.id'))
    bus = relationship('DBBus', foreign_keys=[bus_id])
    cap_id = Column(Integer, ForeignKey('capability_region.id'))
    cap = relationship('DBCapabilityRegion', foreign_keys=[cap_id])
    cost_p_id = Column(Integer, ForeignKey('sample_point.id'))
    cost_p = relationship('DBSamplePoint', foreign_keys=[cost_p_id],
                          uselist=True)
    cost_q_id = Column(Integer, ForeignKey('sample_point.id'))
    cost_q = relationship('DBSamplePoint', foreign_keys=[cost_q_id],
                          uselist=True)
    cost_start = Column(Float, nullable=False)
    cost_stop = Column(Float, nullable=False)
    ramp_up = Column(Float, nullable=True)
    ramp_down = Column(Float, nullable=True)
    min_up = Column(Float, nullable=True)
    min_down = Column(Float, nullable=True)
    energy_min = Column(Float, nullable=True)
    energy_max = Column(Float, nullable=True)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)

    def __eq__(self, other):
        """
        Return True if the data *excl. the cap. region and cost IDs* is equivalent.

        **This is a customized equality operation and designed for the use
        during the saving of scenarios to a database. Apply with caution.**
        """
        if other is None:
            return False
        return (self.id == other.id and
                self.type == other.type and
                self.bus_id == other.bus_id and
                # self.cap_id == other.cap_id and
                # self.cost_p_id == other.cost_p_id and
                # self.cost_q_id == other.cost_q_id and
                self.cost_start == other.cost_start and
                self.cost_stop == other.cost_stop and
                self.ramp_up == other.ramp_up and
                self.ramp_down == other.ramp_down and
                self.min_up == other.min_up and
                self.min_down == other.min_down and
                self.energy_min == other.energy_min and
                self.energy_max == other.energy_max and
                self.annotation == other.annotation)

    def __hash__(self):
        return self.id


class DBSamplePoint(Base):
    """Dataset for a cost function sample point."""

    __tablename__ = 'sample_point'

    id = Column(Integer, primary_key=True)
    x = Column(Float, primary_key=True)
    y = Column(Float, nullable=False)


class DBScenario(Base):
    """Dataset for a scenario."""

    __tablename__ = 'scenario'

    id = Column(Integer, primary_key=True)
    time = Column(Float, nullable=False)
    name = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)
    loss_price = Column(Float, nullable=False)
    annotation = Column(String(DEFAULT_LONG_STRING_LENGTH), nullable=False)


class DBScenarioLoad(Base):
    """Dataset for a load in a scenario."""

    __tablename__ = 'scenario_load'

    scenario_id = Column(Integer, ForeignKey('scenario.id'), primary_key=True)
    scenario = relationship('DBScenario', foreign_keys=[scenario_id])
    bus_id = Column(Integer, ForeignKey('bus.id'), primary_key=True)
    bus = relationship('DBBus', foreign_keys=[bus_id])
    p = Column(Float, nullable=False)
    q = Column(Float, nullable=False)


class DBScenarioInjector(Base):
    """Dataset for the injector adaptation in a scenario."""

    __tablename__ = 'scenario_injector'

    scenario_id = Column(Integer, ForeignKey('scenario.id'), primary_key=True)
    scenario = relationship('DBScenario', foreign_keys=[scenario_id])
    injector_id = Column(Integer, ForeignKey('injector.id'), primary_key=True)
    injector = relationship('DBInjector', foreign_keys=[injector_id])
    p_min = Column(Float, nullable=False)
    p_max = Column(Float, nullable=False)
    q_min = Column(Float, nullable=False)
    q_max = Column(Float, nullable=False)
    cost_scaling = Column(Float, nullable=False)


class DBScenarioInactivity(Base):
    """Dataset for the inactivity specification in a scenario."""

    __tablename__ = 'scenario_inactivity'

    scenario_id = Column(Integer, ForeignKey('scenario.id'), primary_key=True)
    scenario = relationship('DBScenario', foreign_keys=[scenario_id])
    entity_type = Column(Enum(EntityType, values_callable=_enum_to_value),
                         primary_key=True)
    entity_id = Column(Integer, primary_key=True)
