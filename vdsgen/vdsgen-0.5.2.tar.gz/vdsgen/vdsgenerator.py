"""A class for generating virtual datasets from individual HDF5 files."""

import os
import re
import logging

from collections import namedtuple

import h5py as h5

SourceMeta = namedtuple("SourceMeta", ["frames", "height", "width", "dtype"])


class VDSGenerator(object):

    """A class to generate Virtual Datasets from raw HDF5 files."""

    # Constants
    CREATE = "w"  # Will overwrite any existing file
    APPEND = "a"
    READ = "r"
    FULL_SLICE = slice(None)

    # Default Values
    fill_value = -1  # Fill value for spacing
    source_node = "data"  # Data node in source HDF5 files
    target_node = "data"  # Data node in VDS file
    mode = CREATE  # Write mode for vds file
    log_level = 2

    def __init__(self, path, prefix=None, files=None, output=None, source=None,
                 source_node=None, target_node=None, fill_value=None,
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
            log_level(int): Logging level (off=3, info=2, debug=1) -
                Default is info

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.setLevel(self.log_level * 10)

        if (prefix is None and files is None) or \
                (prefix is not None and files is not None):
            raise ValueError("One, and only one, of prefix or files required.")

        self.path = path

        # Overwrite default values with arguments, if given
        if source_node is not None:
            self.source_node = source_node
        if target_node is not None:
            self.target_node = target_node
        if fill_value is not None:
            self.fill_value = fill_value
        if log_level is not None:
            self.logger.setLevel(log_level * 10)

        # If Files not given, find files using path and prefix.
        if files is None:
            self.prefix = prefix
            self.files = self.find_files()
            files = [path_.split("/")[-1] for path_ in self.files]
        # Else, get common prefix of given files and store full path
        else:
            self.prefix = os.path.commonprefix(files)
            self.files = [os.path.join(path, file_) for file_ in files]

        # If output vds file name given, use, otherwise generate a default
        if output is None:
            self.name = self.construct_vds_name(files)
        else:
            self.name = output

        # If source not given, check files exist and get metadata.
        if source is None:
            for file_ in self.files:
                if not os.path.isfile(file_):
                    raise IOError(
                        "File {} does not exist. To create VDS from raw "
                        "files that haven't been created yet, source "
                        "must be provided.".format(file_))
            self.source_metadata = self.process_source_datasets()
        # Else, store given source metadata
        else:
            self.source_metadata = self.process_source_metadata(source)

        self.output_file = os.path.abspath(os.path.join(self.path, self.name))

    def process_source_metadata(self, source):
        frames, height, width = self.parse_shape(source['shape'])
        source_metadata = SourceMeta(
            frames=frames, height=height, width=width,
            dtype=source['dtype'])

        return source_metadata

    @staticmethod
    def parse_shape(shape):
        """Split shape into height, width and frames.

        Args:
            shape(tuple): Shape of dataset

        Returns:
            frames, height, width

        """
        # The last two elements of shape are the height and width of the image
        height, width = shape[-2:]
        # Everything before that is the frames for each axis
        frames = shape[:-2]

        return frames, height, width

    def generate_vds(self):
        """Generate a virtual dataset."""
        if os.path.isfile(self.output_file):
            with h5.File(self.output_file, self.READ, libver="latest") as vds:
                node = vds.get(self.target_node)
            if node is not None:
                raise IOError("VDS {file} already has an entry for node "
                              "{node}".format(file=self.output_file,
                                              node=self.target_node))
            else:
                self.mode = self.APPEND

        virtual_layout = self.create_virtual_layout(self.source_metadata)

        self.logger.info("Creating VDS at %s", self.output_file)
        with h5.File(self.output_file, self.mode, libver="latest") as vds:
            self.validate_node(vds)
            vds.create_virtual_dataset(self.target_node, virtual_layout,
                                       fillvalue=self.fill_value)

    def find_files(self):
        """Find HDF5 files in given folder with given prefix.

        Returns:
            list: HDF5 files in folder that have the given prefix

        """
        regex = re.compile(self.prefix + r"\d+\.(hdf5|hdf|h5)")

        files = []
        for file_ in sorted(os.listdir(self.path)):
            if re.match(regex, file_):
                files.append(os.path.abspath(os.path.join(self.path, file_)))

        if len(files) == 0:
            raise IOError("No files matching pattern found. Got path: {path}, "
                          "prefix: {prefix}".format(path=self.path,
                                                    prefix=self.prefix))
        else:
            self.logger.debug("Found datasets:\n  %s",
                              ", ".join([f.split("/")[-1] for f in files]))
            return files

    def construct_vds_name(self, files):
        """Generate the file name for the VDS from the sub files.

        Args:
            files(list(str)): HDF5 files being combined

        Returns:
            str: Name of VDS file

        """
        _, ext = os.path.splitext(files[0])
        vds_name = "{prefix}vds{ext}".format(prefix=self.prefix, ext=ext)

        self.logger.debug("Generated VDS name:\n  %s", vds_name)
        return vds_name

    def grab_metadata(self, file_path):
        """Grab data from given HDF5 file.

        Args:
            file_path(str): Path to HDF5 file

        Returns:
            dict: Number of frames, height, width and data type of datasets

        """
        h5_data = h5.File(file_path, 'r')[self.source_node]
        frames, height, width = self.parse_shape(h5_data.shape)
        data_type = h5_data.dtype

        return dict(frames=frames, height=height, width=width, dtype=data_type)

    def process_source_datasets(self):
        """Grab data from the given HDF5 files and check for consistency.

        Returns:
            Source: Number of datasets and the attributes of them (frames,
                height width and data type)

        """
        raise NotImplementedError("Must be implemented in child class")

    def create_virtual_layout(self, source_meta):
        """Create a VirtualLayout mapping raw data to the VDS.

        Args:
            source_meta(SourceMeta): Source attributes

        Returns:
            VirtualLayout: Object describing links between raw data and VDS

        """
        raise NotImplementedError("Must be implemented in child class")

    def validate_node(self, vds_file):
        """Check if it is possible to create the given node.

        Create any sub-group of the target node if it doesn't exist.

        Args:
            vds_file(h5py.File): File to check for node

        """
        while self.target_node.endswith("/"):
            self.target_node = self.target_node[:-1]

        if "/" in self.target_node:
            sub_group = self.target_node.rsplit("/", 1)[0]
            if vds_file.get(sub_group) is None:
                vds_file.create_group(sub_group)
