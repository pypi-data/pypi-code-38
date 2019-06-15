"""
General facilities to generate a report.

To do scientific research in terms of reproducibility and traceability it's
highly necessary to report all the steps done on a given dataset and never
separate the dataset from its metadata.

This module provides functionality to create a report containing a 1D and 2D
plot of the dataset, its metadata and all processing steps including
parameters.
"""

import collections
import time

import jinja2

import aspecd.report


class LaTeXReporter(aspecd.report.LaTeXReporter):
    """
    Generate a report based on a LaTeX template provided.

    An example for using the :class:`trepr.report.LaTeXReporter` class may
    look like this::

        template_ = 'path/to/your/template.tex'
        report_output = 'path/to/your/report_output.tex'
        dataset_ = trepr.dataset.ExperimentalDataset()
        report = LaTeXReporter(template_, report_output)
        report.dataset = dataset_
        report.create()
        report.compile()

    Parameters
    ----------
    template : str
        Path to template file used to generate report.

    filename : str
        Path of the resulting template file.

    Attributes
    ----------
    dataset : :obj:`trepr.dataset.Dataset`
        Dataset structure containing raw dat as well as metadata.

    """

    def __init__(self, template='', filename=''):
        """
        Create a report rendering a template and store all files in the
        dataset repository.
        """
        # public properties
        super().__init__(template=template, filename=filename)
        self.dataset = trepr.dataset.Dataset()
        # protected properties
        self._latex_jinja_env = jinja2.Environment()
        self._metadata = dict()
        self._date = None
        self._processing_steps = collections.OrderedDict()
        self._avg_parameter = dict()
        self._figure_name = dict()

    def create(self):
        """Perform all methods to generate a report."""
        self._prepare_metadata()
        self._get_processing_steps()
        self._get_figure_names()
        self._get_current_date()
        self._create_context()
        super().create()

    def _prepare_metadata(self):
        """Prepare the metadata the way it can be rendered."""
        self._metadata = self.dataset.metadata.to_dict()
        self._metadata = self._change_keys_in_dict_recursively(self._metadata)
        self._metadata['Parameter'] = collections.OrderedDict()
        self._collect_parameters()

    def _collect_parameters(self):
        """Collect all the metadata keys."""
        for key in self._metadata.keys():
            if key not in ['Sample', 'Measurement', 'Parameter']:
                self._metadata['Parameter'][key] = \
                    self._metadata[key]

    def _get_processing_steps(self):
        """Get processing steps from history."""
        for history_record in self.dataset.history:
            self._processing_steps[history_record.processing.description] = \
                history_record.processing.parameters
        self._processing_steps = \
            self._change_keys_in_dict_recursively(self._processing_steps)

    @staticmethod
    def _change_keys_in_dict_recursively(dict_=None):
        """Replace all underscores in the keys with a space.
        Note: This is done because LaTeX interprets the underscore not as
        underscore but as command for subscription."""
        tmp_dict = collections.OrderedDict()
        for key, value in dict_.items():
            if isinstance(value, dict):
                dict_[key] = \
                    LaTeXReporter._change_keys_in_dict_recursively(value)
            tmp_dict[key.replace('_', ' ').capitalize()] = dict_[key]
        return tmp_dict

    def _get_figure_names(self):
        """Get the names of the figures used for the report."""
        for i in range(len(self.dataset.representations)):
            if self.dataset.representations[i].plot.description \
                    == '2D plot as scaled image.':
                self._figure_name['Figure2D'] = \
                    self.dataset.representations[i].plot.filename
            elif self.dataset.representations[i].plot.description \
                    == '1D line plot.':
                self._figure_name['Figure1D'] = \
                    self.dataset.representations[i].plot.filename
            else:
                pass

    def _get_current_date(self):
        """Get the current date."""
        self._date = time.strftime('%d.%m.%Y')

    def _create_context(self):
        """Create a dictionary containing all data to write the report."""
        self.context['PROCESSINGSTEPS'] = self._processing_steps
        self.context['METADATA'] = self._metadata
        self.context['DATE'] = self._date
        self.context['PROCESSINGPARAMETERS'] = self._avg_parameter
        self.context['FIGURENAMES'] = self._figure_name


if __name__ == '__main__':
    import trepr.dataset
    import trepr.io
    import trepr.processing

    template_ = 'report.tex'
    filename_ = 'test.tex'
    dataset = trepr.dataset.ExperimentalDataset()
    imp = trepr.io.SpeksimImporter(
        source='/home/popp/nas/Python/Daten/messung01')
    dataset.import_from(imp)
    poc = trepr.processing.PretriggerOffsetCompensation()
    dataset.process(poc)
    pro = trepr.processing.Averaging(
        avg_range=[4.e-7, 6.e-7], dimension=0, unit='axis')
    dataset.process(pro)
    report = LaTeXReporter(template_, filename_)
    report.dataset = dataset
    report.create()
    report.compile()
