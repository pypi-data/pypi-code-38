from strongr.core.abstracts.abstractservice import AbstractService

from strongr.schedulerdomain.command import ScheduleJob, RunEnqueuedJobs,\
                                            StartJobOnVm, CheckJobsRunning, \
                                            EnsureMinAmountOfNodes, ScaleOut, \
                                            JobFinished, VmCreated,\
                                            VmReady, VmDestroyed, VmNew, CheckScaling,\
                                            CleanupNodes, ScaleIn, LogStats, CleanupOldJobs

from strongr.schedulerdomain.handler import ScheduleJobHandler, RunEnqueuedJobsHandler,\
                                            StartJobOnVmHandler, CheckJobsRunningHandler,\
                                            EnsureMinAmountOfNodesHandler, ScaleOutHandler, \
                                            RequestFinishedJobsHandler, JobFinishedHandler,\
                                            VmDestroyedHandler, VmReadyHandler,\
                                            VmCreatedHandler, VmNewHandler, CheckScalingHandler,\
                                            CleanupNodesHandler, ScaleInHandler, LogStatsHandler,\
                                            CleanupOldJobsHandler

from strongr.schedulerdomain.query import RequestScheduledJobs, RequestJobInfo,\
                                            FindNodeWithAvailableResources, RequestFinishedJobs,\
                                            RequestResourcesRequired, RequestVmsByState

from strongr.schedulerdomain.handler import RequestScheduledTasksHandler, RequestTaskInfoHandler,\
                                            FindNodeWithAvailableResourcesHandler, RequestResourcesRequiredHandler,\
                                            RequestVmsByStateHandler

class SchedulerService(AbstractService):
    _command_bus = None
    _query_bus = None

    def register_models(self):
        import strongr.schedulerdomain.model
        # importing alone is enough for registration

    def getCommandBus(self):
        if self._command_bus is None:
            self._command_bus = self._make_default_commandbus({
                        ScheduleJobHandler: ScheduleJob,
                        RunEnqueuedJobsHandler: RunEnqueuedJobs,
                        StartJobOnVmHandler: StartJobOnVm,
                        CheckJobsRunningHandler: CheckJobsRunning,
                        EnsureMinAmountOfNodesHandler: EnsureMinAmountOfNodes,
                        ScaleOutHandler: ScaleOut,
                        JobFinishedHandler: JobFinished,
                        VmCreatedHandler: VmCreated,
                        VmDestroyedHandler: VmDestroyed,
                        VmReadyHandler: VmReady,
                        VmNewHandler: VmNew,
                        CheckScalingHandler: CheckScaling,
                        CleanupNodesHandler: CleanupNodes,
                        ScaleInHandler: ScaleIn,
                        LogStatsHandler: LogStats,
                        CleanupOldJobsHandler: CleanupOldJobs
                    })
        return self._command_bus

    def getQueryBus(self):
        if self._query_bus is None:
            self._query_bus = self._make_default_querybus({
                    RequestScheduledTasksHandler: RequestScheduledJobs,
                    RequestTaskInfoHandler: RequestJobInfo,
                    FindNodeWithAvailableResourcesHandler: FindNodeWithAvailableResources,
                    RequestFinishedJobsHandler: RequestFinishedJobs,
                    RequestResourcesRequiredHandler: RequestResourcesRequired,
                    RequestVmsByStateHandler: RequestVmsByState
                })
        return self._query_bus
