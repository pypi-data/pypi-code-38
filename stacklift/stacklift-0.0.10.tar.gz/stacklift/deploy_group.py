#!/usr/bin/env python3

import asyncio
from stacklift.deploy_template import DeployTemplate
from stacklift.cfn_deploy import DeployStatus
from stacklift.templates_config import TemplatesConfig
from stacklift.global_config import GlobalConfig
import logging

logging.basicConfig(format="[%(name)s] %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)


class DeployGroup:
    def __init__(self, config_file, group_name):
        self.config_file = config_file
        self.templates_config = TemplatesConfig(GlobalConfig(config_file).get_templates_path())

        self.group_name = group_name
        self.deploy_futures = {}

    async def deploy(self, name, start_ready_event):
        await start_ready_event.wait()

        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        template_config = self.templates_config.get_template_config(self.group_name, name)
        depends = template_config.get_depends()
        if depends:
            depend_results = await asyncio.gather(*[self.deploy_futures[x] for x in depends])
            if not all(depend_results):
                logger.info("Not start")
                return None

            if not all([x.deploy_status in [DeployStatus.UNCHANGED,
                                            DeployStatus.CHANGESET_COMPLETED] for x in depend_results]):
                raise RuntimeError("Dependent stack(s) did not complete changing")

        try:
            template_file = template_config.get_template_path()
            function_root = template_config.get_function_root()

            deploy_template = DeployTemplate(template_file=template_file,
                                             config_file=self.config_file,
                                             section_name=name,
                                             stack_desired_state=template_config.get_stack_desired_state())
            deploy_result = await deploy_template.deploy(function_root=function_root)

            return deploy_result
        except:
            logger.exception("Failed to deploy")
            return None

    async def deploy_all(self):
        start_ready_event = asyncio.Event()
        for name in self.templates_config.get_group_template_names(self.group_name):
            self.deploy_futures[name] = asyncio.ensure_future(self.deploy(name, start_ready_event))
        start_ready_event.set()

        results = await asyncio.gather(*self.deploy_futures.values())
        if not all(results):
            raise RuntimeError("Deploy failed")

        lines = ["", "# Changes", ""]
        for result in results:
            if result.deploy_status is not DeployStatus.UNCHANGED:
                lines.append(str(result))
                lines.append("")

        logger.info("\n".join(lines))


def deploy_group(config_file, group_name):
    instance = DeployGroup(config_file=config_file, group_name=group_name)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(instance.deploy_all())
