import numpy as np
import os.path
import matplotlib._pylab_helpers
from matplotlib.backends.backend_pdf import PdfPages
import time

def is_number(x,VarName,**kwargs):
    assert type(VarName)==str, "VarName must be a string."
    default = kwargs.get('default',None)
    notes = kwargs.get("notes","")
    assert type(notes)==str, "notes must be a string."
    if (default is None):
        assert str(type(x)) in [
                "<class 'int'>",
                "<class 'float'>",
                "<class 'float32'>",
                "<class 'float64'>",
                "<class 'numpy.float'>",
                "<class 'numpy.float64'>"], \
            VarName + " must be an int, float, float32, float64, or numpy.float not "+str(type(x))+". " + notes
    else:
        assert str(type(default)) in [
                "<class 'int'>",
                "<class 'float'>",
                "<class 'float32'>",
                "<class 'float64'>",
                "<class 'numpy.float'>",
                "<class 'numpy.float64'>"], \
            "default must be an int, float, float32, float64, or numpy.float not "+str(type(default))+"."
        assert str(type(x)) in [
                "<class 'int'>",
                "<class 'float'>",
                "<class 'float32'>",
                "<class 'float64'>",
                "<class 'numpy.float'>",
                "<class 'numpy.float64'>"], \
            VarName + " must be an int, float, float32, float64, or numpy.float not "+str(type(x))+". Default is " + str(default) + ". " + notes

def save_figures(Destination,BaseFileName,params,ReturnPath=False,**kwargs):
    """

    """

    SubFolder = kwargs.get("SubFolder",time.strftime("%Y_%m_%d_%H%M%S")+"/")
    FilePath = Destination + SubFolder
    assert type(Destination) == str and Destination[-1] == "/", \
    	"Destination must be a string ending is '/'. Currently Destination = " + str(Destination)
    assert type(SubFolder) == str and SubFolder[-1] == "/", \
    	"SubFolder must be a string ending is '/'. Currently SubFolder = " + str(SubFolder)
    assert type(BaseFileName) == str, \
    	"BaseFileName must be a string. Currently BaseFileName = " + str(BaseFileName) + " of type " + str(type(BaseFileName))

    if not os.path.exists(FilePath):
        os.makedirs(FilePath)

        EmptyNotesDoc = open(FilePath+'/notes.txt','w')
        EmptyNotesDoc.write('[Created ' + SubFolder[:10].replace("_","/") + " at " + SubFolder[11:13] + ":" + SubFolder[13:15] + "." + SubFolder[15:17] + "]\n\n")

        paramString = "#"*30 +"\n" + "#"*11 + " Notes " + "#"*12 + "\n" + "#"*30 + "\n\n" + "\t\tNONE\n\n"
        paramString += "#"*30 +"\n" + "#"*9 + " Parameters " + "#"*9 + "\n" + "#"*30 + "\n\n"
        for key in params.keys():
            paramString += "\t\t" + key + ": " + str(params[key]) + "\n"
        paramString += "\n" + "#"*30
        EmptyNotesDoc.write(paramString)

        EmptyNotesDoc.close()

    figs = kwargs.get("figs",
    	[manager.canvas.figure for manager in matplotlib._pylab_helpers.Gcf.get_all_fig_managers()]
    	)

    SaveAsPDF = kwargs.get("SaveAsPDF",False)
    assert type(SaveAsPDF)==bool, "SaveAsPDF must be either True or False."

    i = 1
    FileName = BaseFileName + "_" + "{:0>2d}".format(i) + "-01.jpg"
    if os.path.exists(FilePath + FileName) == True:
    	while os.path.exists(FilePath + FileName) == True:
    		i += 1
    		FileName = BaseFileName + "_" + "{:0>2d}".format(i) + "-01.jpg"

    for i in range(len(figs)):
    	figs[i].savefig(FilePath + FileName[:-6] + "{:0>2d}".format(i+1) + ".jpg")

    if SaveAsPDF == True:
    	PDFFileName = FileName[:-7] + ".pdf"
    	assert not os.path.exists(FilePath + PDFFileName), \
    			("Error with naming file. "
    			+ PDFFileName
    			+ " should not already exist as "
    			+ FileName
    			+ " does not exist. Try renaming or deleting "
    			+ PDFFileName
    			)

    	PDFFile = PdfPages(FilePath + PDFFileName)
    	if len(figs)==1:
    		PDFFile.savefig(figs[0])
    	else:
    		[PDFFile.savefig(fig) for fig in figs]
    	PDFFile.close()

    if ReturnPath==True:
        return(FilePath)
