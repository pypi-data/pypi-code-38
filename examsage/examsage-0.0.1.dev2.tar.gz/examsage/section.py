########################################################################3456789
########################################################################72
# Purpose: Defines a question class for writing TeX files with automatically generated parameters.
import os            # For handling OS objects (for example files)
import importlib     # For dynamically importing modules (without knowing the name until runtime)

class Question(object):
    # Methods
    def __init__(self, question):
        # Copy and delete the dictionary entries. Additional entries will be passed to the Parameters object
        self.path = question.pop('path', None)
        self.points = question.pop('points', None)
        self.spaces = question.pop('spaces', None)
        self.layout = ''
        self.par_file = ''

        # Load the parameters object for the associated question
        try:
            #For this import to work, sys.path must include the parent directory containing the Questions package
            temp_module = importlib.import_module(self.path.replace('/', '.'), package='examsage')
            try:
                Parameters = getattr(temp_module, 'Parameters')
            except Exception as err:
                print(self.__class__)
                print("getattr  FAILED <---------------- FAILED")
                print("Current directory is " + os.getcwd())
                print(self.path)
                print(err)
                print("\n")
        except Exception as err:
            print(self.__class__)
            print(self.path)
            print("importlib.import_module FAILED <---------------- FAILED")
            print("Current directory is " + os.getcwd())
            print("Question path is " + self.path)
            print(err)
            print("\n")

        # Pass any extra agruments to the parameters object
        try:
            self.parameters = Parameters(question)
        except:
            self.parameters = Parameters()

    def write_layout(self, problem_number):
        # Covert the self.point list into a TeX string
        pointsTeX = ''
        for j in range(len(self.points)):
            pointsTeX = pointsTeX + "\n" + r"""\def \points{0}{{{1}}}""".format(chr(ord('A') + j), self.points[j])

        # Covert the self.spaces list into a TeX string
        spacesTeX = ''
        for j in range(len(self.spaces)):
            spacesTeX = spacesTeX + "\n" + r"""\def \answerspace{0}{{{1}}}""".format(chr(ord('A') + j), self.spaces[j])

        ## Create the TeX lines for importing the parameters.TeX and question.TeX
        # Obtain the relative path of the TeX file for the question.
        TeXPath, temp = os.path.split(self.path)
        # Obtain the base name of the question. This is used to name the parameter file as well as identify the question.TeX file name.
        TeXBase = os.path.splitext(temp)[0]
        # Name of the file containing the parameters for the corresponding question
        self.par_file = problem_number + ".{0}.par".format(TeXBase)
        # Populate the TeX lines
        TeX_import_lines = r"""
\import{{\parametersLocation}}{{"{par_file_}"}}
\import{{\questionDir"{pathName_}/"}}{{"{baseName_}.tex"}}

""".format(par_file_ = self.par_file, pathName_ = TeXPath, baseName_ = TeXBase)

        # TeX for the Layout.tex file. Defines the point values, spacing, and locations of the parameters and question files
        self.layout = r"""
{points_}
{spacing_}
{import_lines_}
""".format(import_lines_ = TeX_import_lines, spacing_ = spacesTeX, points_ = pointsTeX)


    def get_parameters(self, layout_path, version):
        # Writes the parameters TeX file a saves it in the "version" folder

        # Create the directory to hold the parameter files for the given version
        version_path = os.path.join(layout_path, version)
        if not os.path.exists(version_path):
            try:
                os.makedirs(version_path)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        # Generate new parameters then write the parameters file.
        self.parameters.generate_parameters()
        with open(os.path.join(version_path, self.par_file), "w") as f:
            f.write(self.parameters.TeX)

class InsertImage(object):
    def __init__(self, image):
        self.path = image.pop('path', None)
        self.scale = image.pop('scale', None)
        self.layout = r"""
\vspace{{-1.5em}}
\begin{{center}}
    \includegraphics[scale={1}]{{\questionDir{0}}}
\end{{center}}
\vspace{{-1.5em}}
""".format(self.path, self.scale)

class NewPage(object):
    def __init__(self):
        self.layout = r"""\textbf{{\small Please continue on the next page.}}
\clearpage{}
"""

class Ztable(object):
    def __init__(self):
        self.layout = r"""
% If this is not a key, then include the z-table
\iftoggle{keyforInstr}{%pass
}{% else
    \iftoggle{key}{%pass
    }{% else
        \clearpage{}
        \includepdf[pages={1,2}]{\questionDir/Images/Ztable.pdf}
    }%
}% end \iftoggle
"""