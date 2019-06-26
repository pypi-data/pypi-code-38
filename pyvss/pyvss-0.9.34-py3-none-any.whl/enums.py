from enum import Enum


class RequestStatus(Enum):
    SUBMITTED = 'Submitted'
    PENDING = 'Pending'
    PROCESSED = 'Processed'
    IN_PROGRESS = 'In Progress'
    ERROR = 'Error Processed'
    SCHEDULED = 'Scheduled'
    MISSED = 'Missed'
    ERROR_RETRY = 'Error Retrying'
    APPROVAL_REQUIRED = 'Approval Required'
    APPROVED = 'Approved'
    REFUSED = 'Refused'
    CANCELLED = 'Cancelled'

    @staticmethod
    def members():
        return RequestStatus.__members__.keys()

    @staticmethod
    def validate(val):
        d = RequestStatus.__members__
        if val.lower() in [k.lower() for k in d.keys()]:
            # ok
            _val = val.upper()
            return d[_val]
        else:
            return False


class VmUsage(Enum):
    PRODUCTION = 'Production'
    TESTING = 'Testing'
    DEVELOPMENT = 'Development'
    QUALITY_ASSURANCE = 'Quality Assurance'
    USER_ACCEPTANCE_TESTING = 'User Acceptance Testing'

    @staticmethod
    def members():
        return RequestStatus.__members__.keys()

    @staticmethod
    def validate(val):
        d = RequestStatus.__members__
        if val.lower() in [k.lower() for k in d.keys()]:
            # ok
            _val = val.upper()
            return d[_val]
        else:
            return False


class VmBuildProcess(Enum):
    CLONE = 'clone'
    TEMPLATE = 'template'
    IMAGE = 'image'
    OS_INSTALL = 'os_install'
