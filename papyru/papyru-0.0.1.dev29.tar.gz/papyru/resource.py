import traceback
from logging import getLogger

from django.core.exceptions import ObjectDoesNotExist

from .problem import Problem

_logger = getLogger(__name__)


class Resource:
    def __call__(self, request, *args):
        try:
            method = getattr(self.__class__, request.method.lower())
        except AttributeError:
            return Problem.method_not_allowed().to_response()

        try:
            return method(self, request, *args)

        except Problem as problem:
            if problem.should_log:
                _logger.error('[%s] %s: %s' % (int(problem.status),
                                               problem.title,
                                               problem.detail))
            return problem.to_response()

        except ObjectDoesNotExist:
            return Problem.not_found().to_response()

        except Exception as exc:
            _logger.error(traceback.format_exc())
            return Problem.internal_error(
                'unexpected error: %s' % exc).to_response()
