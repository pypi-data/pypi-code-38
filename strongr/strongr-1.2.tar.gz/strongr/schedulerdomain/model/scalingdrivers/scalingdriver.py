import dependency_injector.containers as containers
import dependency_injector.providers as providers

import strongr.core

from strongr.schedulerdomain.model.scalingdrivers.nullscaler import NullScaler
from strongr.schedulerdomain.model.scalingdrivers.simplescaler import SimpleScaler
from strongr.schedulerdomain.model.scalingdrivers.surfhpccloudscaler import SurfHpcScaler


class ScalingDriver(containers.DeclarativeContainer):
    """IoC container of service providers."""
    _scalingdrivers = providers.Object({
        'simplescaler': SimpleScaler,
        'nullscaler':  NullScaler,
        'surfsarahpccloud': SurfHpcScaler
    })

    scaling_driver = providers.Singleton(_scalingdrivers()[strongr.core.Core.config().schedulerdomain.scalingdriver.lower()], config=dict(strongr.core.Core.config().schedulerdomain.as_dict()[strongr.core.Core.config().schedulerdomain.scalingdriver]) if strongr.core.Core.config().schedulerdomain.scalingdriver in strongr.core.Core.config().schedulerdomain.as_dict().keys() else {})
