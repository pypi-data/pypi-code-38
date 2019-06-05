from strongr.schedulerdomain.model.scalingdrivers import ScalingDriver

class ScaleInHandler(object):
    def __call__(self, command):
        # forward to configured scalein driver
        ScalingDriver.scaling_driver().scalein(command)

