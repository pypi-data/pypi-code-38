from strongr.schedulerdomain.model.scalingdrivers import ScalingDriver


class ScaleOutHandler(object):
    def __call__(self, command):
        # forward to configured scaleout driver
        ScalingDriver.scaling_driver().scaleout(command)
