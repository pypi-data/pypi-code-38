from .imports import *

def decide_writer(filename, **kw):
    '''
    Decide which animation writer to use, given a desired output filename.

    Parameters
    ----------

    '''
    # figure out the writers to use
    if '.gif' in filename:
        try:
            writer = ani.writers['pillow'](**kw)
        except (RuntimeError, KeyError):
            writer = ani.writers['imagemagick'](**kw)
        except:
            raise RuntimeError('This python seems unable to make an animated gif.')
    else:
        try:
            writer = ani.writers['ffmpeg'](**kw)
        except (RuntimeError,KeyError):
            raise RuntimeError('This computer seems unable to ffmpeg.')
    return writer

def mkdir(path):
    '''
    Make a directory. Don't complain if the directory already exists.

    Parameters
    ----------
    path : str
        The path of the directory to make.
    '''
    try:
        os.mkdir(path)
        print("made {}".format(path))
    except:
        pass
