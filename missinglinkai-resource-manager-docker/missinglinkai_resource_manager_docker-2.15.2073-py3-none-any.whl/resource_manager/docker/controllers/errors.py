class DockerFailedException(Exception):
    @classmethod
    def raise_for_state(cls, *args, exit_code=None, exit_status=None, exit_error=None, step_name=None):
        ex = cls(*args)
        ex.exit_code = exit_code
        ex.exit_status = exit_status
        ex.exit_error = exit_error
        ex.step_name = step_name
        raise ex
