import argparse
import asyncio
import importlib.util
import sys
from time import sleep
from typing import Dict, List

import yaml

from serverchecks import run_checks, run_alerts, Outcome
from serverchecks.alerts import AbstractAlert
from serverchecks.checks import AbstractCheck


# must enter then async chain as soon as possible as any async-using objects (checks, alerts)
# need to be defined inside the event loop; otherwise they will create their own event loops
# which will be never executed
async def command(config_file: str = None) -> None:
    if not config_file:
        parser = argparse.ArgumentParser()
        parser.add_argument('config_file', type=argparse.FileType('r'), help='Configuration file')
        args = parser.parse_args()
        config_file = args.config_file

    # load configuration data from YAML
    data: Dict = yaml.load(config_file, Loader=yaml.SafeLoader)

    # set some defaults
    run_mode: str = data.get('mode', 'once')
    interval: int = data.get('interval', 60)
    verbose: bool = data.get('verbose', False)
    alert_mode: str = data.get('alert_mode', 'on_error')

    # initialize the alert transports
    alerts: List[AbstractAlert] = []
    for alert_name, alert_targets in data.get('alerts', {}).items():

        # dynamically load the alert class
        spec = importlib.util.find_spec(f'serverchecks.alerts.{alert_name}_alert')
        if spec is None:
            print(f'Cannot find alert {alert_name}, skipping')
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        # instantiate the `alerts` list with configured instances for this class
        for target in alert_targets:
            alert = mod.alert_class(**target)
            alerts.append(alert)

            if verbose:
                print(f'Initialized alert class {alert}')

    if verbose:
        print(f'Opening {len(alerts)} alert transports')

    # open alert transports
    transport_tasks = [instance.open() for instance in alerts]
    await run_alerts(transport_tasks)

    if verbose:
        print(f'{len(alerts)} alert transports opened')

    # initialize the list of checks
    checks: List[AbstractCheck] = []

    for check_name, check_targets in data.get('checks', {}).items():
        spec = importlib.util.find_spec(f'serverchecks.checks.{check_name}_check')
        if spec is None:
            print(f'Cannot find check {check_name}, skipping')
            continue
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        for target in check_targets:
            check = mod.check_class(**target)
            checks.append(check)

            if verbose:
                print(f'Initialized check class {check}')

    # start the main test & alerting loop
    continuous_run: bool = True

    if verbose:
        print(f'Entering loop with {len(checks)} checks and {len(alerts)} alerts')

    while continuous_run:
        try:
            # if run mode is set to `once` just prevent the loop from repeating
            continuous_run = run_mode == 'continuous'

            # generate list of callable coroutines from list of checks and pass to asyncio runner
            result: Outcome = await run_checks([instance.check() for instance in checks])

            # alerts are only sent if checks have failed, or if alert mode is set to `always`
            if result.status == False or alert_mode == 'always':
                send_alerts = [instance.alert(result.info) for instance in alerts]
                await run_alerts(send_alerts)

            if continuous_run:
                sleep(interval)

        except KeyboardInterrupt:
            break

    # clean up and close all active alert transports
    # this is important with some transports such as XMPP which may keep connection state on the server-side
    if verbose:
        print(f'Closing {len(alerts)} alert transports')
    transport_tasks = [instance.close() for instance in alerts]
    await run_alerts(transport_tasks)

    sys.exit(0)


if __name__ == "__main__":
    if hasattr(asyncio, 'run'):
        # for Python 3.7+
        asyncio.run(command())
    else:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(command())
        loop.close()
