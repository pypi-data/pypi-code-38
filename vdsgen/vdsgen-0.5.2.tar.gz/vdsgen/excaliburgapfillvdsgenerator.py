"""A class to generate a Virtual Dataset with gaps added to the source."""

from .gapfillvdsgenerator import GapFillVDSGenerator


class ExcaliburGapFillVDSGenerator(GapFillVDSGenerator):

    """A class to generate a Virtual Dataset with gaps added to the source."""

    GRID_X = 8  # All Excalibur sensors are 8 chips wide
    CHIP_SIZE = 256  # Width and height of Excalibur chips is 256 pixels

    def __init__(self, path, prefix=None, files=None, output=None, source=None,
                 source_node=None, target_node=None, fill_value=None,
                 modules=1, chip_spacing=3, module_spacing=10,
                 log_level=None):
        """
        Args:
            path(str): Root folder to find raw files and create VDS
            prefix(str): Prefix of HDF5 files to generate from
                e.g. image_ for image_1.hdf5, image_2.hdf5, image_3.hdf5
            files(list(str)): List of HDF5 files to generate from
            output(str): Name of VDS file.
            source(dict): Height, width, data_type and frames for source data
                Provide this to create a VDS for raw files that don't exist yet
            source_node(str): Data node in source HDF5 files
            target_node(str): Data node in VDS file
            fill_value(int): Fill value for spacing
            modules(int): Number of modules in sensor (1 or 3)
            chip_spacing(int): Spacing between stripes in module
            module_spacing(int): Spacing between modules
            log_level(int): Logging level (off=3, info=2, debug=1) -
                Default is info

        """
        if modules == 1:
            grid_y = 2
        elif modules == 3:
            grid_y = 6
        else:
            raise ValueError("Invalid number of modules - Must be 1 or 3")

        self.chip_spacing = chip_spacing
        self.module_spacing = module_spacing

        super(ExcaliburGapFillVDSGenerator, self).__init__(
            path, prefix, files, output, source, source_node, target_node,
            fill_value,
            self.CHIP_SIZE, self.CHIP_SIZE, self.GRID_X, grid_y,
            log_level)

    def construct_vds_spacing(self):
        """Construct lists of x and y spacings between sub-sections.

        Returns:
            tuple(list): A list of spacings for horizontal and vertical gaps

        """
        x_spacing = [self.chip_spacing] * self.GRID_X
        x_spacing[-1] = 0  # No gap on end

        y_spacing = [self.chip_spacing] * self.grid_y
        for idx in range(1, self.grid_y, 2):
            y_spacing[idx] = self.module_spacing
        y_spacing[-1] = 0  # No gap at bottom

        return x_spacing, y_spacing
