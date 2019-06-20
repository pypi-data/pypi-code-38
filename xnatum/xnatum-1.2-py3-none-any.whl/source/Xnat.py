import xnat as xnatpy
import os
import sys
from .util import tmp_zip
import dicom2nifti
import shutil


class Xnat:
    def __init__(self, server, user, password):
        self.server = server
        self.user = user
        self.password = password
        self.__prearc_session = None
        self.__connect()

    def __connect(self):
        """Connects to the Xnat instance and saves the connection."""
        self.session = xnatpy.connect(
            self.server, user=self.user, password=self.password
        )

    def get_subject_info(self, lproject, lsubject):
        """
        Returns all the info from a specific subject in a project.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID

        Returns
        -------
        object
            All the info from a subject, including the custom variables.
        """
        project = self.session.projects[lproject]
        try:
            subject = project.subjects[lsubject]
            return vars(subject)
        except:
            return "The subject was not found in the project."

    def list_projects(self):
        """
        List all the projects on a Xnat instance

        Extended description of function.

        Returns
        -------
        array(str)
            All the projects
        """
        projects = []
        for project in self.session.projects.values():
            projects.append((project.id, project.name))
        return projects

    def download_ml_data(self, lproject):
        """
        Downloads the data within a Xnat project with specific focus on Machine Learning.
        The experiments inside a subject must be labeled as TRAIN or TEST. 
        This function will download it to a Train folder or Test folder depending on that label.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        [str, str]
            Downloads data and returns an array with the train folder path and the test folder path.
        """
        project = self.session.projects[lproject]
        train_dir = os.path.expanduser(lproject + "/TRAIN")
        test_dir = os.path.expanduser(lproject + "/TEST")

        if not os.path.exists(train_dir):
            os.makedirs(train_dir)
        if not os.path.exists(test_dir):
            os.makedirs(test_dir)
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                print("Downloading ", experiment)
                if experiment.label.find("TRAIN") != -1:
                    experiment.download_dir(train_dir)
                else:
                    experiment.download_dir(test_dir)
        return [train_dir, test_dir]

    def get_train_data(self, lproject):
        """
        Returns the train data within a project.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        object
            All train data.
        """
        project = self.session.projects[lproject]
        trainData = []
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                if experiment.label.find("TRAIN") != -1:
                    trainData.append(experiment)
        return trainData

    def get_test_data(self, lproject):
        """
        Returns the test data within a project.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        object
            All test data.
        """
        project = self.session.projects[lproject]
        testData = []
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                if experiment.label.find("TEST") != -1:
                    testData.append(experiment)
        return testData

    def download_subject_sessions(self, lproject, lsubject):
        """
        Downloads subject sessions to a local folder

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID

        Returns
        -------
        [str]
            Returns the downloaded session names
        """
        project = self.session.projects[lproject]
        subject = project.subjects[lsubject]
        download_dir = os.path.expanduser(lproject)
        print("Using {} as download directory".format(download_dir))
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        for experiment in subject.experiments.values():
            print("Downloading ", experiment)
            experiment.download_dir(download_dir)
        session = [x.label for x in subject.experiments.values()]
        return session

    def download_single_session(self, lproject, lsubject, lsession):
        """
        Downloads a single subject session to a local folder

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID
        lsubject : str
            Session label

        Returns
        -------
        [str]
            Returns the downloaded session name
        """
        project = self.session.projects[lproject]
        subject = project.subjects[lsubject]
        download_dir = os.path.expanduser(lproject)
        print("Using {} as download directory".format(download_dir))
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        for experiment in subject.experiments.values():
            if(experiment.label == lsession):
                print("Downloading ", experiment)
                experiment.download_dir(download_dir)
        return lsession
    
    def download_single_subject_session_to_directory(self, lproject, lsubject, lsession, ldirectory):
        """
        Downloads a single subject session to a specific folder

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID
        lsubject : str
            Session label
        ldirectory: str
            Valid system path where to download the sessions

        Returns
        -------
        [str]
            Returns the downloaded session name
        """
        project = self.session.projects[lproject]
        subject = project.subjects[lsubject]
        download_dir = os.path.expanduser(ldirectory)
        print("Using {} as download directory".format(download_dir))
        for experiment in subject.experiments.values():
            if(experiment.label == lsession):
                print("Downloading ", experiment)
                experiment.download_dir(download_dir)
        return lsession

    def download_subject_sessions_to_directory(self, lproject, lsubject, ldirectory):
        """
        Downloads subject sessions to a specific folder

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID
        ldirectory: str
            Valid system path where to download the sessions

        Returns
        -------
        [str]
            Returns the downloaded session names
        """
        project = self.session.projects[lproject]
        subject = project.subjects[lsubject]
        download_dir = os.path.expanduser(ldirectory)
        print("Using {} as download directory".format(download_dir))
        for experiment in subject.experiments.values():
            print("Downloading ", experiment)
            experiment.download_dir(download_dir)
        session = [x.label for x in subject.experiments.values()]
        return session

    def get_subject_sessions(self, lproject, lsubject):
        """
        Returns a subject sessions without the need to downlaod them locally

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID
        lsubject : str
            Subject ID

        Returns
        -------
        object
            Returns the sessions object.
        """
        project = self.session.projects[lproject]
        subject = project.subjects[lsubject]
        return subject.experiments.values()

    def get_list_subjects(self, lproject):
        """
        Returns a list of subjects within a project.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        [str]
            Returns list of subjects within a project.
        """
        project = self.session.projects[lproject]
        return project.subjects

    def download_project_sessions(self, lproject):
        """
        Downloads all sessions from a project.

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        str
            Returns the directory where the data was downloaded.
        """
        project = self.session.projects[lproject]
        download_dir = os.path.expanduser(lproject)
        print("Using {} as download directory".format(download_dir))
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                print("Downloading ", experiment)
                experiment.download_dir(download_dir)
        return download_dir

    def download_project_sessions_to_directory(self, lproject, ldirectory):
        """
        Download all sessions from a project to a specific directory

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        str
            Returns the directory where the data was downloaded.
        """
        project = self.session.projects[lproject]
        download_dir = os.path.expanduser(ldirectory)
        print("Using {} as download directory".format(download_dir))
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                print("Downloading ", experiment)
                experiment.download_dir(download_dir)
        return download_dir

    def get_project_sessions(self, lproject):
        """
        Returns all the sessions from a project without the need to downlaod them locally

        Extended description of function.

        Parameters
        ----------
        lproject : str
            Project ID

        Returns
        -------
        object
            Sessions from a project
        """
        project = self.session.projects[lproject]
        allexperiments = []
        for subject in project.subjects.values():
            for experiment in subject.experiments.values():
                allexperiments.append(experiment)
        return allexperiments

    def convert_dicom_nifti(self, dicom_directory, output_folder):
        """
        Convers DICOM files to the Nifti format with anonymization.

        Extended description of function.

        Parameters
        ----------
        dicom_directory : str
            The DICOM file path
        output_folder : str
            The output folder
        """
        dicom2nifti.convert_directory(
            dicom_directory, output_folder, compression=True, reorient=True
        )

    def import_resource(self, obj, subdir, files):
        """
        Function to import resources
        """
        for file in files:
            filename = os.path.basename(file)
            uri = "{}/resources/{}/files/{}".format(obj.uri, subdir, filename)
            self.session.put(uri, files={"file": open(file, "rb")})

    def send_sequence(
        self, project, subject, sequence_dir, session="", destination="/prearchive"
    ):
        """
        Function to send a specific sequence to Xnat.
        """
        zipfname = tmp_zip(sequence_dir)
        try:
            self.__prearc_session = self.session.services.import_(
                zipfname,
                overwrite="append",
                project=project,
                subject=subject,
                experiment=subject + "_" + session,
                destination=destination,
                trigger_pipelines=False,
            )
        except:
            print("Unexpected error during XNAT import:")
            print(sys.exc_info())
        os.remove(zipfname)

    def send_session(self, project, subject, session_dir, sequences=None, session=""):
        """
        Function to send a complete session to Xnat.
        """
        if not sequences:
            sequences = os.listdir(session_dir)

        dest = "/prearchive"
        for (n, sequence) in enumerate(sequences):
            print("[{:02d}] Sending: {}".format(n + 1, sequence))
            sequence_dir = os.path.join(session_dir, sequence)
            self.send_sequence(
                project, subject, sequence_dir, session=session, destination=dest
            )
            dest = self.__prearc_session.uri

        self.__prearc_session.archive()
        self.__prearc_session = None

        print("Finished!")
