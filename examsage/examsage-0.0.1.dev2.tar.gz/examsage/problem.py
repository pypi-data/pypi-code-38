########################################################################3456789
########################################################################72
from pathlib import Path # For manuplating filesystem paths
import shutil # For copying directories
import subprocess  # For calling OS processes like LaTeX
import importlib.util # For importing the user defined methods
from wand.image import Image as WImage  # For converting PDFs to an image
from string import ascii_uppercase as uppercase

# Only needed for the Problem.publish() method
from pylatex import Document, Command, Package, UnsafeCommand
from pylatex.base_classes import Arguments, Options
from pylatex.utils import NoEscape

from examsage.pyvars import PyVars

class Problem(Document):
    r"""A problem written in LaTeX with randomly generated parameters.

    Problem objects must have two configuration files in the source
    directory. The file 'body.tex' contains the LaTeX template of the
    problem. The file 'parameter.py' contains a class definition for
    generating variables for the LaTeX template.

    Attributes
    ----------
    parameters : Parameters object
        Generates the problem parameters and TeX
    name : pathlib.Path object
        The name of the problem matches the parent directory of the
        config files.
    points_tex : str in LaTeX format
        LaTeX marcos representation of the points list
    body : str in LaTeX format
        The configureation file `body.tex`.
    tex : str in LaTex format
        LaTeX representation of the problem to be embedded inside a LaTeX
        document environment.

    """

    content_separator = '\n'
    tex_packages = ('standalone',
                    'assessments',
                    'mathexam',
                    'mathdiagrams',
                    'pythontex',
                   )

    def __init__(self, source, points=None,):
        r"""
        Parameters
        ----------
        source : str
            The directory containing the config files for the problem
        points : list of ints or floats, optional
            Point values for the different parts of the problem.
            The default point value is the corresponding list index.

        """

        super().__init__(
            documentclass='standalone',
            document_options=['class=article', 'varwidth=false', 'crop=false'],
            geometry_options={'left':'0.5in', 'right':'0.5in', 'top':'1in', 'bottom':'1in'},
            indent=False,
        )
        for name in Problem.tex_packages:
            self.packages.append(Package(name))

        self.source = source
        self.points = points
        self.assessment = None

        # Create the parameters generator
        self.parameters = self.get_parameters()

        self.version = -1

    #@property
    #def version(self):
    #    if self.assessment:
    #        return self.assessment.version
    #    else:
    #        print("This problem must be appended to an instance of ExamSage.Assessment in order to have a version number.")

    def dumps(self):
        # Delete the old content
        self.clear()
        # Update the problem
        self.append(self.points_tex)
        # Ensure that enough versions have been generated
        versions = self.parameters.versions
        while len(versions) <= self.version:
            next(self.parameters)
        parameters = versions[self.version]
        self.append(NoEscape(parameters))
        self.append(NoEscape(self.body))

        return super().dumps()

    def dumps_content(self):
        # Delete the old content
        self.clear()
        # Update the problem
        self.append(self.points_tex)
        # Ensure that enough versions have been generated
        versions = self.parameters.versions
        while len(versions) <= self.version:
            next(self.parameters)
        parameters = versions[self.version]
        self.append(NoEscape(parameters))
        self.append(NoEscape(self.body))

        return super().dumps_content()

    def generate_pdf(self, *args, instructor_key = False, **kwargs):
        # Delete the old content
        self.preamble.clear()

        # Set the key flags
        if instructor_key:
            self.preamble.append(Command('setbool', Arguments('instructorKey', 'true')))
            self.preamble.append(Command('setbool', Arguments('studentKey', 'true')))
        else:
            self.preamble.append(Command('setbool', Arguments('instructorKey', 'false')))
            self.preamble.append(Command('setbool', Arguments('studentKey', 'false')))

        super().generate_pdf(*args, **kwargs)

    @property
    def source(self):
        return self.__source

    @source.setter
    def source(self, source):
        # Ensure that the problem exists
        source = Path(source)
        if source.exists():
            self.__source = source
        else:
            raise Exception(
                "Problem does not exist. Try running "
                + "examsage.Problem.new('path_to_new_problem')")
            return 1

    @property
    def name(self):
        # Return the parent directory
        return self.source.stem

    @property
    def points(self):
        return self.__points

    @points.setter
    def points(self, points):
        # Identify the required number of point values
        point_length = self.body.count('\py{points')

        if not points:
            # For testing, its helpful assigned point values their index
            points = range(point_length)

        # Ensure that the len(points) is correct
        if point_length != len(points):
            raise Exception(f"The list of point values for '{self.name}' "
                            + f"must have exactly {point_length} elements")

        self.__points = points

    @property
    def points_tex(self):
        keys = []
        values = []
        for index, value in enumerate(self.points):
            keys.append(f'points{uppercase[index]}')
            unit = 'points' if value != 1 else 'point'
            values.append(f"'({value} {unit})'")

        return PyVars(**dict(zip(keys, values)))

    @property
    def body(self):
        """A string returned, without modification, by _latex_item_to_string"""

        with open(self.source / 'body.tex', 'r') as f:
            body = f.read()
        return body

    def get_parameters(self):
        """Return an instance of the Parameters class defined in the source folder."""

        source = self.source
        module_name = 'parameters'
        module_file_path = source / (module_name + '.py')
        # Create an instance of the parameters class in source/parameters.py
        try:
            # Import the module
            module_spec = importlib.util.spec_from_file_location(
                module_name,
                module_file_path,
            )
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            # Import the class definition
            Parameters = getattr(module, 'Parameters')
            return Parameters()
        except Exception as err:
            print(self.__class__)
            print("Failed to create Parameter object <------------- FAILED")
            print("Problem path is " + str(source))
            print(err)
            print("\n")

    def __next__(self):
        # Generate a similar problem
        next(self.parameters)
        return self

    ########### Rewrite for compatibility with pyLaTeX
    @classmethod
    def new(cls, destination, overwrite=False): # <------------ OUTDATED 20190521
        """Copy the default problem to the destination."""

        # Ensure that the problem does not already exist
        destination = Path(destination)
        if destination.exists():
            if overwrite:
                shutil.rmtree(destination)
                print("Existing problem replaced")
            else:
                raise Exception("Problem already exist at " + str(destination))

        try:
            source = Path(cls.__path__[0]) / 'default_problem'
            shutil.copytree(source, destination)
        except Exception as err:
            print(cls)
            print("Failed to create new problem at "
                  + str(destination)
                  + "<---------------- FAILED")
            print(err)
            print("\n")

    def preview(self, resolution=100, compression=99):
        path = self.dest / (self.name + ".pdf")
        try:
            # Convert the PDF into an image
            with WImage(filename=str(path), resolution=resolution) as image:
                image.compression_quality = compression
                #image.save(filename=str(pbm.dest / (pbm.name + ".jpg")))
                img = image.clone()
        except Exception as err:
            print("Error: PDF not coverted. Does the PDF exist?")
            print(f"Path to PDF: {path}")
            print(err)
            print("\n")

        return img