import os
import sys
import io
import json
import IPython
from pandas import DataFrame, read_csv
from ipywidgets import widgets
from ipywidgets import Layout, Tab, Button, VBox, HBox, Box, FloatText, Textarea, Dropdown, Label, IntSlider, Checkbox, Text, Image, Button, SelectMultiple, HTML
from IPython.display import display
from ipywidgets import IntText
from json import dumps as jdump
from sensiml.widgets.base_widget import BaseWidget, button_handling
from sensiml.widgets.renderers import WidgetAttributeRenderer
import numpy as np

category_item_layout = Layout(
    # display='flex',
    size=16,
    # border='solid 2px',
    justify_content='flex-start',
    # background_color= 'red',
    overflow='visible'
)


def clean_name(name):
    return ''.join(e if e.isalnum() else '_' for e in name)


class ModelExploreWidget(BaseWidget):
    def __init__(self, dsk=None, level='Project', folder='knowledgepacks'):
        self._dsk = dsk
        self.kp = None
        if not os.path.exists(folder):
            os.makedirs(folder)
        self.setup(level=level)
        self._last_capture_file = None
        self._last_parent_value = None

    def _enable_buttons(self):
        self._button_recognize_signal_capturefile.disabled = False
        self._button_recognize_signal_featurefile.disabled = False

    def _disable_buttons(self):

        self._button_recognize_signal_capturefile.disabled = True
        self._button_recognize_signal_featurefile.disabled = True

    def setup(self, level):

        self.level = level

    def get_kp_dict(self):
        if self.level.lower() == 'project':
            kps = self._dsk.project.list_knowledgepacks()
        elif self.level.lower() == 'pipeline':
            kps = self._dsk.pipeline.list_knowledgepacks()
        else:
            kps = self._dsk.list_knowledgepacks()

        if isinstance(kps, DataFrame) and len(kps):
            kps = sorted([(name, value) for name, value in kps[[
                         'Name', 'kp_uuid']].values if name], key=lambda s: s[0].lower())

            return kps

        return [('', None)]

    def _load_results(self, uuid, file_name):

        model_results_folder = 'model_results'
        kp_folder = os.path.join(model_results_folder, uuid)
        results_file_path = os.path.join(kp_folder, file_name)

        if not os.path.exists(model_results_folder):
            os.mkdir(model_results_folder)
            return None

        if not os.path.exists(kp_folder):
            os.mkdir(kp_folder)
            return None

        if not os.path.exists(results_file_path):
            return None

        return read_csv(results_file_path)

    def _cache_results(self, uuid, file_name, results):

        model_results_folder = 'model_results'
        kp_folder = os.path.join(model_results_folder, uuid)
        results_file_path = os.path.join(kp_folder, file_name)

        if not os.path.exists(model_results_folder):
            os.mkdir(model_results_folder)

        if not os.path.exists(kp_folder):
            os.mkdir(kp_folder)

        return results.to_csv(results_file_path)

    def _recognize_signal_check_cache(self, b, model_switch=False):

        if model_switch or self._last_capture_file != self._widget_capture_data.value:
            self._recognize_signal(None, recognize=False)

    @button_handling
    def _recognize_signal(self, b, recognize=True):

        capture_file = self._widget_capture_data.value
        self._last_capture_file = capture_file

        self._output_recognition_classification.layout.visibility = "hidden"

        if not capture_file or not self.kp.uuid:
            return

        if self._widget_parent_select.value != self.kp.uuid:
            return

        self.results = self._load_results(self.kp.uuid, capture_file)

        if self.results is None and not recognize:
            return None

        if self.results is None:
            self._button_recognize_signal_capturefile.description = 'Classifying Signal...'
            self.results, s = self.kp.recognize_signal(
                capture=capture_file, renderer=self.renderer)
            self._button_recognize_signal_capturefile.description = 'RUN'

            if not isinstance(self.results, DataFrame):
                return None

            self._cache_results(self.kp.uuid, capture_file, self.results)

        ytick_labels = ["Unknown"]+[self.kp.class_map[x]
                                    for x in sorted(self.kp.class_map)]

        self.results = post_process(
            self.results, self._w_post_process_steps.value)

        ax = self.results.plot(y='Classification', x='SegmentStart', style='--o',
                               figsize=(16, 5), yticks=range(len(ytick_labels)),
                               title='Model: ' + self.kp.name +
                                     '  Capture: '+capture_file +
                                     "  Smoothing: {}".format(
                                         self._w_post_process_steps.value),
                               )

        _ = ax.set_yticklabels(ytick_labels)
        _ = ax.set_xlabel('time (samples)')

        fig = ax.get_figure()

        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        self._output_recognition_classification.value = buf.read()
        self._output_recognition_classification.layout.visibility = "visible"

        """
        M = []
        for i in range(self.results.shape[0]):
            M.append(eval(self.results.loc[i]['FeatureVector']))
        columns = []
        for feature in self.kp.feature_summary:
            columns.append(feature['Feature'])
        fv = DataFrame(M, columns=columns)
        fv['Labels'] = self.results.ClassificationName

        # self._dsk.pipeline.visualize_features(
        #    fv, label_column="Labels")

        # self._output_recognition_features.value = buff.read()
        # self._output_recognition_features.visibility = "visible"
        """

    def _rehydrate_model(self, b):

        if self.kp:
            pipeline_steps = self._dsk.pipeline.rehydrate_knowledgepack(
                self.kp, replace=False)

            pipeline_steps.append("r,s = dsk.pipeline.execute()")

            print('\n\n'.join(pipeline_steps))

            instructions = '#### This is a rehydrated Knowledge Pack. \n\n#### Important: Remove the quotes at the start and execute this cell to run. \n\n\n'

            df = DataFrame(
                ['"\n'+instructions+'\n\n'.join(pipeline_steps).replace('"', "\'")+'\n\n\n########""""""'])

            df.to_clipboard(index=False, header=False, excel=True)

            return pipeline_steps

        return ''

    def get_feature_file_list(self):
        ff = self._dsk.list_featurefiles(silent=True)
        if ff is not None:
            return list(ff['Name'].values)
        else:
            return []

    def get_capture_file_list(self):
        ff = self._dsk.list_captures()
        if ff is not None:
            return list(ff['Name'].values)
        else:
            return []

    def _refresh(self):
        if self._dsk is None:
            return
        if list(self._widget_capture_data.options) != [None] + self.get_capture_file_list():
            self._widget_capture_data.options = [
                None] + self.get_capture_file_list()
        self._widget_parent_select.options = self.get_kp_dict()
        self._widget_parent_select.value = self._widget_parent_select.options[0][1]

    def _clear(self):
        self._widget_parent_select.options = ['']
        self._widget_parent_select.value = ''
        self._widget_confusion_matrix.value = ''
        self._widget_feature_summary.value = ''
        self._widget_model_summary.value = ''
        self._widget_capture_data.options = ['']
        self._widget_capture_data.value = ''

    def _update_confusion_matrix(self, *args):

        if self._last_parent_value == self._widget_parent_select.value:
            return

        if self._widget_parent_select.value:
            self._last_parent_value = self._widget_parent_select.value
            self.kp = self._dsk.get_knowledgepack(
                self._widget_parent_select.value)
            self._widget_confusion_matrix.value = self.kp.confusion_matrix.__html__()
            self._widget_feature_summary.value = self._get_feature_summary_html(
                self.kp)
            self._widget_model_summary.value = self._get_model_summary_html(
                self.kp)
            self._recognize_signal_check_cache(None, model_switch=True)

    def _get_feature_summary_html(self, kp):
        return DataFrame(kp.feature_summary)[
            ['Category', 'Generator', 'Sensors']].to_html()

    def _get_model_summary_html(self, kp):
        model_summary = kp.device_configuration
        model_summary.pop('sample_rate', None)
        model_summary['uuid'] = kp.uuid

        columns = list(model_summary.keys())

        if kp.device_configuration['classifier'] == 'PME':
            important_metrics = ['classifier', 'neurons',
                                 'classification_mode', 'distance_mode', 'optimizer']
            model_summary['optimizer'] = kp.pipeline_summary[-1]['optimizers'][0]['name']
            model_summary['neurons'] = len(kp.neuron_array)
            model_summary['distance_mode'] = 'LSUP' if model_summary['distance_mode'] else 'L1'
            model_summary['classification_mode'] = 'KNN' if model_summary['classification_mode'] else 'RBF'
            columns = [x for x in model_summary.keys() if x not in
                       important_metrics]
            columns = important_metrics+columns

        if kp.device_configuration['classifier'] == 'Decision Tree Ensemble':
            model_summary['n_estimators'] = kp.pipeline_summary[-1]['optimizers'][0]['inputs']['n_estimators']
            model_summary['max_depth'] = kp.pipeline_summary[-1]['optimizers'][0]['inputs']['max_depth']
            columns = ['classifier', 'n_estimators', 'max_depth', 'uuid']

        if kp.device_configuration['classifier'] == 'Boosted Tree Ensemble':
            # TODO: Parse boosted tree ensemble
            columns = list(model_summary.keys())
            pass

        model_summary_df = DataFrame([model_summary])

        return model_summary_df[columns].to_html()

    def _refresh_models_list(self, b):
        if self._dsk:
            if self._dsk.pipeline:
                self._widget_parent_select.options = self.get_kp_dict()
                self._widget_parent_select.value = self._widget_parent_select.options[0][1]

    def create_widget(self):

        self._info_validation_method_size = widgets.Button(
            icon="question",
            disabled=True,
            tooltip='Uses a majority vote algorithm over past events in the buffer to determine the current classification. A buffer size of 1 is equivalent to no post processing.',
            layout=Layout(width="5%", align_self='flex-end')
        )

        self._button_recognize_signal_featurefile = Button(
            icon='angle-double-right',  tooltip='Run recognition against the provided test data.', layout=Layout(width='15%'))
        self._button_recognize_signal_capturefile = Button(
            icon='angle-double-right',  tooltip='Run recognition against the provided test data.', layout=Layout(width='45%'), description='RUN')
        self._button_refresh = Button(icon='refresh', layout=Layout(
            width='15%'), tooltip='Refresh Model List')
        self._button_rehydrate = Button(icon='copy', layout=Layout(
            width='15%'), tooltip='Rehydate and paste pipeline coded. Note ( The copied code will have extra """ wrapping the code, remove those before executing')
        self._widget_parent_select = Dropdown(
            description="Model Name", options=[], layout=Layout(width='85%'))
        self._widget_test_data = Dropdown(
            description="Test Data", options=[None])
        self._widget_confusion_matrix = HTML(
            disabled=True,
        )
        self._widget_feature_summary = HTML(
            disabled=True
        )
        self._widget_model_summary = HTML(
            disabled=True
        )
        self._widget_render_space = HTML(
            disabled=True
        )

        self.renderer = WidgetAttributeRenderer(
            self._widget_render_space, 'value')

        self._output_recognition_classification = widgets.Image(
            format='png', disabled=True)

        self._widget_capture_data = Dropdown(
            description="Test Data", options=[None],  layout=Layout(width='45%'))

        self._w_post_process_steps = IntSlider(
            description='Smoothing', min=1, max=100, value=1, step=5)

        model_explore_tabs = Tab([
            VBox([HBox([
                self._widget_capture_data,
                self._button_recognize_signal_capturefile,
            ]),
                HBox([
                    self._w_post_process_steps,
                    self._info_validation_method_size,

                ]),
                self._output_recognition_classification,
                # self._output_recognition_features
            ]),
            VBox([self._widget_confusion_matrix]),
            VBox([self._widget_feature_summary]),
            VBox([self._widget_model_summary]),



        ])
        self.kb_items = VBox([
            HBox([self._widget_parent_select, self._button_refresh, self._button_rehydrate
                  ]),
            model_explore_tabs,
            self._widget_render_space,
        ])

        model_explore_tabs.set_title(0, 'Test Model')
        model_explore_tabs.set_title(1, 'Confusion Matrix')
        model_explore_tabs.set_title(2, 'Feature Summary')
        model_explore_tabs.set_title(3, 'Model Summary')

        self._output_recognition_classification.layout.visibility = "hidden"

        self._button_refresh.on_click(self._refresh_models_list)
        self._button_rehydrate.on_click(self._rehydrate_model)
        self._widget_parent_select.observe(self._update_confusion_matrix)
        self._widget_capture_data.observe(self._recognize_signal_check_cache)
        self._button_recognize_signal_capturefile.on_click(
            self._recognize_signal)

        self._refresh()

        return self.kb_items


def post_process(results, buffer):

    if buffer > results.shape[0]:
        buffer = results.shape[0]

    post_processed_results = [-1]*(buffer)

    for i in range(0, results.shape[0]-buffer):
        counts = np.bincount(results['Classification'].iloc[i:i+buffer].values)
        post_processed_results.append(np.argmax(counts))

    results['Classification'] = post_processed_results

    return results[results['Classification'] != -1].reset_index(drop=True)
