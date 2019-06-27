import sys

from AnyQt.QtWidgets import QFormLayout, QSizePolicy

import numpy as np

import Orange.data
from Orange import preprocess
from Orange.widgets.data.owpreprocess import (
    PreprocessAction, Description, icon_path, DescriptionRole, ParametersRole, blocked
)
from Orange.widgets import gui, settings
from Orange.widgets.widget import Output, Msg

from orangecontrib.spectroscopy.data import getx
from orangecontrib.spectroscopy.preprocess import Integrate

from orangecontrib.spectroscopy.widgets.owspectra import SELECTONE
from orangecontrib.spectroscopy.widgets.owhyper import refresh_integral_markings
from orangecontrib.spectroscopy.widgets.owpreprocess import (
    SpectralPreprocess
)
from orangecontrib.spectroscopy.widgets.preprocessors.utils import BaseEditorOrange, \
    SetXDoubleSpinBox

from orangecontrib.spectroscopy.widgets.gui import MovableVline


class IntegrateOneEditor(BaseEditorOrange):

    class Warning(BaseEditorOrange.Warning):
        out_of_range = Msg("Limit out of range.")

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)

        layout = QFormLayout()
        self.controlArea.setLayout(layout)

        minf, maxf = -sys.float_info.max, sys.float_info.max

        self.__values = {}
        self.__editors = {}
        self.__lines = {}

        for name, longname in self.integrator.parameters():
            v = 0.
            self.__values[name] = v

            e = SetXDoubleSpinBox(decimals=4, minimum=minf, maximum=maxf,
                                  singleStep=0.5, value=v)
            e.focusIn = self.activateOptions
            e.editingFinished.connect(self.edited)
            def cf(x, name=name):
                return self.set_value(name, x)
            e.valueChanged[float].connect(cf)
            self.__editors[name] = e
            layout.addRow(name, e)

            l = MovableVline(position=v, label=name)
            l.sigMoved.connect(cf)
            l.sigMoveFinished.connect(self.edited)
            self.__lines[name] = l

        self.focusIn = self.activateOptions
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.user_changed = False

    def activateOptions(self):
        self.parent_widget.curveplot.clear_markings()
        self.parent_widget.redraw_integral()
        for l in self.__lines.values():
            if l not in self.parent_widget.curveplot.markings:
                l.report = self.parent_widget.curveplot
                self.parent_widget.curveplot.add_marking(l)

    def set_value(self, name, v, user=True):
        if user:
            self.user_changed = True
        if self.__values[name] != v:
            self.__values[name] = v
            with blocked(self.__editors[name]):
                self.__editors[name].setValue(v)
                self.__lines[name].setValue(v)
            self.parent_widget.redraw_integral()
            self.changed.emit()

    def setParameters(self, params):
        if params:  # parameters were set manually set
            self.user_changed = True
        for name, _ in self.integrator.parameters():
            self.set_value(name, params.get(name, 0.), user=False)

    def parameters(self):
        return self.__values

    @classmethod
    def createinstance(cls, params):
        params = dict(params)
        values = []
        for ind, (name, _) in enumerate(cls.integrator.parameters()):
            values.append(params.get(name, 0.))
        return Integrate(methods=cls.integrator, limits=[values], metas=True)

    def execute_instance(self, instance, data):
        self.Warning.out_of_range.clear()
        if data:
            xs = getx(data)
            if len(xs):
                minx = np.min(xs)
                maxx = np.max(xs)
                # we use single integrals per Integrate: len(instance.limits) == 1
                limits = instance.limits[0]
                for v in limits:
                    if v < minx or v > maxx:
                        self.parent_widget.Warning.preprocessor()
                        self.Warning.out_of_range()
        return instance(data)


class IntegrateSimpleEditor(IntegrateOneEditor):
    qualname = "orangecontrib.infrared.integrate.simple"
    integrator = Integrate.Simple

    def set_preview_data(self, data):
        if not self.user_changed:
            x = getx(data)
            if len(x):
                self.set_value("Low limit", min(x))
                self.set_value("High limit", max(x))
                self.edited.emit()


class IntegrateBaselineEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.baseline"
    integrator = Integrate.Baseline


class IntegratePeakMaxEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.peak_max"
    integrator = Integrate.PeakMax


class IntegratePeakMaxBaselineEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.peak_max_baseline"
    integrator = Integrate.PeakBaseline


class IntegrateAtEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.closest"
    integrator = Integrate.PeakAt

    def set_preview_data(self, data):
        if not self.user_changed:
            x = getx(data)
            if len(x):
                self.set_value("Closest to", min(x))
                self.edited.emit()


class IntegratePeakXEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.peakx"
    integrator = Integrate.PeakX


class IntegratePeakXBaselineEditor(IntegrateSimpleEditor):
    qualname = "orangecontrib.infrared.integrate.peakx_baseline"
    integrator = Integrate.PeakXBaseline


PREPROCESSORS = [
    PreprocessAction(
        "Integrate", c.qualname, "Integration",
        Description(c.integrator.name, icon_path("Discretize.svg")),
        c
    ) for c in [
        IntegrateSimpleEditor,
        IntegrateBaselineEditor,
        IntegratePeakMaxEditor,
        IntegratePeakMaxBaselineEditor,
        IntegrateAtEditor,
        IntegratePeakXEditor,
        IntegratePeakXBaselineEditor
    ]
]


class OWIntegrate(SpectralPreprocess):
    name = "Integrate Spectra"
    id = "orangecontrib.spectroscopy.widgets.integrate"
    description = "Integrate spectra in various ways."
    icon = "icons/integrate.svg"
    priority = 1010
    replaces = ["orangecontrib.infrared.widgets.owintegrate.OWIntegrate"]

    settings_version = 2

    PREPROCESSORS = PREPROCESSORS
    BUTTON_ADD_LABEL = "Add integral..."

    class Outputs:
        preprocessed_data = Output("Integrated Data", Orange.data.Table, default=True)
        preprocessor = Output("Preprocessor", preprocess.preprocess.Preprocess)

    output_metas = settings.Setting(True)

    preview_on_image = True

    def __init__(self):
        self.markings_list = []
        super().__init__()
        cb = gui.checkBox(self.output_box, self, "output_metas", "Output as metas", callback=self.commit)
        self.output_box.layout().insertWidget(0, cb)  # move to top of the box
        self.curveplot.selection_type = SELECTONE
        self.curveplot.select_at_least_1 = True
        self.curveplot.selection_changed.connect(self.redraw_integral)

    def redraw_integral(self):
        dis = []
        if np.any(self.curveplot.selection_group) and self.curveplot.data:
            # select data
            ind = np.flatnonzero(self.curveplot.selection_group)[0]
            show = self.curveplot.data[ind:ind+1]

            previews = self.flow_view.preview_n()
            for i in range(self.preprocessormodel.rowCount()):
                if i in previews:
                    item = self.preprocessormodel.item(i)
                    desc = item.data(DescriptionRole)
                    params = item.data(ParametersRole)
                    if not isinstance(params, dict):
                        params = {}
                    preproc = desc.viewclass.createinstance(params)
                    preproc.metas = False
                    datai = preproc(show)
                    di = datai.domain.attributes[0].compute_value.draw_info(show)
                    color = self.flow_view.preview_color(i)
                    dis.append({"draw": di, "color": color})
        refresh_integral_markings(dis, self.markings_list, self.curveplot)

    def show_preview(self, show_info=False):
        # redraw integrals if number of preview curves was changed
        super().show_preview(False)
        self.redraw_integral()

    def create_outputs(self):
        data = self.data
        preprocessor = self._build_preprocessor()
        if data is not None and preprocessor is not None:
            data = preprocessor(data)
        return data, preprocessor

    def _build_preprocessor(self):
        plist = []
        for i in range(self.preprocessormodel.rowCount()):
            item = self.preprocessormodel.item(i)
            pp = self._create_preprocessor(item, None)
            plist.append(pp)
        if plist:
            return PreprocessorListMoveMetas(not self.output_metas, preprocessors=plist)
        else:
            return None


class PreprocessorListMoveMetas(preprocess.preprocess.PreprocessorList):
    """Move added meta variables to features if needed."""

    def __init__(self, move_metas, **kwargs):
        super().__init__(**kwargs)
        self.move_metas = move_metas

    def __call__(self, data):
        tdata = super().__call__(data)
        if self.move_metas:
            oldmetas = set(data.domain.metas)
            newmetas = [m for m in tdata.domain.metas if m not in oldmetas]
            domain = Orange.data.Domain(newmetas, data.domain.class_vars,
                                        metas=data.domain.metas)
            tdata = Orange.data.Table(domain, tdata)
        return tdata


if __name__ == "__main__":  # pragma: no cover
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    WidgetPreview(OWIntegrate).run(Orange.data.Table("collagen.csv"))
