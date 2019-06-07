import traceback

from worker.worker_runtime import WorkerRuntime
from worker.worker_start import Worker


class WorkerStage:
    def run(self, state_machine):
        raise RuntimeError("unimplemented")


'''

    Stage: ENROLL

    Prev: POLL

    ON_SUCCESS: POLL

    ON_FAILURE: <Exit>

'''


class WorkerStageEnroll(WorkerStage):
    def run(self, state_machine):
        try:
            simulate_enroll_response = state_machine.runtime.simulate_enroll()
            success = state_machine.worker.enroll(simulate_enroll_response)
        except Exception as e:
            print("[Stage:ENROLL] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False

        if success:
            return state_machine.stage_poll
        else:
            return None


'''

    Stage: POLL

    Prev: ENROLL, POLL

    ON_SUCCESS:
        - If master server indicates no task: POLL_WAIT
        - If master server indicates task ready: FETCH

    ON_FAILURE:
        - If master server indicates re-enroll: ENROLL
        - If need clean up: TASK_CLEANUP
        - Otherwise: <Exit>

'''


class WorkerStagePoll(WorkerStage):
    def run(self, state_machine):
        try:
            is_poll_no_task = state_machine.runtime.is_simulate_poll_no_task()
            job_response = state_machine.runtime.get_simulated_job()

            success, \
            task_ready, \
            re_enroll, \
            need_cleanup = state_machine.worker.poll(is_poll_no_task, job_response)
        except Exception as e:
            print("[Stage:POLL] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False
            task_ready = False
            re_enroll = False
            # If an exception happens, check if the task has a non-None
            # task_uuid. If so, we need to clean up.
            if state_machine.worker.get_current_task_uuid() is not None:
                need_cleanup = True
            else:
                need_cleanup = False

        if success:
            if task_ready:
                return state_machine.stage_fetch
            else:
                return state_machine.stage_poll_wait
        elif need_cleanup:
            return state_machine.stage_task_cleanup
        elif re_enroll:
            return state_machine.stage_enroll
        else:
            return None


'''

    Stage: POLL_WAIT

    Prev: POLL

    ON_SUCCESS: POLL

    * Note that this stage always succeeds.

'''


class WorkerStagePollWait(WorkerStage):
    def run(self, state_machine):
        state_machine.worker.poll_wait()
        return state_machine.stage_poll


'''

    Stage: FETCH

    Prev: POLL

    ON_SUCCESS: PRE_RUN

    ON_FAILURE: TASK_CLEANUP

'''


class WorkerStageFetch(WorkerStage):
    def run(self, state_machine):
        try:
            args = {}
            download_code = state_machine.runtime.get_download_code()
            download_dataset = state_machine.runtime.get_download_dataset()

            if download_code is not None:
                args['download_code'] = download_code

            if download_dataset is not None:
                args['download_dataset'] = download_dataset

            success = state_machine.worker.fetch(**args)
        except Exception as e:
            print("[Stage:FETCH] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False

        if success:
            return state_machine.stage_pre_run
        else:
            return state_machine.stage_task_cleanup


'''

    Stage: PRE_RUN

    Prev: FETCH

    ON_SUCCESS: RUN

    ON_FAILURE: TASK_CLEANUP

'''


class WorkerStagePreRun(WorkerStage):
    def run(self, state_machine):
        try:
            success = state_machine.worker.pre_run()
        except Exception as e:
            print("[Stage:PRE_RUN] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False

        if success:
            return state_machine.stage_run
        else:
            return state_machine.stage_task_cleanup


'''

    Stage: RUN

    Prev: PRE_RUN

    ON_SUCCESS: SIGNAL

    ON_FAILURE: POST_RUN

'''


class WorkerStageRun(WorkerStage):
    def run(self, state_machine):
        try:
            success = True
            container_config = state_machine.runtime.container_configuration()
            state_machine.worker.run(container_config)
        except Exception as e:
            print("[Stage:RUN] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False

        if success:
            return state_machine.stage_signal
        else:
            return state_machine.stage_post_run


'''

    Stage: SIGNAL

    Prev: RUN

    ON_SUCCESS: POST_RUN

    ON_FAILURE: POST_RUN

'''


class WorkerStageSignal(WorkerStage):
    def run(self, state_machine):
        try:
            simulate_keep_alive_response = state_machine.runtime.simulate_signal_keep_alive_response()
            is_signal_finish = state_machine.runtime.is_simulate_signal_finish()
            state_machine.worker.signal(simulate_keep_alive_response, is_signal_finish)
        except Exception as e:
            print("[Stage:SIGNAL] Exception: {}".format(str(e)))
            traceback.print_exc()
            # Swallow exception here and always proceed to post_run.

        return state_machine.stage_post_run


'''

    Stage: POST_RUN

    Prev: SIGNAL

    ON_SUCCESS: TASK_CLEANUP

    ON_FAILURE: TASK_CLEANUP

'''


class WorkerStagePostRun(WorkerStage):
    def run(self, state_machine):
        try:
            args = {}
            args['simulate_need_upload_output'] = state_machine.runtime.get_upload_output()
            args['simulate_need_upload_log'] = state_machine.runtime.get_upload_log()
            args['local_output_folder'] = state_machine.runtime.get_local_output_folder()

            state_machine.worker.post_run(**args)
        except Exception as e:
            print("[Stage:POST_RUN] Exception: {}".format(str(e)))
            traceback.print_exc()
            # Swallow exception here and always proceed to task_cleanup.

        return state_machine.stage_task_cleanup


'''

    Stage: TASK_CLEANUP

    Prev: POLL, PRE_RUN, POST_RUN

    ON_SUCCESS: POLL

    ON_FAILURE: <Exit>

'''


class WorkerStageTaskCleanup(WorkerStage):
    def run(self, state_machine):
        try:
            success = state_machine.worker.task_cleanup()
        except Exception as e:
            print("[Stage:TASK_CLEANUP] Exception: {}".format(str(e)))
            traceback.print_exc()
            success = False

        if state_machine.runtime.run_once():
            return None

        if success:
            return state_machine.stage_poll
        else:
            return None


class WorkerStateMachine:
    stage_enroll = WorkerStageEnroll()
    stage_poll = WorkerStagePoll()
    stage_poll_wait = WorkerStagePollWait()
    stage_fetch = WorkerStageFetch()
    stage_pre_run = WorkerStagePreRun()
    stage_run = WorkerStageRun()
    stage_signal = WorkerStageSignal()
    stage_post_run = WorkerStagePostRun()
    stage_task_cleanup = WorkerStageTaskCleanup()

    def __init__(self, worker: Worker, runtime: WorkerRuntime):
        self.worker = worker
        self.runtime = runtime

    def start(self):
        # The entry state of the worker is always enroll.
        next_stage = self.stage_enroll.run(self)
        while next_stage is not None:
            next_stage = next_stage.run(self)
