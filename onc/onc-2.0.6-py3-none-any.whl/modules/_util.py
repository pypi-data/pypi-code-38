import os
import humanize
from datetime import timedelta


def saveAsFile(response, filePath: str, fileName: str, overwrite: bool):
    """
    Saves the file downloaded in the response object, in the outPath, with filename
    If overwrite, will overwrite files with the same name
    """
    # Create outPath directory if not exists
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    
    # Save file in outPath if it doesn't exist yet
    fullPath = filePath + '/' + fileName
    if overwrite or (not os.path.exists(fullPath)):
        try:
            file = open(fullPath, 'wb+')
            file.write(response.content)
            file.close()
            
        except Exception:
            raise
    else:
        raise IOError('Skipping "{:s}": File already exists.'.format(fullPath))


def _formatSize(size: float):
    """
    Returns a formatted file size string representation
    @param size: {float} Size in bytes
    """
    return humanize.naturalsize(size)


def _formatDuration(secs: float):
    """
    Returns a formatted time duration string representation of a duration in seconds
    @param seconds: float
    """
    if secs < 1.0:
        txtDownTime = '{:.3f} seconds'.format(secs)
    else:
        d = timedelta(seconds=secs)
        txtDownTime = humanize.naturaldelta(d)

    return txtDownTime


def _printErrorMessage(response, parameters: dict, showUrl: bool=False, showValue: bool=False):
    """
    Method to print infromation of an error returned by the API to the console
    Builds the error description from the response object 
    """
    if response.status_code == 400:
        if showUrl: print('Error Executing: {:s}'.format(response.url))
        payload = response.json()
        if len(payload) >= 1:
            print("")
            for e in payload['errors']:
                code = e['errorCode']
                msg  = e['errorMessage']
                parm = e['parameter']

                matching = [p for p in parm.split(',') if p in parameters.keys()]
                if len(matching) >= 1:
                    for p in matching:
                        print("  Error {:d}: {:s}. Parameter '{:s}' with value '{:}'".format(code, msg, p, parameters[p]))
                else:
                    print("  '{}' for {}".format(msg, parm))

                if showValue:
                    for p in parm.split(','):
                        parmValue = parameters[p]
                        print("  {} for {} - value: '{}'".format(msg, p, parmValue))
            print("")

    else:
        msg = '\nError {:d} - {:s}\n'.format(response.status_code, response.reason)
        print(msg)