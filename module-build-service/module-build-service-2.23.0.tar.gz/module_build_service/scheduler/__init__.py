""" This is a sub-module for backend/scheduler functionality. """

import fedmsg
import moksha.hub

import module_build_service.models
import module_build_service.scheduler.consumer

import logging

log = logging.getLogger(__name__)


def main(initial_messages, stop_condition):
    """ Run the consumer until some condition is met.

    Setting stop_condition to None will run the consumer forever.
    """

    config = fedmsg.config.load_config()
    config["mbsconsumer"] = True
    config["mbsconsumer.stop_condition"] = stop_condition
    config["mbsconsumer.initial_messages"] = initial_messages

    # Moksha requires that we subscribe to *something*, so tell it /dev/null
    # since we'll just be doing in-memory queue-based messaging for this single
    # build.
    config["zmq_enabled"] = True
    config["zmq_subscribe_endpoints"] = "ipc:///dev/null"

    consumers = [module_build_service.scheduler.consumer.MBSConsumer]

    # Note that the hub we kick off here cannot send any message.  You
    # should use fedmsg.publish(...) still for that.
    moksha.hub.main(
        # Pass in our config dict
        options=config,
        # Only run the specified consumers if any are so specified.
        consumers=consumers,
        # Do not run default producers.
        producers=[],
        # Tell moksha to quiet its logging.
        framework=False,
    )


def make_simple_stop_condition(session):
    """ Return a simple stop_condition callable.

    Intended to be used with the main() function here in manage.py and tests.

    The stop_condition returns true when the latest module build enters the any
    of the finished states.
    """

    def stop_condition(message):
        # XXX - We ignore the message here and instead just query the DB.

        # Grab the latest module build.
        module = (
            session.query(module_build_service.models.ModuleBuild)
            .order_by(module_build_service.models.ModuleBuild.id.desc())
            .first()
        )
        done = (
            module_build_service.models.BUILD_STATES["failed"],
            module_build_service.models.BUILD_STATES["ready"],
            module_build_service.models.BUILD_STATES["done"],
        )
        result = module.state in done
        log.debug("stop_condition checking %r, got %r" % (module, result))
        return result

    return stop_condition
