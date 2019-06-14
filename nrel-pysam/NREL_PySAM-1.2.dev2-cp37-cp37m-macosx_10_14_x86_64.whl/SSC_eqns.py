import PySAM.Windpower as wp


def func(self):
    print(self.wind_resource_shear)


# wp.Windpower.

a = wp.new()
a.__setattr__("func", func)
a.func(a)

