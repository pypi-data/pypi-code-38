def _density(mean_density, material_density, material_porosity, water_density):
    return ((mean_density - water_density)
            / (material_density - (water_density * (1 - material_porosity))))


def productivity(crosssectional_area, mean_density, mean_speed,
                 material_density, material_porosity,
                 water_density=1000, coeff1=.9, coeff2=1.1, time_delta=1):
    density = _density(mean_density, material_density,
                       material_porosity, water_density)

    return (coeff1 * coeff2
            * crosssectional_area
            * mean_speed * density / time_delta)
