from ..utilities import DockerTools
from ..utilities.click_utils import pop_key_or_prompt_if


class CloudConnector(object):
    @classmethod
    def cloud_connector_defaults(cls, ctx, cloud_type, kwargs):
        prefix, config_data = DockerTools.get_config_prefix_and_file(ctx.obj.config)

        return dict(
            mali_image=ctx.obj.ml_image,
            socket_server=ctx.obj.rm_socket_server,
            config_volume=ctx.obj.rm_config_volume,
            rm_image=ctx.obj.rm_manager_image,
            container_name=ctx.obj.rm_container_name,
            prefix=prefix,
            name=pop_key_or_prompt_if(kwargs, 'connector', text='Connector [--connector]:', default='%s-%s' % (cloud_type, 'default')),
            cloud_type=cloud_type,
        ), config_data
