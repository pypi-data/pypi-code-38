import strongr.core

import strongr.core.domain.clouddomain
import strongr.core.gateways

from strongr.schedulerdomain.model import Job, Vm, VmState, JobState

from sqlalchemy.sql import func
from sqlalchemy import and_, or_

class FindNodeWithAvailableResourcesHandler:
    _timeout = 0

    def __call__(self, query):
        db = strongr.core.gateways.Gateways.sqlalchemy_session()

        # subquery to see whats already running on vm
        subquery = db.query(Job.vm_id, func.sum(Job.cores).label('cores'), func.sum(Job.ram).label('ram')).filter(Job.state.in_([JobState.RUNNING])).group_by(Job.vm_id).subquery('j')

        query = db.query(Vm.vm_id)\
            .outerjoin(subquery, subquery.c.vm_id == Vm.vm_id)\
            .filter(
                and_(
                    or_(
                        and_( # case 1 - vm with jobs, check if vm has enough availabale resources to run the job
                            Vm.cores - subquery.c.cores >= query.cores,
                            Vm.ram - subquery.c.ram >= query.ram
                        ),
                        and_( # case 2 - vm with no jobs, check if vm has enough available resources to run the job
                            subquery.c.cores == None,
                            subquery.c.ram == None,
                            Vm.cores >= query.cores,
                            Vm.ram >= query.ram
                        )
                    ),
                    Vm.state.in_([VmState.READY]) # vm should be in state ready before we push jobs to it
                )
            ).order_by(Vm.ram - subquery.c.ram)

        results = query.all()

        if len(results) == 0:
            return None
        return results[0].vm_id
