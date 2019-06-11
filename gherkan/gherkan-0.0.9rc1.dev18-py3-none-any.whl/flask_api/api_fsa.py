import atexit
import datetime
import importlib
import logging
import logging.handlers
import queue
import os
import re

import yaml
from flask import send_file

from gherkan.containers.NLPModelManager import NLPModelManager
from .raw_text_to_signal import nl_to_signal as nlToSignal
from .signal_to_nl import signal_to_nl as signalToNL
from .signal_to_negated_signal import signal_to_negated_signal as signalToNegatedSignal
from gherkan.processing.SignalMapper import SignalMapper
from gherkan.speech_recognition.paid_speech_to_text import transcribe as speechToText

DEBUG_MODE = False


class API_FSA():
    """
    FSA class for tracking state from REST API. State is written into a file
    so it should be persistent even over long time periods.
    """

    # =====>>> PATH variables <<<===== #
    stateFilePath = 'state.fsa'  # file to store the current state (see S_* variables)
    configFilePath = 'fsa_config.yaml'  # (editable) configuration file

    # This path does not need to be set to the package's root, probably
    rootFolder = importlib.util.find_spec("gherkan").submodule_search_locations[0]  # the package's root folder

    dataFolder = os.path.join(rootFolder, 'data')  # folder with received and processed files (inp/out files)
    audioFolder = os.path.join(dataFolder, 'audio')  # folder with audio files

    robotProgramsPath = os.path.join(rootFolder, 'utils', 'RobotPrograms_{}.json')  # template of the path to the robot programs
    signalMappingsPath = os.path.join(rootFolder, 'utils', 'signal_mappings_{}.json')  # template of the path to the robot programs

    language = 'en'

    # NLP model manager
    nmm = None

    # =====>>> STATE constants <<<===== #
    # State is stored as 2 bytes in the state.fsa binary file
    S_OFF = 0
    S_IDLE = 1
    S_RECEIVED_NL_TEXT = 2
    S_CORRECTING_NL_TEXT = 4
    S_FINISHED_PROCESSING_NL_TEXT = 8
    S_RECEIVED_SIGNAL = 16
    S_FINISHED_PROCESSING_SIGNAL = 32
    S_RECEIVED_AUDIO = 64
    S_CORRECTING_AUDIO = 128
    S_FINISHED_PROCESSING_AUDIO = 256
    S_SIGNAL_MAPPING_EXISTS = 512
    S_ERROR = 1024

    # This is for debugging
    STATES = ["S_IDLE", "S_RECEIVED_NL_TEXT", "S_CORRECTING_NL_TEXT", "S_FINISHED_PROCESSING_NL_TEXT", "S_RECEIVED_SIGNAL", "S_FINISHED_PROCESSING_SIGNAL", "S_RECEIVED_AUDIO", "S_CORRECTING_AUDIO", "S_FINISHED_PROCESSING_AUDIO", "S_SIGNAL_MAPPING_EXISTS", "S_ERROR"]

    # =====>>> PARAMETER name constants <<<===== #
    P_LAST_SIGNAL_FILE = "lastSignalFile"
    P_LAST_NL_TEXT_FILE = "lastNLTextFile"
    P_LAST_AUDIO_FILE = "lastAudioFile"
    P_RESPONSE_MODE = "responseMode"  # response mode for the processed text, see parameter VALUES

    # =====>>> parameter VALUES <<<===== #
    PV_RESPONSE_FILE = "responseModeFile"  # sends back a file
    PV_RESPONSE_JSON = "responseModeJSON"  # sends back a JSON

    # =====>>> OTHER <<<===== #
    basenameExtractorRegex = re.compile(r"(?P<basename>.+?)(?P<rest>(_signals|\.)+.+)")
    IS_SET_UP = False

    # =====>>> Helper STATIC methods <<<===== #
    @staticmethod
    def toBytes(integer):
        # Maybe extend this with a loop but so far 1024 as the limit is ok
        return bytes([(0b11100000000 & integer) >> 8, 0b11111111 & integer])

    @staticmethod
    def fromBytes(byte):
        # Maybe extend this with a loop but so far 1024 as the limit is ok
        return (byte[0] << 8) | byte[1]

    @staticmethod
    def generateDatestring():
        return datetime.datetime.now().strftime('%Y_%b_%d-%H_%M_%S')

    # =====>>> Helper CLASS methods <<<===== #

    @classmethod
    def states2str(cls):
        with open(cls.stateFilePath, 'rb') as statefile:
            state = cls.fromBytes(statefile.read())
        return [cls.STATES[i] for i in range(10) if (2**i) & state]

    @classmethod
    def getState(cls):
        with open(cls.stateFilePath, 'rb') as statefile:
            state = cls.fromBytes(statefile.read())
        logging.debug("FSA> Requested state: {}", state)
        states = cls.states2str()
        logging.debug("FSA> Current states:\n\t{}", states)
        return state

    @classmethod
    def setState(cls, state):
        logging.debug("FSA> Setting state to: {}", state)
        states = [cls.STATES[i] for i in range(10) if (2**i) & state]
        logging.debug("FSA> Current states:\n\t{}", states)
        if isinstance(state, int):
            state = cls.toBytes(state)
        with open(cls.stateFilePath, 'wb') as statefile:
            statefile.write(state)

    @classmethod
    def addState(cls, state):
        """ Adds a state to the FSA
        This method should be preferred instead of the "setState" method
        """
        currentState = cls.getState()
        if state > cls.S_IDLE:
            currentState &= ~cls.S_IDLE
        cls.setState(currentState | state)

    @classmethod
    def removeState(cls, *states):
        """ Removes a state from the FSA
        This method should be preferred instead of the "setState" method.
        Multiple states can be removed at once
        This methods, however, cannot be used to set the state to S_OFF.
        """
        nextState = cls.getState()
        for state in states:
            nextState &= ~state
        if nextState < cls.S_IDLE:
            nextState |= cls.S_IDLE
        cls.setState(nextState)

    @classmethod
    def getConfig(cls, param=None):
        with open(cls.configFilePath, 'r', encoding="utf-8") as cfg:
            config = yaml.full_load(cfg)
            if param is not None:
                try:
                    value = config[param]
                except Exception as e:
                    value = None
        logging.debug("FSA> Requested value of configuration parameter: {} = {}", param, value)
        return value

    @classmethod
    def setConfig(cls, param, value):
        with open(cls.configFilePath, 'r', encoding="utf-8") as cfg:
            config = yaml.full_load(cfg)
        config[param] = value
        with open(cls.configFilePath, 'w', encoding="utf-8") as cfg:
            yaml.dump(config, cfg)
        logging.debug("FSA> Setting configuration parameter: {} = {}", param, value)
        logging.debug("Configuration yaml file:\n\t{}", str(config))

    @classmethod
    def regenerateConfig(cls):
        logging.debug("FSA> Regenerating configuration file")
        with open(cls.configFilePath, 'w', encoding="utf-8") as cfg:
            # TODO: add more defaults to config
            yaml.dump({"flush": False, "responseMode": "responseModeFile"}, cfg)

    # =====>>> API initialization <<<===== #
    @classmethod
    def setup(cls, debugMode=False):
        """This function sets up the the paths and logging

        Parameters
        ----------
        debugMode : bool, optional
            This enforces the logging system to output the logging messages as well (the default is False, which [default_description])
        """

        global DEBUG_MODE
        if not DEBUG_MODE:  # Manually setting DEBUG_MODE to True overrides the setting requested via the API
            DEBUG_MODE = debugMode

        # Check if the root folder is set correctly
        if not os.path.isdir(cls.rootFolder):
            raise Exception("The root folder is set to a non-existent path!\nRoot folder: {}".format(cls.rootFolder))
        if not os.access(cls.rootFolder, os.W_OK):
            raise Exception("Cannot write to the root folder!\nRoot folder: {}".format(cls.rootFolder))
        if not os.access(cls.rootFolder, os.R_OK):
            raise Exception("Cannot read from the root folder!\nRoot folder: {}".format(cls.rootFolder))

        # Check the existence of data folders
        if not os.path.isdir(cls.audioFolder):
            os.makedirs(cls.audioFolder)

        # > LOGGING <
        logging.captureWarnings(True)  # capture warnings

        class QFilter(logging.Filter):

            def filter(self, record):
                return hasattr(record, "type")

        class ConsoleFormatter(logging.Formatter):

            def __init__(self):
                self.default_msec_format = "%s.%03d"
                super().__init__(datefmt="%Y-%m-%d %H:%M:%S.uuu")
                self.oldFormatterRegex = re.compile(r"%\w+:")

            def format(self, record):
                template = "[{time}] *{severity}*: "
                if hasattr(record, "type"):
                    template = template + f"[{record.type}] {{message}}"
                else:
                    template = template + "{message}"

                if record.args:
                    if self.oldFormatterRegex.search(record.msg) is not None:
                        formattedMessage = record.msg % record.args
                    else:
                        formattedMessage = record.msg.format(*record.args)
                else:
                    formattedMessage = record.msg
                record.message = formattedMessage
                string = template.format(severity=record.levelname, time=self.formatTime(record), message=formattedMessage)

                if record.levelno >= logging.ERROR:
                    string += f"\nError occurred in file '{record.filename}' ({record.pathname}) in function '{record.funcName}' on line '{record.lineno}'. See the log file for more details."
                string += ""
                return string

        class NewStyleLR(logging.LogRecord):

            def __init__(self, name, level, pathname, lineno, msg, args, exc_info, func, sinfo):
                super().__init__(name, level, pathname, lineno, msg, args, exc_info, func, sinfo)
                self.oldFormatterRegex = re.compile(r"%\w")

            def getMessage(self):
                msg = str(self.msg)
                if self.args:
                    if self.oldFormatterRegex.search(msg) is not None:
                        msg = msg % self.args
                    else:
                        msg.format(*self.args)
                self.message = msg
                return msg

        logging.setLogRecordFactory(NewStyleLR)

        cls.logQueue = queue.Queue()  # Queue to put the log records into
        queueHandler = logging.handlers.QueueHandler(cls.logQueue)
        queueHandler.addFilter(QFilter())
        queueHandler.setFormatter(ConsoleFormatter())
        queueHandler.setLevel(logging.WARNING)

        consoleHandler = logging.StreamHandler()
        consoleHandler.setLevel(logging.DEBUG if DEBUG_MODE else logging.INFO)
        consoleHandler.setFormatter(ConsoleFormatter())

        fileHandler = logging.FileHandler(filename=os.path.join(cls.dataFolder, "log.txt"), encoding="utf-8")
        fileHandler.setLevel(logging.NOTSET)
        fileHandler.setFormatter(ConsoleFormatter())

        logging.basicConfig(handlers=[queueHandler, fileHandler, consoleHandler])
        rootLogger = logging.getLogger()  # get the root logger
        rootLogger.setLevel(0)  # the logger filters the records even before they get to handlers, so the level shall be set to lowest possible value

        if not os.path.isfile(cls.configFilePath):
            cls.regenerateConfig()

        cls.IS_SET_UP = True

    # =====>>> API initialization <<<===== #
    @classmethod
    def init_fsa(cls, address, port):
        if not cls.IS_SET_UP:
            raise Exception("The API FSA was not setup properly before initialization! Run API_FSA.setup() before init_fsa()!")
        # > Initialization <
        logging.info("The RESTful API to the Gherkan NL Instruction Processing system is starting...")

        logging.info("Host address: {}\nPort number: {}", address, port)
        cls.setConfig("host", address)
        cls.setConfig("port", port)

        logging.info("Checking done, checking state from previous run...")
        # Check for previous sessions
        if os.path.exists(cls.stateFilePath):
            previousState = cls.getState()
            # Check and handle error
            if previousState == cls.S_ERROR:
                if cls.getConfig('flush'):
                    logging.info("Found error state from a previous run.\nError flushing is set to True - flushing the error and reseting the system.")
                    previousState = cls.S_OFF
                    cls.regenerateConfig()
                else:
                    raise Exception("Previous run of the system resulted in an error! Resolve the error and set the fsa_config\nPlease, check the log file for details.")
            if previousState != cls.S_OFF:
                logging.info("Found non-OFF state from previous run, restoring the system with state {}", previousState)
                cls.setState(previousState)
            else:
                # Set state to ready/idle
                logging.info("System ready, state set to IDLE.")
                cls.setState(cls.S_IDLE)
        else:
            logging.info("System ready, state set to IDLE.")
            cls.setState(cls.S_IDLE)

        # Load NLP models (time-consuming operation)
        logging.info("Loading NLP models")

        cls.nmm = NLPModelManager()
        cls.nmm.load_all_models()

        # Register function that will shutdown the FSA when the server is terminated
        atexit.register(cls.finalize)

    @classmethod
    def finalize(cls):
        """Shuts down the FSA when the server (application) is terminated
        """

        logging.info("Shutting down FSA.")
        cls.setState(cls.S_OFF)
        logging.shutdown()

    # =====>>> RESTful API Call handling functions <<<===== #
    @classmethod
    def receiveSignal(cls, text):
        """This function handles the receiving of signal text.
        """

        state = cls.getState()
        if state & (cls.S_RECEIVED_AUDIO | cls.S_RECEIVED_NL_TEXT):
            raise Exception("Different data type already received!")

        if state & cls.S_RECEIVED_SIGNAL:
            signalFileMode = 'a'
            fileName = cls.getConfig(cls.P_LAST_SIGNAL_FILE)
        else:
            cls.addState(cls.S_RECEIVED_SIGNAL)
            signalFileMode = 'w'
            fileName = os.path.join(cls.dataFolder, '_'.join([cls.generateDatestring(), 'signals.feature']))
            cls.setConfig(cls.P_LAST_SIGNAL_FILE, fileName)

        with open(fileName, signalFileMode, encoding="utf-8") as sigFile:
            sigFile.writelines(text)

        cls.removeState(cls.S_SIGNAL_MAPPING_EXISTS)

        # Signal text can be iteratively written into the file
        # When all signals were written, the user can request NL file

    @classmethod
    def requestSignal(cls):
        """This function return a composed signal file derived from NL text, if it was provided
        """
        state = cls.getState()
        if state & cls.S_RECEIVED_SIGNAL:  # Signals were sent and requested back (e.g. to check the state of the file)
            return send_file(cls.getConfig(cls.P_LAST_SIGNAL_FILE))
        elif not (state & cls.S_FINISHED_PROCESSING_NL_TEXT):  # Check if NL text was sent and processed
            raise Exception("NL text was not provided, cannot return signal file!")

        signalFilePath = cls.getConfig(cls.P_LAST_SIGNAL_FILE)

        responseMode = cls.getConfig(cls.P_RESPONSE_MODE)
        if responseMode == cls.PV_RESPONSE_FILE:
            response = send_file(signalFilePath)
        elif responseMode == cls.PV_RESPONSE_JSON:
            with open(signalFilePath, "r", encoding="utf-8") as signalFile:
                signalText = signalFile.read()

            # TODO: Split file into response

            response = {
                "language": "en<OR>cs",
                "background": "background text",
                "description": "This feature is not implemented, yet! Use RESPONSE_MODE: FILE instead.",
                "scenarios": signalText
            }

        cls.removeState(cls.S_FINISHED_PROCESSING_NL_TEXT, cls.S_RECEIVED_NL_TEXT)
        return response

    @classmethod
    def requestRemappedSignal(cls):
        """This function return a remapped signal
        """
        state = cls.getState()
        if not state & (cls.S_RECEIVED_SIGNAL | cls.S_FINISHED_PROCESSING_NL_TEXT):
            Exception("NL text nor signal file was not provided, cannot return signal file!")

        if not state & cls.S_SIGNAL_MAPPING_EXISTS:
            return send_file(cls.getConfig(cls.P_LAST_SIGNAL_FILE))

        signalFilePath = cls.getConfig(cls.P_LAST_SIGNAL_FILE)

        path, filename = os.path.split(signalFilePath)
        remappedSignalFilePath = os.path.join(path, cls.basenameExtractorRegex.sub(r"\g<basename>_remapped\g<rest>", filename))
        
        signalMapper = SignalMapper()

        signalMapper.loadSignal(signalFilePath)  # load the signal file
        signalMapper.loadDictionary(cls.signalMappingsPath.format(cls.language))  # write the signal file
        signalMapper.encode()  # encode the signal with the loaded dictionary
        signalMapper.writeSignal(remappedSignalFilePath)

        response = send_file(remappedSignalFilePath)
        # cls.removeState(cls.S_FINISHED_PROCESSING_NL_TEXT, cls.S_RECEIVED_NL_TEXT)
        return response

    @classmethod
    def requestNegatedSignal(cls):
        """This function return the signal file with all the statements negated.
        """
        state = cls.getState()

        if not (state & cls.S_RECEIVED_SIGNAL):
            raise Exception("Signal file was not provided, cannot return negated signal file!")

        signal_file = cls.getConfig(cls.P_LAST_SIGNAL_FILE)

        outputFile = signalToNegatedSignal(signal_file, cls.nmm)

        cls.removeState(cls.S_RECEIVED_SIGNAL)

        responseMode = cls.getConfig(cls.P_RESPONSE_MODE)
        if responseMode == cls.PV_RESPONSE_FILE:
            response = send_file(outputFile)
        else:
            response = {"Message": "Response mode not implemented yet."}

        return response

    @classmethod
    def requestNLText(cls):
        state = cls.getState()
        if not (state & cls.S_RECEIVED_SIGNAL):
            raise Exception("Signal file was not provided, cannot return NL text!")

        signalFilePath = cls.getConfig(cls.P_LAST_SIGNAL_FILE)

        path, filename = os.path.split(signalFilePath)
        outputFile = os.path.join(path, cls.basenameExtractorRegex.sub(r"\g<basename>.feature", filename))

        logging.debug("Calling SignalToNL; associated file: {}", signalFilePath)
        signalToNL(signalFilePath, cls.nmm)

        cls.removeState(cls.S_RECEIVED_SIGNAL)

        responseMode = cls.getConfig(cls.P_RESPONSE_MODE)
        if responseMode == cls.PV_RESPONSE_FILE:
            response = send_file(outputFile)
        elif responseMode == cls.PV_RESPONSE_JSON:
            with open(outputFile, "r", encoding="utf-8") as nlTextFile:
                nlText = nlTextFile.read()

            response = {
                "language": "en<OR>cz",
                "description": "This feature is not implemented, yet! Use RESPONSE_MODE: FILE instead.",
                "background": "background/context text",
                "scenarios": nlText
            }
        else:
            response = {"Message": "Request mode is set to an incorrect value!"}
        return response

    @classmethod
    def receiveNLText(cls, data):
        state = cls.getState()
        if state & (cls.S_RECEIVED_SIGNAL | cls.S_RECEIVED_AUDIO):
            raise Exception("Different data type already received!")

        cls.addState(cls.S_RECEIVED_NL_TEXT)

        basepath = os.path.join(cls.dataFolder, cls.generateDatestring())
        nlFilePath = f"{basepath}.feature"
        signalFilePath = f"{basepath}_signals.feature"

        logging.debug("Calling nlToSignal; associated file: {}\nData: {}", basepath, data)
        cls.getLogs()  # this will empty any previous log messages, just in case
        nlToSignal(basepath, data, cls.nmm)
        logs = cls.getLogs()  # get log records generated while processing the NL text

        response = {
            "info": "Processing done",
            "lines": [],
            "error_lines": [],
            "error_hints": [],
            "errors": False
        }

        if len(logs) > 0:  # There were some problems while processing the text
            cls.removeState(cls.S_RECEIVED_NL_TEXT)
            response["info"] = "Some problems occurred while processing the NL text. Please correct the indicated problems and resubmit the text."
            response["errors"] = True
            for log in logs:
                response["error_lines"].append(log.message)
        else:
            cls.setConfig(cls.P_LAST_NL_TEXT_FILE, nlFilePath)
            cls.setConfig(cls.P_LAST_SIGNAL_FILE, signalFilePath)
            cls.addState(cls.S_FINISHED_PROCESSING_NL_TEXT)

        cls.removeState(cls.S_SIGNAL_MAPPING_EXISTS)

        return response

    @classmethod
    def receiveAudio(cls, audioPath, language):
        state = cls.getState()
        if state & (cls.S_RECEIVED_SIGNAL | cls.S_RECEIVED_NL_TEXT):
            raise Exception("Different data type already received!")

        if language == "en":
            lang = "en-US"
        elif language == "cs":
            lang = "cs-CZ"
        transcriptPath = '.'.join([audioPath[:audioPath.find(".")], "txt"])

        logging.debug("Calling speechToText; audio file: {}\nlanguage: {}", audioPath, lang)
        try:
            transcript = speechToText(audioPath, lang)
        except Exception as e:
            raise e

        logging.info(f"Audio transcript: {transcript}")
        logging.info(f"Saving transcript to {transcriptPath}")

        with open(transcriptPath, "w", encoding="utf-8") as tf:
            tf.writelines(transcript)

        return transcript

    @classmethod
    def requestRobotPrograms(cls, language):
        if not language:
            language = cls.language

        with open(cls.robotProgramsPath.format(language), 'r', encoding="utf-8") as robotProgramFile:
            robotPrograms = robotProgramFile.read()

        return robotPrograms

    @classmethod
    def receiveRobotPrograms(cls, programs, language):
        if not language:
            language = cls.language
        programs.save(cls.robotProgramsPath.format(language))
        programs.close()

    @classmethod
    def requestSignalMapping(cls, language):
        state = cls.getState()
        if not (state & (cls.S_RECEIVED_SIGNAL | cls.S_FINISHED_PROCESSING_NL_TEXT)):
            raise Exception("There is no signal file to extract the mapping from!")

        if not language:
            language = cls.language

        signalFilePath = cls.getConfig(cls.P_LAST_SIGNAL_FILE)  # get the last signal file

        signalMapper = SignalMapper()

        signalMapper.loadSignal(signalFilePath)  # load the signal file
        signalMapper.analyze()  # analyze it (get the signals)

        signalMapper.writeDictionary(cls.signalMappingsPath.format(language))  # write the signal file

        cls.addState(cls.S_SIGNAL_MAPPING_EXISTS)

        with open(cls.signalMappingsPath.format(language), 'r', encoding="utf-8") as signalMappingsFile:
            signalMappings = signalMappingsFile.read()  # the file is written and reread - not efficient but easier to code...

        return signalMappings

    @classmethod
    def receiveSignalMapping(cls, mapping, language):
        state = cls.getState()
        if not (state & cls.S_SIGNAL_MAPPING_EXISTS):
            raise Exception("Signal mapping was not created! First, request the signal mapping file then adjustment to the mapping can be made.")

        if not language:
            language = cls.language

        mapping.save(cls.signalMappingsPath.format(cls.language))
        mapping.close()

    # =====>>> RESTful API Helper functions <<<===== #
    @classmethod
    def getLogs(cls):
        logs = []
        while not cls.logQueue.empty():
            try:
                item = cls.logQueue.get(False)
            except queue.Empty:
                logging.exception("The logging queue was emptied for some reason (even though while not empty is used).")
            else:
                logs.append(item)
        return logs

    @classmethod
    def canRequestSignal(cls):
        """Checks whether it is possible to request a signal file.
        """
        state = cls.getState()
        return state & (cls.S_FINISHED_PROCESSING_NL_TEXT | cls.S_RECEIVED_SIGNAL)

    @classmethod
    def canRequestNegatedSignal(cls):
        """Checks whether it is possible to request a negated signal file.
        """
        state = cls.getState()
        return state & cls.S_RECEIVED_SIGNAL

    @classmethod
    def canRequestNLText(cls):
        """Checks whether it is possible to request a NL text file.
        """
        state = cls.getState()
        return state & cls.S_RECEIVED_SIGNAL
