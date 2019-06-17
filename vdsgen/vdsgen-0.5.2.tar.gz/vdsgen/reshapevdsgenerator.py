"""A class to generate an ND Virtual Dataset from a 1D raw dataset."""

import logging

from .vds import VirtualLayout, VirtualSource, h5slice
from .vdsgenerator import VDSGenerator, SourceMeta


class ReshapeVDSGenerator(VDSGenerator):
    """A class to generate an ND Virtual Dataset from a 1D raw dataset."""

    logger = logging.getLogger("ReshapeVDSGenerator")

    def __init__(self, shape,
                 path, prefix=None, files=None, output=None, source=None,
                 source_node=None, target_node=None, fill_value=None,
                 log_level=None,
                 alternate=None):
        """
        Args:
            shape(tuple(int)): Shape of output dataset
            alternate(tuple(bool)): Whether each axis alternates

        """
        super(ReshapeVDSGenerator, self).__init__(
            path, prefix, files, output, source, source_node, target_node,
            fill_value, log_level)

        self.total_frames = 0
        self.periods = []
        self.alternate = alternate
        self.dimensions = shape
        self.source_file = self.files[0]  # Reshape only has one raw file

    def process_source_datasets(self):
        """Grab data from the given HDF5 files and check for consistency.

        Returns:
            Source: Number of datasets and the attributes of them (frames,
                height width and data type)

        """
        data = self.grab_metadata(self.files[0])
        self.total_frames = data["frames"][0]
        for dataset in self.files[1:]:
            temp_data = self.grab_metadata(dataset)
            self.total_frames += temp_data["frames"][0]
            for attribute, value in data.items():
                if attribute != "frames" and temp_data[attribute] != value:
                    raise ValueError("Files have mismatched "
                                     "{}".format(attribute))

        source = SourceMeta(frames=data['frames'],
                            height=data['height'], width=data['width'],
                            dtype=data['dtype'])

        self.logger.debug("Source metadata retrieved:\n"
                          "  Frames: %s\n"
                          "  Height: %s\n"
                          "  Width: %s\n"
                          "  Data Type: %s", self.total_frames, *source[1:])
        return source

    def create_virtual_layout(self, source_meta):
        """Create a VirtualLayout mapping raw data to the VDS.

        Args:
            source_meta(SourceMeta): Source attributes

        Returns:
            VirtualLayout: Object describing links between raw data and VDS

        """
        if source_meta.frames[0] != self.product(self.dimensions):
            raise ValueError(
                "Length of source frames ({}) does no match target shape "
                "[{}] ({}))".format(
                    source_meta.frames[0],
                    ", ".join(str(d) for d in self.dimensions),
                    self.product(self.dimensions))
            )
        vds_shape = self.dimensions + (source_meta.height, source_meta.width)
        self.logger.debug("VDS metadata:\n"
                          "  Shape: %s\n", vds_shape)
        v_layout = VirtualLayout(vds_shape, source_meta.dtype)

        source_shape = source_meta.frames + \
            (source_meta.height, source_meta.width)
        v_source = VirtualSource(
            self.source_file, name=self.source_node,
            shape=source_shape, dtype=source_meta.dtype
        )

        if self.alternate is not None:
            v_layout = self.create_alternating_virtual_layout(
                v_source, v_layout
            )
        else:
            v_layout[...] = v_source

        return v_layout

    def create_alternating_virtual_layout(self, v_source, v_layout):
        radices = self._create_mixed_radix_set()

        for idx in range(self.product(self.dimensions)):
            nd_indices = self._calculate_axis_indices(idx, radices)

            vds_hyperslab = tuple(nd_indices +
                                  [self.FULL_SLICE, self.FULL_SLICE])
            v_layout[vds_hyperslab] = v_source[idx]

            self.logger.debug(
                "Mapping %s[%s, ...] to %s[%d, ...].",
                self.name, ", ".join(str(idx) for idx in nd_indices),
                self.source_file.split("/")[-1], idx)

        return v_layout

    def _create_mixed_radix_set(self):
        # Create a mixed radix set mapping any 1D index to an ND index
        # The 1D index is a decimal number and the ND index is the equivalent
        # representation in the mixed radix numeral system derived from shape
        # e.g. for shape (5, 3, 10) radices = 30, 10 and 1
        #   132 -> 412 (30*4 + 10*1 + 1*2) so [132] in 1D -> [4, 1, 2] in 3D
        radices = [1]  # Smallest radix is always worth 1 in decimal
        for axis_length in reversed(self.dimensions[1:]):
            radices.insert(0, radices[0] * axis_length)
        return tuple(radices)

    @staticmethod
    def product(iterable):
        """Calculate product of elements of an iterable.

        Args:
            iterable: An object capable of returning its members one at a time.
                Must have at least on element.

        Returns:
            int: Product

        """
        product = 1
        for value in iterable:
            product *= value
        return product

    def _calculate_axis_indices(self, index, radices):
        """Calculate N-dimensional axes, taking account of alternting axes.

        Args:
            index(int): 1D index to calcluate from
            radices(tuple): Mixed radix numeral definition

        Returns:
            list: ND Indices of each axis for 1D index

        """
        remaining = index  # Take a copy to modify
        axis_indices = [0 for _ in self.dimensions]
        for idx, radix in enumerate(radices):
            axis_indices[idx], remaining = divmod(remaining, radix)

        # Invert axis indices for alternating axes, if the cycle is odd
        for axis in range(1, len(self.dimensions)):
            axis_cycle = index // radices[axis - 1]
            if self.alternate[axis] and axis_cycle % 2 != 0:
                max_index = self.dimensions[axis] - 1
                axis_indices[axis] = max_index - axis_indices[axis]

        return axis_indices
