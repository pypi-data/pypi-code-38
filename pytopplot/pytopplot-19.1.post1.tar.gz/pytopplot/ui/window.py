from tempfile import mkdtemp
from os import path
from time import sleep
import subprocess
import csv
from shutil import rmtree, copyfile
from os import environ, access, X_OK
from os.path import isfile
import platform
import yaml

from PyQt5 import QtWidgets, uic, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.lines as mlines

import pytopplot.generator.generator as gen
import pytopplot.parse.parser as prs

# Window field maps
ITEST = {"Calculate": 0, "Test": 1}
MROT = {"Monopole fields": 0, "Dipole fields": 1}
NWFUN = {
    "Kaiser-Bessel window": 1,
    "4-term 74dB Blackman-Harris window": 2,
    "Gaussian window": 3,
}
# Inverted field maps
RITEST = {j: i for i, j in ITEST.items()}
RMROT = {j: i for i, j in MROT.items()}
RNWFUN = {j: i for i, j in NWFUN.items()}


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, topdir):
        super(MainWindow, self).__init__()
        uic.loadUi(path.join(topdir, "ui", "window.ui"), self)  # load UI
        self.appCloseAction.triggered.connect(self.close)  # close button
        self.execLocation.setText(
            path.join(topdir, "abci", platform.system(), "abci.exe")
        )  # set executable path in settings window
        self.tempDir = None  # temp dir for data files
        self.data = []
        self.topdir = topdir  # entry point file location
        self.lastdir = (
            environ["HOMEPATH"] if platform.system() == "Windows" else environ["HOME"]
        )  # holds last accessed directory

        # setup matplotlib
        self.pCanvas = MplCanvas(self)
        self.pToolbar = NavigationToolbar(self.pCanvas, self)
        self.pFrame.layout().addWidget(self.pCanvas)
        self.pFrame.layout().addWidget(self.pToolbar)

        # geometry related
        self.gCanvas = MplCanvas(self)
        self.gFrame.layout().addWidget(self.gCanvas)
        self.gToolbar = NavigationToolbar(self.gCanvas, self)
        self.gFrame.layout().addWidget(self.gToolbar)
        self.gUploadButton.clicked.connect(self.gupload)
        self.gDownloadButton.clicked.connect(self.gdownload)
        self.gDrawButton.clicked.connect(self.gdraw)
        self.gStyle.addItems(["Absolute", "Incremental"])
        self.gMenu = QtWidgets.QMenu()
        self.gTable.contextMenuEvent = lambda event: self.gMenu.popup(
            QtGui.QCursor.pos()
        )
        gAddBAction = QtWidgets.QAction("Add row before", self)
        gAddBAction.triggered.connect(self.gaddb)
        self.gMenu.addAction(gAddBAction)
        gAddAAction = QtWidgets.QAction("Add row after", self)
        gAddAAction.triggered.connect(self.gadda)
        self.gMenu.addAction(gAddAAction)
        gRemAction = QtWidgets.QAction("Remove Rows", self)
        gRemAction.triggered.connect(self.grem)
        self.gMenu.addAction(gRemAction)

        # job related
        self.jABCUploadButton.clicked.connect(self.jabcupload)
        self.jABCDownloadButton.clicked.connect(self.jabcdownload)
        self.jYAMLUploadButton.clicked.connect(self.jyamlupload)
        self.jYAMLDownloadButton.clicked.connect(self.jyamldownload)
        self.jCalculateButton.clicked.connect(self.jcalculate)
        self.ITEST.addItems(["Calculate", "Test"])
        self.MROT.addItems(["Monopole fields", "Dipole fields"])
        self.NWFUN.addItems(
            [
                "Kaiser-Bessel window",
                "4-term 74dB Blackman-Harris window",
                "Gaussian window",
            ]
        )
        self.jTable.itemSelectionChanged.connect(self.jtableselchanged)
        self.jTable.itemChanged.connect(self.jtableitemchanged)
        self.jMenu = QtWidgets.QMenu()
        self.jTable.contextMenuEvent = lambda event: self.jMenu.popup(
            QtGui.QCursor.pos()
        )
        jAddBAction = QtWidgets.QAction("Add row before", self)
        jAddBAction.triggered.connect(self.jaddb)
        self.jMenu.addAction(jAddBAction)
        jAddAAction = QtWidgets.QAction("Add row after", self)
        jAddAAction.triggered.connect(self.jadda)
        self.jMenu.addAction(jAddAAction)
        jRemAction = QtWidgets.QAction("Remove Row", self)
        jRemAction.triggered.connect(self.jrem)
        self.jMenu.addAction(jRemAction)
        self.LCBACK.toggled.connect(self.jlcbackchanged)
        self.LPLE.toggled.connect(self.jlplchanged)
        self.LPLC.toggled.connect(self.jlplchanged)

        # draw related
        self.pList.currentRowChanged.connect(self.plistselect)
        self.pUploadButton.clicked.connect(self.pupload)
        self.pDownloadButton.clicked.connect(self.pdownload)

        # settings
        self.execFindButton.clicked.connect(self.ssetExec)

        # shortcuts
        self.gShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+1"), self)
        self.gShortcut.activated.connect(lambda: self.Tabs.setCurrentIndex(0))
        self.jShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+2"), self)
        self.jShortcut.activated.connect(lambda: self.Tabs.setCurrentIndex(1))
        self.pShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+3"), self)
        self.pShortcut.activated.connect(lambda: self.Tabs.setCurrentIndex(2))
        self.sShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+4"), self)
        self.sShortcut.activated.connect(lambda: self.Tabs.setCurrentIndex(3))
        self.sShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+PgDown"), self)
        self.sShortcut.activated.connect(self.nexttab)
        self.sShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+PgUp"), self)
        self.sShortcut.activated.connect(self.prevtab)
        self.genShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("g"), self)
        self.genShortcut.activated.connect(self.gentab)
        self.meshShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("m"), self)
        self.meshShortcut.activated.connect(self.meshtab)
        self.beamShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("b"), self)
        self.beamShortcut.activated.connect(self.beamtab)
        self.timeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("t"), self)
        self.timeShortcut.activated.connect(self.timetab)
        self.wakeShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("w"), self)
        self.wakeShortcut.activated.connect(self.waketab)
        self.plotShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("p"), self)
        self.plotShortcut.activated.connect(self.plottab)
        self.printShortcut = QtWidgets.QShortcut(QtGui.QKeySequence("l"), self)
        self.printShortcut.activated.connect(self.printtab)

        self.jobList = gen.JobList()
        self.jobLastSelected = -1
        self.show()

    def gentab(self, *arg):
        """select generic tab"""
        self.settingsPage.setCurrentIndex(0)

    def meshtab(self, *arg):
        """select mesh tab"""
        self.settingsPage.setCurrentIndex(1)

    def beamtab(self, *arg):
        """select beam tab"""
        self.settingsPage.setCurrentIndex(2)

    def timetab(self, *arg):
        """select time tab"""
        self.settingsPage.setCurrentIndex(3)

    def waketab(self, *arg):
        """select wake tab"""
        self.settingsPage.setCurrentIndex(4)

    def plottab(self, *arg):
        """select plot tab"""
        self.settingsPage.setCurrentIndex(5)

    def printtab(self, *arg):
        """select print tab"""
        self.settingsPage.setCurrentIndex(6)

    def nexttab(self, *arg):
        """select next tab"""
        next = (
            self.Tabs.currentIndex() + 1
            if self.Tabs.currentIndex() < self.Tabs.count() - 1
            else 0
        )
        self.Tabs.setCurrentIndex(next)

    def prevtab(self, *arg):
        """select previous tab"""
        next = (
            self.Tabs.currentIndex() - 1
            if self.Tabs.currentIndex() > 0
            else self.Tabs.count() - 1
        )
        self.Tabs.setCurrentIndex(next)

    def gupload(self, *arg):
        """upload geometry file"""
        file, type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", self.lastdir, "CSV Files (*.csv);;All Files (*)"
        )
        if isfile(file):
            self.lastdir = path.dirname(file)
            try:
                with open(file, "r") as f:
                    self.gTable.setRowCount(0)
                    reader = csv.reader(f)
                    i = 0
                    for row in reader:
                        if len(row) == 2:
                            self.gTable.insertRow(i)
                            r = QtWidgets.QTableWidgetItem()
                            r.setText(row[0])
                            z = QtWidgets.QTableWidgetItem()
                            z.setText(row[1])
                            self.gTable.setItem(i, 0, r)
                            self.gTable.setItem(i, 1, z)
                            i += 1
            except PermissionError:
                dialog = AlertWindow(self.topdir, "Cannot open file")
                dialog.exec_()

    def gdownload(self, *arg):
        """download geometry file"""
        file, type = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.lastdir, "CSV Files (*.csv);;All Files (*)"
        )
        if file != "":
            self.lastdir = path.dirname(file)
            try:
                with open(file, "w") as f:
                    wr = csv.writer(f, quoting=csv.QUOTE_ALL)
                    for i in range(0, self.gTable.rowCount()):
                        r = ""
                        z = ""
                        if (
                            self.gTable.item(i, 0) is not None
                            and self.gTable.item(i, 0).text() != ""
                        ):
                            r = self.gTable.item(i, 0).text()
                            if (
                                self.gTable.item(i, 1) is not None
                                and self.gTable.item(i, 1).text() != ""
                            ):
                                z = self.gTable.item(i, 1).text()
                                if r != "" or z != "":
                                    wr.writerow((r, z))
            except PermissionError:
                dialog = AlertWindow(self.topdir, "Cannot open file")
                dialog.exec_()

    def gdraw(self, *arg):
        """draw geometry plot"""
        data = []
        for i in range(0, self.gTable.rowCount()):
            r = ""
            z = ""
            if (
                self.gTable.item(i, 0) is not None
                and self.gTable.item(i, 0).text() != ""
            ):
                r = self.gTable.item(i, 0).text()
            if (
                self.gTable.item(i, 1) is not None
                and self.gTable.item(i, 1).text() != ""
            ):
                z = self.gTable.item(i, 1).text()
            if r != "" or z != "":
                data.append((r, z))

        if self.tempDir is not None:
            try:
                rmtree(self.tempDir)
            except FileNotFoundError:
                pass
        self.tempDir = mkdtemp()
        inputfile = path.join(self.tempDir, "workfile.abc")
        outputfile = path.join(self.tempDir, "workfile.top")
        gen.generate_file(
            inputfile,
            self.gStyle.currentText(),
            data,
            {"gensec": gen.DEFAULTGEN, "timesec": gen.DEFAULTTIME},
            [
                {
                    "meshsec": gen.DEFAULTMESH,
                    "beamsec": gen.DEFAULTBEAM,
                    "wakesec": gen.DEFAULTWAKE,
                    "plotsec": gen.DEFAULTPLOT,
                    "printsec": gen.DEFAULTPRINT,
                }
            ],
        )
        proc = subprocess.Popen(
            [self.execLocation.text(), inputfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        rv = proc.wait()
        if rv != 0:
            out = "\n".join([l.decode().strip() for l in proc.stderr.readlines()])
            out = "Non-zero exit code\n" + out
            dialog = AlertWindow(self.topdir, out)
            dialog.exec_()
        else:
            plto = prs.top_parse(outputfile)
            if len(plto) == 0:
                dialog = AlertWindow(
                    self.topdir,
                    "Top parser error. \
Check geometry.",
                )
                dialog.exec_()
            else:
                plto = plto[0]
                data = plto.data_dump()
                self.gCanvas.axes.clear()
                for style in data.keys():
                    for d in data[style]:
                        self.gCanvas.axes.plot(
                            d[:, 0], d[:, 1], linestyle=style, color="black"
                        )
                        self.gCanvas.axes.set_title(plto.title_dump())
                        self.gCanvas.axes.set_xlabel(plto.xlab_dump())
                self.gCanvas.axes.set_ylabel(plto.ylab_dump())
                self.gCanvas.axes.grid()
                legends = []
                for style, label in plto.legends_dump().items():
                    legends.append(
                        mlines.Line2D(
                            [], [], color="black", linestyle=style, label=label
                        )
                    )
                if len(legends) > 0:
                    self.gCanvas.axes.legend(handles=legends)
                self.gCanvas.draw()

    def gaddb(self, *arg):
        """Add geometry list row before"""
        self.gTable.insertRow(self.gTable.currentRow())

    def gadda(self, *arg):
        """Add geometry list row after"""
        self.gTable.insertRow(self.gTable.currentRow() + 1)

    def grem(self, *arg):
        """Remove geometry list row"""
        rmrange = self.gTable.selectedRanges()[0]
        for i in range(rmrange.bottomRow(), rmrange.topRow() - 1, -1):
            self.gTable.removeRow(i)

    def jabcupload(self, *arg):
        """Upload .abc file"""
        file, type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", self.lastdir, "ABC Files (*.abc);;All Files (*)"
        )
        if isfile(file):
            self.Tabs.setEnabled(False)
            self.Tabs.repaint()

            if self.tempDir is not None:
                try:
                    rmtree(self.tempDir)
                except FileNotFoundError:
                    pass
            self.tempDir = mkdtemp()
            inputfile = path.join(self.tempDir, "workfile.abc")
            copyfile(file, inputfile)
            outputfile = path.join(self.tempDir, "workfile.top")
            proc = subprocess.Popen(
                [self.execLocation.text(), inputfile],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                bufsize=0,
            )
            progress = ProgressWindow(self.topdir, proc)
            progress.exec_()
            rv = proc.wait()
            if rv != 0:
                out = "\n".join([l.decode().strip() for l in proc.stderr.readlines()])
                out = "Non-zero exit code\n" + out
                dialog = AlertWindow(self.topdir, out)
                dialog.exec_()
            else:
                plto = prs.top_parse(outputfile)
                if len(plto) == 0:
                    dialog = AlertWindow(
                        self.topdir,
                        "Top parser error. \
    Check geometry and settings.",
                    )
                    dialog.exec_()
                else:
                    self.data = plto
                    self.pList.clear()
                    for i in self.data:
                        title = (
                            i.title_dump()
                            if i.title_dump() != ""
                            else "No name avaliable"
                        )
                        self.pList.addItem(title)

            self.Tabs.setEnabled(True)

    def jabcdownload(self, *arg):
        """Download .abc file"""
        file, type = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.lastdir, "ABC Files (*.abc);;All Files (*)"
        )
        if file != "":
            j = self.jobList.get(self.jobLastSelected)
            if j is not None:
                j.settings(self.jgetsettings())
            else:
                self.jobList.set_anonym(self.jgetsettings())
            self.jobList.set_common(self.jgetcommsettings())
            data = []
            for i in range(0, self.gTable.rowCount()):
                r = ""
                z = ""
                if (
                    self.gTable.item(i, 0) is not None
                    and self.gTable.item(i, 0).text() != ""
                ):
                    r = self.gTable.item(i, 0).text()
                    if (
                        self.gTable.item(i, 1) is not None
                        and self.gTable.item(i, 1).text() != ""
                    ):
                        z = self.gTable.item(i, 1).text()
                    if r != "" or z != "":
                        data.append((r, z))

                if self.tempDir is not None:
                    try:
                        rmtree(self.tempDir)
                    except FileNotFoundError:
                        pass
                self.tempDir = mkdtemp()
                inputfile = path.join(self.tempDir, "workfile.abc")
                gen.generate_file(
                    inputfile,
                    self.gStyle.currentText(),
                    data,
                    self.jobList.get_common(),
                    self.jobList.dump_settings(),
                )
            try:
                copyfile(inputfile, file)
            except IOError:
                dialog = AlertWindow(self.topdir, "Cannot open file")
                dialog.exec_()

    def jyamlupload(self, *arg):
        """Upload YAML settings"""
        file, type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", self.lastdir, "YAML Files (*.yaml);;All Files (*)"
        )
        if file != "":
            self.lastdir = path.dirname(file)
            try:
                with open(file, "r") as f:
                    jobList = yaml.load(f)
                    if jobList.version() != gen.SETTINGS_VERSION:
                        dialog = AlertWindow(self.topdir, "File version do not match")
                        dialog.exec_()
                    else:
                        self.jobList = jobList
                        self.jTable.blockSignals(True)
                        self.jTable.setRowCount(0)
                        i = 0
                        for j in self.jobList.iterate_list():
                            new = QtWidgets.QTableWidgetItem()
                            new.setText(j.name())
                            j.index(i)
                            self.jTable.insertRow(i)
                            self.jTable.setItem(i, 0, new)
                            i += 1
                        new = QtWidgets.QTableWidgetItem()
                        self.jTable.insertRow(i)
                        self.jTable.setItem(i, 0, new)
                        self.jTable.setCurrentCell(0, 0)
                        self.jobLastSelected = 0
                        j = self.jobList.get(0)
                        if j is None:
                            self.jsetsettings(self.jobList.get_anonym())
                        else:
                            self.jsetsettings(j.settings())
                        self.jsetcommsettings(self.jobList.get_common())
                        self.jTable.blockSignals(False)
            except PermissionError:
                dialog = AlertWindow(self.topdir, "Cannot open file")
                dialog.exec_()

    def jyamldownload(self, *arg):
        """Download YAML settings"""
        file, type = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.lastdir, "YAML Files (*.yaml);;All Files (*)"
        )
        if file != "":
            self.lastdir = path.dirname(file)
            self.jobList.set_common(self.jgetcommsettings())
            j = self.jobList.get(self.jobLastSelected)
            if j is None:
                self.jobList.set_anonym(self.jgetsettings())
            else:
                j.settings(self.jgetsettings())
            try:
                with open(file, "w") as f:
                    yaml.dump(self.jobList, f)
            except PermissionError:
                dialog = AlertWindow(self.topdir, "Cannot open file")
                dialog.exec_()

    def jlcbackchanged(self, *arg):
        """Uncheck LPLE and LPLC settings if LCBACK changed"""
        if arg[0]:
            self.LPLE.setChecked(False)
            self.LPLC.setChecked(False)

    def jlplchanged(self, *arg):
        """Uncheck LCBACK setting if LPLC changed"""
        if arg[0]:
            self.LCBACK.setChecked(False)

    def jcalculate(self, *arg):
        """Start calculation"""
        self.Tabs.setEnabled(False)
        self.Tabs.repaint()
        j = self.jobList.get(self.jobLastSelected)
        if j is None:
            self.jobList.set_anonym(self.jgetsettings())
        else:
            j.settings(self.jgetsettings())
        self.jobList.set_common(self.jgetcommsettings())
        data = []
        for i in range(0, self.gTable.rowCount()):
            r = ""
            z = ""
            if (
                self.gTable.item(i, 0) is not None
                and self.gTable.item(i, 0).text() != ""
            ):
                r = self.gTable.item(i, 0).text()
            if (
                self.gTable.item(i, 1) is not None
                and self.gTable.item(i, 1).text() != ""
            ):
                z = self.gTable.item(i, 1).text()
            if r != "" or z != "":
                data.append((r, z))

        if self.tempDir is not None:
            try:
                rmtree(self.tempDir)
            except FileNotFoundError:
                pass
        self.tempDir = mkdtemp()
        inputfile = path.join(self.tempDir, "workfile.abc")
        outputfile = path.join(self.tempDir, "workfile.top")
        gen.generate_file(
            inputfile,
            self.gStyle.currentText(),
            data,
            self.jobList.get_common(),
            self.jobList.dump_settings(),
        )
        proc = subprocess.Popen(
            [self.execLocation.text(), inputfile],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=0,
        )
        progress = ProgressWindow(
            self.topdir, proc, self.jobList.get_common()["gensec"]["TITLE"]
        )
        progress.exec_()
        rv = proc.wait()
        if rv != 0:
            out = "\n".join([l.decode().strip() for l in proc.stderr.readlines()])
            out = "Non-zero exit code\n" + out
            dialog = AlertWindow(self.topdir, out)
            dialog.exec_()
        else:
            plto = prs.top_parse(outputfile)
            if len(plto) == 0:
                dialog = AlertWindow(
                    self.topdir,
                    "Top parser error. \
Check geometry and settings.",
                )
                dialog.exec_()
            else:
                self.data = plto
                self.pList.clear()
                for i in self.data:
                    title = (
                        i.title_dump() if i.title_dump() != "" else "No name avaliable"
                    )
                    self.pList.addItem(title)
        self.Tabs.setEnabled(True)

    def jaddb(self, *arg):
        """Add job list row before"""
        self.jTable.blockSignals(True)
        index = self.jTable.currentRow()
        self.jTable.insertRow(index)
        [
            j.index(j.index() + 1)
            for j in self.jobList.iterate_list()
            if j.index() >= index
        ]
        self.jobLastSelected = self.jobLastSelected + 1
        self.jTable.blockSignals(False)

    def jadda(self, *arg):
        """Add job list row after"""
        self.jTable.blockSignals(True)
        index = self.jTable.currentRow() + 1
        self.jTable.insertRow(index)
        [
            j.index(j.index() + 1)
            for j in self.jobList.iterate_list()
            if j.index() >= index
        ]
        self.jTable.blockSignals(False)

    def jrem(self, *arg):
        """Remove job list row"""
        self.jTable.blockSignals(True)
        index = self.jTable.selectedRanges()[0].bottomRow()
        if self.jobList.get(index) is not None:
            dialog = AlertWindow(
                self.topdir,
                "Can remove empty cells only. \
Remove name to delete",
            )
            dialog.exec_()
        else:
            self.jTable.removeRow(index)
            [
                i.index(i.index() - 1)
                for i in self.jobList.iterate_list()
                if i.index() > index
            ]
            j = self.jobList.get(index)
            if j is None:
                self.jsetsettings(self.jobList.get_anonym())
            else:
                self.jsetsettings(j.settings())
            self.jobLastSelected = index
        self.jTable.blockSignals(False)

    def jtableselchanged(self, *arg):
        """Selected another job"""
        lj = self.jobList.get(self.jobLastSelected)
        if lj is not None:
            lj.settings(self.jgetsettings())
        else:
            self.jobList.set_anonym(self.jgetsettings())

        if len(self.jTable.selectedIndexes()) == 0:
            self.jobLastSelected = -1
            self.jsetsettings(self.jobList.get_anonym())
        else:
            index = self.jTable.selectedIndexes()[0].row()
            j = self.jobList.get(index)
            if j is not None:
                self.jobLastSelected = j.index()
                self.jsetsettings(j.settings())
            else:
                self.jobLastSelected = -1
                self.jsetsettings(self.jobList.get_anonym())

    def jtableitemchanged(self, *arg):
        """Edited job"""
        index = self.jTable.selectedIndexes()[0].row()
        text = self.jTable.item(index, 0).text()
        j = self.jobList.pop(index)
        if j is not None:
            if text == "" and j.name() != "":
                self.jobLastSelected = -1
                self.jsetsettings(self.jobList.get_anonym())
            else:
                j.name(text)
                self.jobLastSelected = j.index()
                self.jobList.push(j)
        else:
            if text != "":
                self.jobList.add(name=text, index=index, settings=self.jgetsettings())
                self.jobLastSelected = index

    def jgetcommsettings(self, *arg):
        """Create common settings dict"""
        d = {"gensec": {}, "timesec": {}}
        d["gensec"]["TITLE"] = self.TITLE.text()
        d["gensec"]["LSAV"] = self.LSAV.isChecked()
        d["gensec"]["LREC"] = self.LREC.isChecked()
        d["gensec"]["LCPUTM"] = self.LCPUTM.isChecked()
        d["gensec"]["ITEST"] = ITEST[self.ITEST.currentText()]
        d["gensec"]["TSOS"] = self.TSOS.value()
        d["gensec"]["TMAX"] = self.TMAX.value()
        d["timesec"]["MT"] = self.MT.value()
        d["timesec"]["NSHOT"] = self.NSHOT.value()
        d["timesec"]["TPS"] = self.TPS.text() if self.TPS.text() != "" else None

        return d

    def jgetsettings(self, *arg):
        """Retrieve job settings"""
        d = {"meshsec": {}, "beamsec": {}, "wakesec": {}, "plotsec": {}, "printsec": {}}
        d["meshsec"]["DDR"] = self.DDR.text() if self.DDR.text() != "" else None
        d["meshsec"]["RMARK"] = self.RMARK.text() if self.RMARK.text() != "" else None
        d["meshsec"]["NR"] = self.NR.text() if self.NR.text() != "" else None
        d["meshsec"]["NZ"] = self.NZ.text() if self.NZ.text() != "" else None
        d["meshsec"]["RZ"] = self.RZ.text() if self.RZ.text() != "" else None
        d["meshsec"]["DDZ"] = self.DDZ.text()
        d["beamsec"]["MROT"] = MROT[self.MROT.currentText()]
        d["beamsec"]["NBUNCH"] = self.NBUNCH.value()
        d["beamsec"]["ISIG"] = self.ISIG.value()
        d["beamsec"]["BSEP"] = self.BSEP.value()
        d["beamsec"]["SIG"] = self.SIG.text() if self.SIG.text() != "" else None
        d["beamsec"]["RDRIVE"] = (
            self.RDRIVE.text() if self.RDRIVE.text() != "" else None
        )
        d["wakesec"]["UBT"] = self.UBT.text() if self.UBT.text() != "" else None
        d["wakesec"]["ZCF"] = self.ZCF.text() if self.ZCF.text() != "" else None
        d["wakesec"]["ZCT"] = self.ZCT.text() if self.ZCT.text() != "" else None
        d["wakesec"]["RWAK"] = self.RWAK.text() if self.RWAK.text() != "" else None
        d["wakesec"]["ZSEP"] = self.ZSEP.value()
        d["wakesec"]["LCFRON"] = self.LCFRON.isChecked()
        d["wakesec"]["LCBACK"] = self.LCBACK.isChecked()
        d["wakesec"]["LCHIN"] = self.LCHIN.isChecked()
        d["wakesec"]["LNAPOLY"] = self.LNAPOLY.isChecked()
        d["wakesec"]["LNONAP"] = self.LNONAP.isChecked()
        d["wakesec"]["LCRBW"] = self.LCRBW.isChecked()
        d["plotsec"]["LCAVIN"] = self.LCAVIN.isChecked()
        d["plotsec"]["LCAVUS"] = self.LCAVUS.isChecked()
        d["plotsec"]["LPATH"] = self.LPATH.isChecked()
        d["plotsec"]["LPLW"] = self.LPLW.isChecked()
        d["plotsec"]["LPLWL"] = self.LPLWL.isChecked()
        d["plotsec"]["LPLWA"] = self.LPLWA.isChecked()
        d["plotsec"]["LPLWT"] = self.LPLWT.isChecked()
        d["plotsec"]["LFFT"] = self.LFFT.isChecked()
        d["plotsec"]["LFFTL"] = self.LFFTL.isChecked()
        d["plotsec"]["LFFTA"] = self.LFFTA.isChecked()
        d["plotsec"]["LFFTT"] = self.LFFTT.isChecked()
        d["plotsec"]["LINTZ"] = self.LINTZ.isChecked()
        d["plotsec"]["LSPEC"] = self.LSPEC.isChecked()
        d["plotsec"]["LWNDW"] = self.LWNDW.isChecked()
        d["plotsec"]["LPLE"] = self.LPLE.isChecked()
        d["plotsec"]["LPLC"] = self.LPLC.isChecked()
        d["plotsec"]["LPALL"] = self.LPALL.isChecked()
        d["plotsec"]["ALPHA"] = self.ALPHA.value()
        d["plotsec"]["EXPFAC"] = self.EXPFAC.value()
        d["plotsec"]["CUTOFF"] = self.CUTOFF.value()
        d["plotsec"]["NPLOT"] = self.NPLOT.value()
        d["plotsec"]["NWFUN"] = NWFUN[self.NWFUN.currentText()]
        d["printsec"]["LPRW"] = self.LPRW.isChecked()
        d["printsec"]["LMATPR"] = self.LMATPR.isChecked()
        d["printsec"]["LSVW"] = self.LSVW.isChecked()
        d["printsec"]["LSVWL"] = self.LSVWL.isChecked()
        d["printsec"]["LSVWA"] = self.LSVWA.isChecked()
        d["printsec"]["LSVWT"] = self.LSVWT.isChecked()
        d["printsec"]["LSVF"] = self.LSVF.isChecked()
        return d

    def jsetcommsettings(self, d):
        """Set common settings"""
        self.TITLE.setText(d["gensec"]["TITLE"])
        self.LSAV.setChecked(d["gensec"]["LSAV"])
        self.LREC.setChecked(d["gensec"]["LREC"])
        self.LCPUTM.setChecked(d["gensec"]["LCPUTM"])
        self.ITEST.setCurrentText(RITEST[d["gensec"]["ITEST"]])
        self.TSOS.setValue(d["gensec"]["TSOS"])
        self.TMAX.setValue(d["gensec"]["TMAX"])
        self.MT.setValue(d["timesec"]["MT"])
        self.NSHOT.setValue(d["timesec"]["NSHOT"])
        if d["timesec"]["TPS"] is None:
            self.TPS.setText("")
        else:
            self.TPS.setText(d["timesec"]["TPS"])

    def jsetsettings(self, d):
        """Set job settings"""
        if d["meshsec"]["DDR"] is None:
            self.DDR.setText("")
        else:
            self.DDR.setText(d["meshsec"]["DDR"])
        if d["meshsec"]["RMARK"] is None:
            self.RMARK.setText("")
        else:
            self.RMARK.setText(d["meshsec"]["RMARK"])
        if d["meshsec"]["NR"] is None:
            self.NR.setText("")
        else:
            self.NR.setText(d["meshsec"]["NR"])
        if d["meshsec"]["NZ"] is None:
            self.NZ.setText("")
        else:
            self.NZ.setText(d["meshsec"]["NZ"])
        if d["meshsec"]["RZ"] is None:
            self.RZ.setText("")
        else:
            self.RZ.setText(d["meshsec"]["RZ"])
        self.DDZ.setText(d["meshsec"]["DDZ"])
        self.MROT.setCurrentText(RMROT[d["beamsec"]["MROT"]])
        self.NBUNCH.setValue(d["beamsec"]["NBUNCH"])
        self.ISIG.setValue(d["beamsec"]["ISIG"])
        self.BSEP.setValue(d["beamsec"]["BSEP"])
        if d["beamsec"]["SIG"] is None:
            self.SIG.setText("")
        else:
            self.SIG.setText(d["beamsec"]["SIG"])
        if d["beamsec"]["RDRIVE"] is None:
            self.RDRIVE.setText("")
        else:
            self.RDRIVE.setText(d["beamsec"]["RDRIVE"])
        if d["wakesec"]["UBT"] is None:
            self.UBT.setText("")
        else:
            self.UBT.setText(d["wakesec"]["UBT"])
        if d["wakesec"]["ZCF"] is None:
            self.ZCF.setText("")
        else:
            self.ZCF.setText(d["wakesec"]["ZCF"])
        if d["wakesec"]["ZCT"] is None:
            self.ZCT.setText("")
        else:
            self.ZCT.setText(d["wakesec"]["ZCT"])
        if d["wakesec"]["RWAK"] is None:
            self.RWAK.setText("")
        else:
            self.RWAK.setText(d["wakesec"]["RWAK"])
        self.ZSEP.setValue(d["wakesec"]["ZSEP"])
        self.LCFRON.setChecked(d["wakesec"]["LCFRON"])
        self.LCBACK.setChecked(d["wakesec"]["LCBACK"])
        self.LCHIN.setChecked(d["wakesec"]["LCHIN"])
        self.LNAPOLY.setChecked(d["wakesec"]["LNAPOLY"])
        self.LNONAP.setChecked(d["wakesec"]["LNONAP"])
        self.LCRBW.setChecked(d["wakesec"]["LCRBW"])
        self.LCAVIN.setChecked(d["plotsec"]["LCAVIN"])
        self.LCAVUS.setChecked(d["plotsec"]["LCAVUS"])
        self.LPATH.setChecked(d["plotsec"]["LPATH"])
        self.LPLW.setChecked(d["plotsec"]["LPLW"])
        self.LPLWL.setChecked(d["plotsec"]["LPLWL"])
        self.LPLWA.setChecked(d["plotsec"]["LPLWA"])
        self.LPLWT.setChecked(d["plotsec"]["LPLWT"])
        self.LFFT.setChecked(d["plotsec"]["LFFT"])
        self.LFFTL.setChecked(d["plotsec"]["LFFTL"])
        self.LFFTA.setChecked(d["plotsec"]["LFFTA"])
        self.LFFTT.setChecked(d["plotsec"]["LFFTT"])
        self.LINTZ.setChecked(d["plotsec"]["LINTZ"])
        self.LSPEC.setChecked(d["plotsec"]["LSPEC"])
        self.LWNDW.setChecked(d["plotsec"]["LWNDW"])
        self.LPLE.setChecked(d["plotsec"]["LPLE"])
        self.LPLC.setChecked(d["plotsec"]["LPLC"])
        self.LPALL.setChecked(d["plotsec"]["LPALL"])
        self.ALPHA.setValue(d["plotsec"]["ALPHA"])
        self.EXPFAC.setValue(d["plotsec"]["EXPFAC"])
        self.CUTOFF.setValue(d["plotsec"]["CUTOFF"])
        self.NPLOT.setValue(d["plotsec"]["NPLOT"])
        self.NWFUN.setCurrentText(RNWFUN[d["plotsec"]["NWFUN"]])
        self.LPRW.setChecked(d["printsec"]["LPRW"])
        self.LMATPR.setChecked(d["printsec"]["LMATPR"])
        self.LSVW.setChecked(d["printsec"]["LSVW"])
        self.LSVWL.setChecked(d["printsec"]["LSVWL"])
        self.LSVWA.setChecked(d["printsec"]["LSVWA"])
        self.LSVWT.setChecked(d["printsec"]["LSVWT"])
        self.LSVF.setChecked(d["printsec"]["LSVF"])

    def pupload(self, *arg):
        """Upload .top file"""
        file, type = QtWidgets.QFileDialog.getOpenFileName(
            self, "Open File", self.lastdir, "TopDraw Files (*.top);;All Files (*)"
        )
        if isfile(file):
            self.lastdir = path.dirname(file)
            self.data = prs.top_parse(file)
            self.pList.clear()
            for i in self.data:
                title = i.title_dump() if i.title_dump() != "" else "No name avaliable"
                self.pList.addItem(title)

    def pdownload(self, *arg):
        """Download .top file"""
        file, type = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save File", self.lastdir, "TOP Files (*.top);;All Files (*)"
        )
        if file != "":
            outputfile = path.join(self.tempDir, "workfile.top")
            if isfile(outputfile):
                try:
                    copyfile(outputfile, file)
                except IOError:
                    dialog = AlertWindow(self.topdir, "Cannot open file")
                    dialog.exec_()
            else:
                dialog = AlertWindow(
                    self.topdir,
                    "There is no top \
file to download",
                )
                dialog.exec_()

    def plistselect(self, index):
        """Select plot to draw"""
        data = self.data[index].data_dump()
        self.pCanvas.axes.clear()
        for style in data.keys():
            for d in data[style]:
                self.pCanvas.axes.plot(d[:, 0], d[:, 1], linestyle=style, color="black")
        self.pCanvas.axes.set_title(self.data[index].title_dump())
        self.pCanvas.axes.set_xlabel(self.data[index].xlab_dump())
        self.pCanvas.axes.set_ylabel(self.data[index].ylab_dump())
        self.pCanvas.axes.grid()
        self.pInfo.setText("\n".join(self.data[index].description_dump()))
        legends = []
        for style, label in self.data[index].legends_dump().items():
            legends.append(
                mlines.Line2D([], [], color="black", linestyle=style, label=label)
            )
        if len(legends) > 0:
            self.pCanvas.axes.legend(handles=legends)
        self.pCanvas.draw()

    def ssetExec(self, *arg):
        """Set abci executable location"""
        file, type = QtWidgets.QFileDialog.getOpenFileName(
            self, "ABCI binary", self.lastdir, "All Files (*)"
        )
        if isfile(file) and access(file, X_OK):
            self.execLocation.setText(file)
            self.lastdir = path.dirname(file)

    def closeEvent(self, *arg):
        """Cleanup and close program"""
        if self.tempDir is not None:
            try:
                rmtree(self.tempDir)
            except FileNotFoundError:
                pass


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(
            self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        FigureCanvas.updateGeometry(self)


class AlertWindow(QtWidgets.QDialog):
    def __init__(self, topdir, message):
        super(AlertWindow, self).__init__()
        uic.loadUi(path.join(topdir, "ui", "alert.ui"), self)
        self.textBrowser.setText(message)


class ProgressWindow(QtWidgets.QDialog):
    def __init__(self, topdir, process, title=""):
        super(ProgressWindow, self).__init__()
        uic.loadUi(path.join(topdir, "ui", "progress.ui"), self)
        if title != "":
            self.setWindowTitle(title)
        self.topdir = topdir
        self.interrupt.clicked.connect(lambda: process.terminate())
        self.thread = CloneThread(process)
        self.thread.newline.connect(self.newline)
        self.thread.eof.connect(self.close)
        self.thread.start()
        self.closeEvent = lambda x: process.terminate()

    def newline(self, msg):
        self.output.addItem(msg)


class CloneThread(QtCore.QThread):
    newline = QtCore.pyqtSignal("PyQt_PyObject")
    eof = QtCore.pyqtSignal("PyQt_PyObject")

    def __init__(self, process):
        QtCore.QThread.__init__(self)
        self.proc = process

    def run(self):
        out = None
        while self.proc.poll() is None:
            out = self.proc.stdout.readline().decode().strip()
            self.newline.emit(out)
        self.eof.emit(out)
