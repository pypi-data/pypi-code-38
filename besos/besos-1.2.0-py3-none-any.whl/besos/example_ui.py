import os
import hublib.ui as ui
import ipywidgets as w
from IPython.display import display
import config

import eppy_funcs as ef
import sampling

from functools import partial


class FileManager:
    def __init__(self, extensions, dir=config.inDir, defaults=config.files, **kwargs):
        self.files = {}  # maps extension name to (current, {candidates}) tuples
        # defaults must already be in the directory
        for ext, file in defaults.items():
            if ext not in extensions:
                raise ValueError('{} is not a valid extension'.format(ext))
            self.files[ext] = (file, {file})
        self.directory = dir
        self.extensions = extensions
        self.out = w.Output()
        self.displayOptions()

        widgetDefaults = {'name': "Files", 'desc': '',
                          'maxsize': '10M', 'width': '30%', 'maxnum': 5}
        widgetDefaults.update(kwargs)

        multiLoader = ui.FileUpload(dir=dir, cb=self, **widgetDefaults)
        self.w = w.VBox([multiLoader.w, self.out])

    def __call__(self, w, fileNames):
        self.out.clear_output()
        badFiles = []
        with self.out:
            for name in fileNames:
                ext = name.split('.')[-1]
                name = self._short(name)
                if ext in self.extensions:
                    current, options = self.files.get(ext, ('File Needed', set()))
                    self.files[ext] = (name, options | {name})
                else:
                    badFiles.append(name)
            if badFiles:
                print(' and '.join([', '.join(badFiles[:-1]), badFiles[-1]]),
                      'are invalid files. Only files with the extensions',
                      ' or '.join([', '.join(self.extensions[:-1]), self.extensions[-1]]),
                      'are allowed')
        self.displayOptions()
        w.reset()

    def displayOptions(self):
        with self.out:
            for ext in self.extensions:
                current, options = self.files.get(ext, ('File Needed', ['File Needed']))
                dd = ui.Dropdown(name=ext + ' file', description='',
                                 value=current,
                                 options=options, cb=partial(self._setFile, ext=ext))
                display(dd)

    def _short(self, name):
        return name[len(self.directory) + 1:]

    def getFile(self, ext):
        # deliberetly does not catch key errors
        # might want to replace with __getitem__
        return os.path.join(self.directory, self.files[ext][0])

    def _setFile(self, w, file, ext):
        current, options = self.files[ext]
        self.files[ext] = (file, options)


fileTypes = ['building', 'idd', 'epw']
fm = FileManager(fileTypes)


def output(transformers):
    idf = None
    results = w.Output()

    def _getSamples(w):
        nonlocal idf
        global df
        if idf is None:
            idf = ef.get_idf(fm.getFile('building'), fm.getFile('idd'), fm.getFile('epw'))
        with results:
            print('Simulating...')
            df = sampling.dist_sampler(samplerType.value, transformers, samplesBox.value)
            df['energy use'] = ef.Evaluator(transformers, idf).df_apply(df)
            print('Done')

            display(df)
    goButton = w.Button(description='Get Samples')
    goButton.on_click(_getSamples)
    return w.VBox([goButton, results])


startButtons = w.HBox([ui.HideCodeButton().w, ui.RunAllButton().w])

samplerType = ui.Dropdown('Sampling method', '',
                          options={'Latin Hypercube': sampling.lhs,
                                   'Random': sampling.random,
                                   'LHS with minimax criterion': sampling.lhs_maximin,
                                   'Random, seeded': sampling.seeded_sampler},
                          value=sampling.lhs)

samplesBox = ui.Integer('Samples', value=5, min=1, max=20)

interface = w.VBox([fm.w, samplerType.w, samplesBox.w])
