# # # # # # # # # # # # # # # # # # # # # # # # # #
# Individual Based Model class
# Based on: Kattwinkel & Reichert, EMS 2017.
#
# Jonas Sukys
# Eawag, Switzerland
# jonas.sukys@eawag.ch
# All rights reserved.
# # # # # # # # # # # # # # # # # # # # # # # # # #

import os, re
import numpy
import pandas
#from copy import deepcopy as copy

from spux.models.model import Model

from spux.drivers import java
from spux.io import parameters as txt
from spux.utils.annotate import annotate
from spux.io.loader import read_types_of_keys
from ..io.report import report

class IBM (Model): #(object)
    """Individual Based Model class with java interface."""

    # construct IBM for the specified 'config'
    def __init__(
        self,
        config,
        classpath=None,
        jvmpath=None,
        jvmargs="-Xmx1G",
        paramtypefl=None,
        initial=None
    ):
        """Construct IBM for the specified 'config'."""

        self.initial = initial

        # kick-out
        if paramtypefl is None:
            raise ValueError("Fatal. Input file with parameters types is mandatory.")

        #find name of input files
        fullfile = os.path.join('input/input/',config)
        #
        keys = ["fNameInputUniParam","fNameInputTaxParam","fNameInputTaxNames"]
        self.infls = []
        with open (fullfile, 'r') as fl:
            for line in fl:
                if re.match(keys[0],line) or re.match(keys[1],line):
                    self.infls.append( ((line.split(':')[1]).strip('\n')).strip('\t') )
                elif re.match(keys[2],line):
                    specsfl = ( (line.split(':')[1]).strip('\n') ).strip('\t')

        #get name of species (labels)
        fullfile = os.path.join('input/input/',specsfl)
        with open(fullfile, 'r') as fl:
            next(fl)
            self.species = [ line.strip('\n') for line in fl ]

        #get parameters types
        self.paramtypefl = paramtypefl
        self.model_params = read_types_of_keys(infl=paramtypefl)

        #check parameters names
        for i in range(len(self.infls)):
            fullfile = os.path.join('input/input/',self.infls[i])
            with open(fullfile) as fl:
                next(fl) #first line is not a paramter
                for line in fl:
                    (key, val) = line.split()
                    if key not in self.model_params:
                        raise ValueError("Fatal. Parameter {} is not in file {}.".format(key,paramtypefl))

        self.config = config

        # Java Virtual Machine arguments
        self.jvmpath = jvmpath
        self.classpath = classpath
        self.jvmargs = jvmargs

        # initially neither interface nor model do exist
        self.interface = None
        self.model = None

        # sandboxing
        self.sandboxing = 1

        # serialization
        self.serialization = 'binary'

    # setup driver
    def driver (self):
        """Setup java driver (interface to user java code)."""

        # start Java Virtual Machine
        report (self, 'driver -> jvm')
        driver = java.Java (jvmpath=self.jvmpath, classpath=self.classpath, jvmargs=self.jvmargs)

        # get model class
        report (self, 'driver -> model')
        self.Model = driver.get_class("mesoModel.TheModel")

        # construct ModelWriterReader object for later save/load
        report (self, 'driver -> interface')
        Interface = driver.get_class("mesoModel.ModelWriterReader")
        self.interface = Interface()

    # initialize IBM using specified 'inputset' and 'parameters'
    def init (self, inputset, parameters):
        """Setup IBM using specified 'inputset' and 'parameters'."""

        # base class 'init (...)' method
        Model.init (self, inputset, parameters)

        if hasattr(self.initial,'draw'):
            inivals = self.initial.draw (self.rng)
            self.inivals = inivals
            # generate random initial values for nInitm2
            if self.verbosity >= 2:
                print ('Initial values:')
                print (inivals)

        #ugly patch to another refactoring problem
        self.sandbox.template = 'input'
        self.sandbox.copyin ()

        path = os.path.join(self.sandbox(), "input")
        #update parameter values in model input file
        for filename in self.infls:
            inputfile = os.path.join(path, filename)
            available = txt.load(inputfile)
            if hasattr(self.initial,'draw'):
                parini = pandas.Series.append(inivals, parameters)
            else:
                parini = parameters
            for label, value in parini.items():
                if label in available:
                    if self.model_params[label].lower() == 'double' or self.model_params[label].lower() == 'float':
                        available [label] = float([value] [0])
                    elif self.model_params[label][0:3].lower() == 'int':
                        available [label] = round([value] [0])
                    elif self.model_params[label].lower() == 'binary':
                        if [value] [0] != 0 or [value] [0] != 1:
                            raise ValueError("Fatal. Wrong value for binary parameter.")
                        available [label] = round([value] [0])
                    else:
                        raise ValueError("Fatal. Wrong type for parameter.")
            txt.save(available, inputfile, delimiter="\t")

        # setup driver
        self.driver ()

        # construct model object - set self.model to the java Model
        report (self, 'init -> model')
        self.model = self.Model (numpy.ndarray.tolist(self.seed()))

        # isolate model
        report (self, 'init -> isolate')
        self.model.setPaths (self.sandbox())

        # run model initialization for the specified 'config'
        report (self, 'init -> initModel')
        try:
            self.model.initModel ([self.config])
        except:
            raise ValueError("Caught the runtime exception on java.")

        # simulation initialization
        report (self, 'init -> initSimulation')
        self.model.initSimulation()

        # run initial simulation
        report (self, 'init -> runSimulationInitExtPartFiltering')
        self.model.runSimulationInitExtPartFiltering()

    # run IBM up to specified time and return the prediction
    def run (self, time):
        """Run IBM up to specified time and return the prediction."""

        # base class 'init ()' method
        Model.run (self, time)

        # set seed - pass array of seeds to Java source code
        report (self, 'run -> reinitiliazeModel')
        self.model.reinitializeModel ( numpy.ndarray.tolist(self.seed()) )

        # run model up to specified time
        report (self, 'run -> runModelExtPartFiltering')
        self.model.runModelExtPartFiltering(int(time))

        # get model output
        observation = self.model.observe()
        observation = numpy.array (observation)
        sums = numpy.sum (observation, axis=0)

        cf = 0.15*0.15*4 #correction factor (simulated area versus measurement area)
        sumsc = sums * cf
        tobs = numpy.append(sums,sumsc)

        labels = self.species[:]
        scaled_labels = [s + '_scaled' for s in labels]
        for i in scaled_labels:
            labels.append(i)

        if hasattr(self,'inivals'):
            tobs = numpy.append(tobs,self.inivals.values)
            for i in self.inivals.keys():
                labels.append(i)

        return annotate(tobs,labels,time)

    # save current model state
    def save (self):
        """Save current model state (the whole java program instance is saved)."""

        report (self, 'save')

        if self.serialization == "binary":
            buff = self.interface.writeModelByteArray (self.model)
            state = java.Java.save(buff)

        return state

    # load specified model state
    def load (self, state):
        """Load model state (the whole java program instance) previously saved with save()."""

        report (self, 'load')

        # setup driver
        self.driver ()

        # - binary array representing serialized model state (fast)
        if self.serialization == "binary":
            buff = java.Java.load(state)
            self.model = self.interface.loadModelByteArray(buff)

        #ugly patch to another refactoring problem
        self.sandbox.template = 'input'
        self.sandbox.copyin ()

        # isolate model
        self.sandbox.template = 'input'
        self.sandbox.copyin ()
        report (self, 'load-isolate')
        self.model.setPaths (self.sandbox())

    # construct a data container for model state with a specified size
    def state (self, size):
        """Construct a data container for model state with a specified size."""

        return numpy.empty (size, dtype="uint8")
