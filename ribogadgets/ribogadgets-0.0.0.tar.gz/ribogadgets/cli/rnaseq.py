from .main import *
from ..rnaseq import *

@cli.group()
def rnaseq():
    """
    Display, set or delete RNA-Seq data 
    """
    pass


@rnaseq.command()
@click.argument('ribo', type = click.Path( ))
@click.option('--name',  
               help     = "experiment name", 
               type     = click.STRING , 
               required = True)
@click.option('--rnaseq',  
               help     = "Transcript Expression File", 
               type     = click.Path(exists = True) , 
               required = True)
@click.option('--sep',  
               help     = "Column Separator: Default is tab", 
               type     = click.STRING ,
               default  = "\t",  
               required = False)
@click.option( '--force',
               is_flag = True,
               help    = 'Set RNA-Seq without prompting user.')
def set(ribo, name, rnaseq, sep, force):
    """
    Store the transcript expression data of a experiment

    RNA-Seq data is given in a text file with two columns where the
    first column has the transcript names and the second column
    has transcript expressions.

    By default the columns are tab separated. 
    The user can change this by providing
    --set argument.

    The experiment name is given in the name parameter.

    \b
    Examples:
    ----------

    1) Store rnaseq data from a zipped tab separated file for experiment WT

    ribog rnaseq set --name WT --rnaseq wt_transcript.tsv.gz test.ribo

    2) Pipe rnaseq data from another process in comma separated form

    cat transcript.csv | ribog rnaseq set --name WT --sep "," test.ribo

    """

    set_rnaseq_wrapper(ribo_file   = ribo, 
                       name        = name, 
                       rnaseq_file = rnaseq, 
                       sep         = sep,
                       force       = force)


@rnaseq.command()
@click.argument('ribo', type = click.Path( ))
@click.option('--name',  
               help     = "experiment name", 
               type     = click.STRING , 
               required = False)
@click.option('--out',  
               help     = "Output File", 
               type     = click.Path() , 
               required = False)
@click.option('--sep',  
               help     = "Column Separator: Default is tab", 
               type     = click.STRING ,
               default  = "\t",  
               required = False)
def get(ribo, name, out, sep):
    """
    Get transcript expression data of a given experiment

    If no output parameter is provided, the results are printed to standard output.

    Transcript expression is reported in two columns 
    where the first column corresponds to transcript names and
    the second column corresponds to transcript expression.

    \b
    Examples
    --------

    Save the transcript expression in a tab separated file in gzipped form.

    1) ribog rnaseq get --name WT --out transcript_exp.tsv.gz test.ribo

    Print the transcript expression on the screen

    2) ribog rnaseq get --name WT test.ribo
    """

    get_rnaseq_wrapper(ribo_file = ribo, 
                       name      = name,
                       output    = out,
                       sep       = sep)



@rnaseq.command()
@click.argument('ribo', type = click.Path( ))
@click.option('--name',  
               help     = "experiment name", 
               type     = click.STRING , 
               required = True)
@click.option( '--force',
               is_flag = True,
               help    = 'Delete RNA-Seq without prompting user.')
def delete(ribo, name, force):
    """
    Delete RNA-Seq data of a particular experiment

    \b
    Example
    -------

    ribog rnaseq delete --name WT test.ribo 
    """

    delete_rnaseq_wrapper(ribo_file = ribo, 
                          name      = name,
                          force     = force)
